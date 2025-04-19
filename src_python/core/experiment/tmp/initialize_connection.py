import websockets
import base64
import time
import json
import logging


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
            #logging.error("Handshake failed: Unexpected response from server.") #TODO reintroduce logging
            raise RuntimeError("Handshake failed: Unexpected response from server.")

        network_id = message_data.get("to")
        logging.info(message_data.get("messages")) #TODO reintroduce logging

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
            logging.info("Sending handshake...") #TODO reintroduce logging
            response = await websocket.recv()
            message_data = json.loads(response)
            command = message_data.get("command")
            logging.info(f"Received {command}: {message_data.get('messages')}") #TODO reintroduce logging
            if command == "ACK":
                isConnected = True

        return websocket, network_id, partner_id
    except Exception as e:
        await websocket.close()
        raise e