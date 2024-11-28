import asyncio
import websockets
import json
import base64
from PIL import Image

import agent
import util_functions as util
from ShapePuzzleGenerator import ShapePuzzleGenerator
from action_perception_loop import action_perception_loop
from generate_episode_GIF import generate_episode_gif

from WebglServer import run_server_in_background


async def client():
    uri = "ws://localhost:1984"  # Replace with your server's URI
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
            print("Preparing the puzzle...")

            for env_type, num_games in num_game_env.items():
                if env_type == 'ShapePuzzle':
                    # Generate ShapePuzzle configurations
                    with open(instruction_prompt_file_path, 'r', encoding='utf-8') as file:
                        instruction_prompt = file.read()
                    shape_puzzle_generator = ShapePuzzleGenerator(board_size=board_size, num_landmarks=num_landmarks,
                                                                  instruction_prompt=instruction_prompt,
                                                                  experiment_type = experiment_type,
                                                                  grid_label=grid_label,
                                                                  camera_offset = camera_offset,
                                                                  screenshot_alpha = screenshot_alpha)
                    setup , configs_path = shape_puzzle_generator.generate_configs(num_configs=num_games)

                    message_data = {
                        "command": "Setup",
                        "from": network_id,
                        "to": partner_id,  # Server ID or specific target ID
                        "messages": [json.dumps(setup)],
                        "payload": base64.b64encode(b"nothing here").decode("utf-8")
                    }
                    await websocket.send(json.dumps(message_data))
                    print(f"sending the setup to the the game...")
                else:
                    print(f"No configuration generator available for environment type: {env_type}")

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
                image.show()

            #old logic
            user_message = ""
            while user_message != "exit":
                user_message = input("Enter command to send: ")

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
                    print(message_list)
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
                    print(message_data.get("messages"))
                    encoded_data = message_data.get("payload")
                    observation = base64.b64decode(encoded_data)
                    image = Image.frombytes('RGBA', (1200, 900), observation, 'raw')
                    image = image.transpose(Image.FLIP_TOP_BOTTOM)
                    image.show()

        except websockets.ConnectionClosed as e:
            #print("Connection with server was closed.")
            print(f"Connection closed with code {e.code}, reason: {e.reason}")
        except KeyboardInterrupt:
            print("Interrupted by user. Closing connection.")
            await websocket.close()


def run_experiment():



if __name__ == "__main__":
    # Generate a unique client ID for this session
    partner_id = ""
    network_id = ""
    max_game_length = 100  # Max amount of action-perception iterations with the environment
    num_game_env = {'ShapePuzzle': 1}  # Number of game environments, how many different tasks have to be solved
    experiment_type = 'Puzzle'
    #choices are between 'edge', 'cell' , 'both' and 'none'
    grid_label = 'none' #need to add to JSON
    camera_offset = [0,0,0] #need to add to JSON
    screenshot_alpha = 0.0 #need to add to JSON
    instruction_prompt_file_path = r"../../Resources/instruction_prompts/instruction_prompt_1.txt"
    screenshotWidth = 0
    screenshotHeight = 0

    #Legacy params from old main
    single_images = True
    COT = True

    #probably unnecssary Params
    board_size = 5 # Size of the game board environment (square)
    num_landmarks = 7 # Number of different landmarks for the ShapePuzzle game

    #replace this with new one file generation
    json_file_paths, image_file_paths = util.load_config_paths(configs_path)

    # Start the server in the background
    run_server_in_background()

    # Load LLMs and game configs for experiment
    agents = {  # 'UserInteractiveAgent': agent.UserInteractiveAgent(),
        'GPT4Agent': agent.GPT4Agent(single_images=single_images, COT=COT),
        #          'ClaudeAgent': agent.ClaudeAgent(single_images= single_images, COT=COT)
        #          'GeminiAgent': agent.GeminiAgent(single_images= single_images, COT=COT)
    }  # Replace with LLMs here with same API as UserInteractiveAgent

    experiment_paths = util.create_experiment_directories(num_game_env, agents)

    # Run the client
    asyncio.run(client())