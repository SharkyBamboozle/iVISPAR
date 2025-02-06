import websockets
import base64
import time
import json
import logging
import experiment_utilities as util

from experiment_logging import log_separator

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
            logging.error("Handshake failed: Unexpected response from server.")
            raise RuntimeError("Handshake failed: Unexpected response from server.")

        network_id = message_data.get("to")
        logging.info(message_data.get("messages"))

        # Register partner ID
        isConnected = False
        partner_id = None
        while not isConnected:
            partner_id = input("Please enter the remote client id: ")
            print()  # This ensures the cursor moves to a new line
            message_data = {
                "command": "Handshake",
                "from": network_id,
                "to": partner_id,
                "messages": ["Action Perception client attempting to register partner id with the game"],
                "payload": base64.b64encode(b"nothing here").decode("utf-8"),
            }
            await websocket.send(json.dumps(message_data))
            logging.info("Sending handshake...")
            response = await websocket.recv()
            message_data = json.loads(response)
            command = message_data.get("command")
            logging.info(f"Received {command}: {message_data.get('messages')}")
            if command == "ACK":
                isConnected = True

        return websocket, network_id, partner_id
    except Exception as e:
        await websocket.close()
        raise e


async def interact_with_server(websocket, network_id, partner_id, agent, game, episode_logger):
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
    response = await websocket.recv()
    message_data = json.loads(response)
    delay = agent.delay

    i = 0
    while not game.check_done(message_data):
        log_separator(f"Action-Perception Loop: {i}", logger=episode_logger)
        time.sleep(delay)
        if message_data.get("command") == "Screenshot" or message_data.get("command") == "ActionAck":
            observation = game.feed_sim_response(message_data, i)
            user_message = agent.act(observation, i)
            game.feed_agent_response(user_message)

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
            break
        if user_message.lower() == "exit":
            episode_logger.info("Closing connection...")
            message_data = {
                "command": "Reset",
                "from": network_id,
                "to": partner_id,  # Server ID or specific target ID
                "messages": ["reset to main menu"],
                "payload": base64.b64encode(b"Optional binary data").decode("utf-8")
            }
            await websocket.send(json.dumps(message_data))
            await websocket.close()
            episode_logger.info("Connection closed")
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
            await websocket.send(json.dumps(message_data))
            response = await websocket.recv()
            message_data = json.loads(response)

        i += 1
        game._save_logs()

    #save last observation after game is done
    observation = game.feed_sim_response(message_data, i)
    game._save_logs()

    # Send the JSON message to the server
    #response = await websocket.recv()
    message_data = {
        "command": "Reset",
        "from": network_id,
        "to": partner_id,  # Server ID or specific target ID
        "messages": ["reset to main menu"],
        "payload": base64.b64encode(b"Optional binary data").decode("utf-8")
    }
    await websocket.send(json.dumps(message_data))
    #image = game.feed_sim_response(message_data, 100)
    #game._save_logs()

    ##TODO save response data to experiment_path