import websockets
import base64
from PIL import Image
import json
import agent_systems
import os
from load_JSON_from_experiment_dir import load_single_json_from_directory

async def client(agent, max_game_length, experiment_path):

    uri = "ws://localhost:1984"  # Replace with your server's URI

    # Create the 'obs' subdirectory inside the save path
    obs_dir = os.path.join(experiment_path, 'obs')
    os.makedirs(obs_dir, exist_ok=True)  # Create 'obs' directory if it doesn't exist

    async with websockets.connect(uri,max_size=10000000,ping_interval=10, ping_timeout=360) as websocket:
        print(f"Connecting to server. Type 'exit' to close the connection.")
        try:
            response = await websocket.recv()
            message_data = json.loads(response)
            if message_data.get("command") == "Handshake":
                network_id = message_data.get("to")
                print(message_data.get("messages"))
                isConnected = False
                while not isConnected:
                    partner_id = input("Please enter the remote client id :")
                    message_data = {
                        "command": "Handshake",
                        "from": network_id,
                        "to": partner_id,  # Server ID or specific target ID
                        "messages": ["Action Perception client attempting to register partner id with the game"],
                        "payload": base64.b64encode(b"nothing here").decode("utf-8")
                    }
                    await websocket.send(json.dumps(message_data))
                    print(f"sending handshake")
                    response = await websocket.recv()
                    message_data = json.loads(response)
                    command = message_data.get("command")
                    msg = message_data.get("messages")
                    print(f"Received {command} : {msg}")
                    if command == "ACK":
                        partner_id =  message_data.get("from")
                        isConnected = True

            setup_config_file = load_single_json_from_directory(experiment_path)
            message_data = {
                "command": "Setup",
                "from": network_id,
                "to": partner_id,  # Server ID or specific target ID
                "messages": [json.dumps(setup_config_file)],
                "payload": base64.b64encode(b"nothing here").decode("utf-8")
            }
            await websocket.send(json.dumps(message_data))
            print(f"sending the setup to the the game...")

            response = await websocket.recv()
            message_data = json.loads(response)
            command = message_data.get("command")
            msg = message_data.get("messages")
            print(f"screenshot size is {msg[0]}*{msg[1]}")
            screenshotWidth = int(msg[0])
            screenshotHeight = int(msg[1])
            if command == "Screenshot":
                print(message_data.get("messages"))
                encoded_data = message_data.get("payload")
                observation = base64.b64decode(encoded_data)
                image = Image.frombytes('RGBA', (screenshotWidth, screenshotHeight), observation, 'raw')
                image = image.transpose(Image.FLIP_TOP_BOTTOM)

                filename = os.path.join(obs_dir, f"obs_1_init.png")
                image.save(filename)  # Save the image as a PNG
                print(f"Saved image to {filename}")


            ##TODO add agent here


            i = 2
            user_message = ""
            while user_message != "exit":

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
                    #print(message_list)
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

                #response = await asyncio.wait_for(websocket.recv(), 10)
                response = await websocket.recv()
                message_data = json.loads(response)
                command = message_data.get("command")
                msg = message_data.get("messages")
                #print(f"Received {command} : {msg}")
                if command == "ActionAck":

                    #print(message_data.get("messages"))
                    msg_dir = os.path.join(experiment_path, 'msg')
                    os.makedirs(msg_dir, exist_ok=True)  # Create 'obs' directory if it doesn't exist
                    json_filename = os.path.join(msg_dir, f"msg_{i}.json")
                    with open(json_filename, 'w') as json_file:
                        json.dump(message_data, json_file, indent=4)


                    encoded_data = message_data.get("payload")
                    observation = base64.b64decode(encoded_data)
                    image = Image.frombytes('RGBA', (1200, 900), observation, 'raw')
                    image = image.transpose(Image.FLIP_TOP_BOTTOM)
                    #image.show()

                    filename = os.path.join(obs_dir, f"obs_{i}_{user_message}.png")
                    image.save(filename)  # Save the image as a PNG
                    print(f"Saved image to {filename}")
                    i  +=1

                ##TODO save response data to experiment_path

        except websockets.ConnectionClosed as e:
            #print("Connection with server was closed.")
            print(f"Connection closed with code {e.code}, reason: {e.reason}")
        except KeyboardInterrupt:
            print("Interrupted by user. Closing connection.")
            await websocket.close()
