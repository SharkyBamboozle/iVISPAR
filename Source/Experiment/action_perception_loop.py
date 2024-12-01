import websockets
import base64
from PIL import Image
import time
import json
import os
import experiment_utilities as util


async def initialize_connection(uri):
    """
    Initialize the WebSocket connection, perform the handshake, and register the partner ID.

    Args:
        uri (str): The WebSocket server URI.

    Returns:
        tuple: A tuple containing the WebSocket connection, network ID, and partner ID.
    """
    websocket = await websockets.connect(uri, max_size=10000000, ping_interval=10, ping_timeout=360)
    try:
        # Perform the handshake
        response = await websocket.recv()
        message_data = json.loads(response)
        if message_data.get("command") != "Handshake":
            raise RuntimeError("Handshake failed: Unexpected response from server.")

        network_id = message_data.get("to")
        print(message_data.get("messages"))

        # Register partner ID
        isConnected = False
        partner_id = None
        while not isConnected:
            partner_id = input("Please enter the remote client id: ")
            message_data = {
                "command": "Handshake",
                "from": network_id,
                "to": partner_id,
                "messages": ["Action Perception client attempting to register partner id with the game"],
                "payload": base64.b64encode(b"nothing here").decode("utf-8"),
            }
            await websocket.send(json.dumps(message_data))
            print("Sending handshake...")
            response = await websocket.recv()
            message_data = json.loads(response)
            command = message_data.get("command")
            print(f"Received {command}: {message_data.get('messages')}")
            if command == "ACK":
                isConnected = True

        return websocket, network_id, partner_id
    except Exception as e:
        await websocket.close()
        raise e


async def interact_with_server(websocket, network_id, partner_id, agent, experiment_path, max_game_length=30):
    """
    Perform repeated interactions with the server after the connection has been established.

    Args:
        websocket: The active WebSocket connection.
        network_id (str): The client network ID.
        partner_id (str): The registered partner ID.
        agent: The agent performing the actions.
        experiment_path (str): The path to save experiment data.
        max_game_length (int): The maximum number of actions to perform.
    """
    # Create the 'obs' subdirectory inside the save path
    obs_dir = os.path.join(experiment_path, 'obs')
    os.makedirs(obs_dir, exist_ok=True)

    msg_dir = os.path.join(experiment_path, 'msg')
    os.makedirs(msg_dir, exist_ok=True)  # Create 'obs' directory if it doesn't exist

    setup_config_file = util.load_single_json_from_directory(experiment_path)
    message_data = {
        "command": "Setup",
        "from": network_id,
        "to": partner_id,
        "messages": [json.dumps(setup_config_file)],
        "payload": base64.b64encode(b"nothing here").decode("utf-8"),
    }
    await websocket.send(json.dumps(message_data))
    print("Sending setup to the game...")

    response = await websocket.recv()
    message_data = json.loads(response)
    command = message_data.get("command")
    msg = message_data.get("messages")
    #print(f"screenshot size is {msg[0]}*{msg[1]}")
    #screenshotWidth = int(msg[0])
    #screenshotHeight = int(msg[1])
    if command == "Screenshot":
        print(message_data.get("messages"))
        encoded_data = message_data.get("payload")
        observation = base64.b64decode(encoded_data)
        image = Image.frombytes('RGBA', (1200, 900), observation, 'raw')
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        filename = os.path.join(obs_dir, f"obs_0_init.png")
        image.save(filename)  # Save the image as a PNG
        print(f"Saved image to {filename}")



    time.sleep(0.2)
    i = 1
    user_message = ""
    while user_message != "done":
        time.sleep(0.2)
        user_message = agent.act(image)

        # Exit the loop if the user wants to close the connection
        if user_message.lower() == "reset":
            message_data = {
                "command": "Reset",
                "from": network_id,
                "to": partner_id,  # Server ID or specific target ID
                "messages": ["reset to main menu"],
                "payload": base64.b64encode(b"Optional binary data").decode("utf-8")
            }
            await websocket.send(json.dumps(message_data))
            print(f"Sending data")
            break
        if user_message.lower() == "exit":
            print("Closing connection...")
            message_data = {
                "command": "Reset",
                "from": network_id,
                "to": partner_id,  # Server ID or specific target ID
                "messages": ["reset to main menu"],
                "payload": base64.b64encode(b"Optional binary data").decode("utf-8")
            }
            await websocket.send(json.dumps(message_data))
            print(f"Sending data")
            await websocket.close()
            print("Connection closed")
            break
        else:
            message_list = [msg.strip() for msg in user_message.split(",")]
            # Create a JSON-formatted message
            # print(message_list)
            message_data = {
                "command": "GameInteraction",
                "from": network_id,
                "to": partner_id,  # Server ID or specific target ID
                "messages": message_list,
                "payload": base64.b64encode(b"Optional binary data").decode("utf-8")
            }

            # Send the JSON message to the server
            await websocket.send(json.dumps(message_data))
            print(f"Sending data")

        # Wait for a response from the server

        # response = await asyncio.wait_for(websocket.recv(), 10)
        response = await websocket.recv()
        message_data = json.loads(response)
        command = message_data.get("command")
        msg = message_data.get("messages")
        # print(f"Received {command} : {msg}")
        if command == "ActionAck":
            # print(message_data.get("messages"))

            encoded_data = message_data.get("payload")
            observation = base64.b64decode(encoded_data)
            image = Image.frombytes('RGBA', (1200, 900), observation, 'raw')
            image = image.transpose(Image.FLIP_TOP_BOTTOM)

            filename = os.path.join(obs_dir, f"obs_{i}_{user_message}.png")
            image.save(filename)  # Save the image as a PNG
            print(f"Saved image to {filename}")

            # Remove the 'payload' entry if it exists
            #message_data.pop('payload', None)

            json_filename = os.path.join(msg_dir, f"msg_{i}.json")
            with open(json_filename, 'w') as json_file:
                json.dump(message_data.get("messages")[0], json_file, indent=4)
            i += 1

        ##TODO save response data to experiment_path