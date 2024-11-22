import asyncio
import websockets
import uuid
import json
import base64

connected_clients = {}

async def handle_client(websocket, path):

    client_id = str(uuid.uuid4())
    connected_clients[client_id] = websocket
    print(f"Client connected and registered with network id: {client_id}")

    #sending handshake to client

    byte_array = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01'

    # Encode the byte array to Base64
    encoded_byte_array = base64.b64encode(byte_array).decode('utf-8')
    handshake_data = {
        "command" : "Handshake",
        "from" : "0000-0000-0000-0000",
        "to" : client_id,
        "messages" : ["welcome to Microcomsim action perception server V1.0.","your network id is registered"],
        "payload" : encoded_byte_array
    }
    #websocket.send(f"Handshake")
    await websocket.send(json.dumps(handshake_data))
    try:
        # Continuously listen for messages from the client
        #async for message in websocket:
        while True:

            message = await websocket.recv()

            print(message)
            # Parse the incoming message as JSON
            if message != "":
                message_data = json.loads(message)
                #if message_data.get("command") == "ClientClose":
                #    raise websocket.ConnectionClosed
                to_client_id = message_data.get("to")
                from_client_id = message_data.get("from")
                command =  message_data.get("command")
                print(f"Packet from {from_client_id} to {to_client_id}: command {command}")

                if to_client_id in connected_clients:
                    # Route the message to the intended recipient
                    await connected_clients[to_client_id].send(json.dumps(message_data))
                else:
                    # Notify the sender that the target client is not connected
                    error_message = {
                        "command": "Error",
                        "from": "0000-0000-0000-0000",  # Server ID
                        "to": from_client_id,
                        "messages": [f"Target client {to_client_id} is not connected."],
                        "payload": ""
                    }
                    await websocket.send(json.dumps(error_message))
                message = ""

    except json.JSONDecodeError:
        print("Received invalid JSON message")
    except websockets.ConnectionClosed:
        print(f"Client {client_id} disconnected")
    finally:
        print(f"removing connection {client_id}")
        # Remove the client from the connected clients dictionary on disconnection

        del connected_clients[client_id]


async def start_server():
    # Define the host and port for the server
    server = await websockets.serve(handle_client, "localhost", 1984,max_size=10000000,ping_interval=10, ping_timeout=360)  # Replace "localhost" and 8765 if needed

    print("WebSocket server started on ws://localhost:1984")
    #await server.wait_closed()
    await asyncio.Future()


# Run the server
asyncio.run(start_server())