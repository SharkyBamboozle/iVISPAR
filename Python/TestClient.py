import asyncio
import websockets
import json
import base64
from PIL import Image
from ShapePuzzleGenerator import ShapePuzzleGenerator

# Generate a unique client ID for this session
partner_id = ""
network_id = ""
max_game_length = 100  # Max amount of action-perception iterations with the environment
num_game_env = {'ShapePuzzle': 1}  # Number of game environments, how many different tasks have to be solved


board_size = 5 # Size of the game board environment (square)
num_landmarks = 3 # Number of different landmarks for the ShapePuzzle game
instruction_prompt_file_path = r"./instruction_prompts/instruction_prompt_1.txt"


async def client():
    uri = "ws://localhost:1984"  # Replace with your server's URI
    async with websockets.connect(uri,max_size=10000000) as websocket:
        print(f"Connecting to server. Type 'exit' to close the connection.")
        try:
            response = await websocket.recv()
            message_data = json.loads(response)
            if message_data.get("command") == "Handshake":
                network_id = message_data.get("to")
                print(message_data.get("message"))
                isConnected = False
                while not isConnected:
                    partner_id = input("Please enter the remote client id :")
                    message_data = {
                        "command": "Handshake",
                        "from": network_id,
                        "to": partner_id,  # Server ID or specific target ID
                        "message": "Action Perception client attempting to register partner id with the game",
                        "payload": base64.b64encode(b"nothing here").decode("utf-8")
                    }
                    await websocket.send(json.dumps(message_data))
                    print(f"sending handshake")
                    response = await websocket.recv()
                    message_data = json.loads(response)
                    command = message_data.get("command")
                    msg = message_data.get("message")
                    print(f"Received {command} : {msg}")
                    if command == "ACK":
                        partner_id =  message_data.get("from")
                        isConnected = True
            print("Preparing the puzzle...")

            for env_type, num_games in num_game_env.items():
                if env_type == 'ShapePuzzle':
                    # Generate ShapePuzzle configurations
                    with open(instruction_prompt_file_path, 'r', encoding='utf-8') as file:
                        instruction_prompt = file.read()
                    shape_puzzle_generator = ShapePuzzleGenerator(board_size=board_size, num_landmarks=num_landmarks,
                                                                  instruction_prompt=instruction_prompt)
                    setup , configs_path = shape_puzzle_generator.generate_configs(num_configs=num_games)

                    message_data = {
                        "command": "Setup",
                        "from": network_id,
                        "to": partner_id,  # Server ID or specific target ID
                        "message": json.dumps(setup),
                        "payload": base64.b64encode(b"nothing here").decode("utf-8")
                    }
                    await websocket.send(json.dumps(message_data))
                    print(f"sending the setup to the the game...")
                else:
                    print(f"No configuration generator available for environment type: {env_type}")

            response = await websocket.recv()
            message_data = json.loads(response)
            command = message_data.get("command")
            msg = message_data.get("message")
            print(f"Received {command} : {msg}")
            if command == "Screenshot":
                print(message_data.get("message"))
                encoded_data = message_data.get("payload")
                observation = base64.b64decode(encoded_data)
                image = Image.frombytes('RGBA', (1200, 900), observation, 'raw')
                image = image.transpose(Image.FLIP_TOP_BOTTOM)
                image.show()

            #old logic
            user_message = ""
            while user_message != "exit":
                user_message = input("Enter message to send to server: ")

                # Exit the loop if the user wants to close the connection
                if user_message.lower() == "exit":
                    print("Closing connection...")
                    await websocket.close()
                    print("Connection closed")
                    break

                # Create a JSON-formatted message
                message_data = {
                    "command": "UserMessage",
                    "from": network_id,
                    "to": partner_id,  # Server ID or specific target ID
                    "message": user_message,
                    "payload": base64.b64encode(b"Optional binary data").decode("utf-8")
                }

                # Send the JSON message to the server
                await websocket.send(json.dumps(message_data))
                print(f"Sending data")

                # Wait for a response from the server
                response = await asyncio.wait_for(websocket.recv(), 10)
                message_data = json.loads(response)
                text = message_data.get("message")
                print(f"Received from client: {text}")

        except websockets.ConnectionClosed:
            print("Connection with server was closed.")
        except KeyboardInterrupt:
            print("Interrupted by user. Closing connection.")
            await websocket.close()

# Run the client
asyncio.run(client())