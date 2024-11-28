import asyncio
import websockets
import json
import base64
import time
from PIL import Image

import agent
import util_functions as util
from ShapePuzzleGenerator import ShapePuzzleGenerator
from Source.main import config_id
from action_perception_loop import action_perception_loop
from generate_episode_GIF import generate_episode_gif
from WebglServer2 import run_WebGL_server_in_background
from Server import run_WebSocket_server_in_background


async def client(setup , configs_path):
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


def expand_config_file(experiment_paths, grid_label, camera_offset, screenshot_alpha):
    """
    Load JSON configs from a list of file paths, add additional values to them,
    and save the updated JSONs back to the same files.

    Parameters:
        experiment_paths (list): List of file paths to JSON configuration files.
        grid_label (str): One of ['edge', 'cell', 'both', 'none'] to add to the JSON.
        camera_offset (list): A list of three numbers [x, y, z] to add to the JSON.
        screenshot_alpha (float): A float value to add to the JSON.
    """
    # Check for valid grid_label
    valid_grid_labels = {'edge', 'cell', 'both', 'none'}
    if grid_label not in valid_grid_labels:
        raise ValueError(f"Invalid grid_label '{grid_label}'. Must be one of {valid_grid_labels}.")

    for path in experiment_paths:
        if not path.endswith('.json'):
            print(f"Skipping non-JSON file: {path}")
            continue

        try:
            # Load the JSON config
            with open(path, 'r') as file:
                config = json.load(file)

            # Add the new values
            config["grid_label"] = grid_label
            config["camera_offset"] = camera_offset
            config["screenshot_alpha"] = screenshot_alpha

            # Save the updated JSON back to the file
            with open(path, 'w') as file:
                json.dump(config, file, indent=4)

            print(f"Updated and saved: {path}")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error processing file {path}: {e}")


def run_experiment(agents, grid_label, camera_offset, screenshot_alpha,
                   max_game_length,instruction_prompt_file_path, num_game_env):


    #replace this with new one file generation
    json_file_paths, image_file_paths = util.load_config_paths_from_ID(config_id)

    experiment_paths = util.create_experiment_directories(num_game_env, agents)

    # Run the server
    print("starting WebSocket Server")
    run_WebSocket_server_in_background()

    # run WebGL Server
    print("starting WebGL Server")
    run_WebGL_server_in_background()

    # Loop over the agents, game environments, and game instances
    for agent_type, agent in agents.items():
        for env_type, num_games in num_game_env.items():
            for game_num in range(1, num_games + 1):
                print(f"Agent: {agent_type}, Environment: {env_type}, Game Instance: {game_num}")

                experiment_path = experiment_paths[agent_type][env_type][game_num]

                # Move the JSON and image files to the experiment path using the new utility function
                util.copy_files_to_experiment(json_file_paths[game_num - 1],
                                              image_file_paths[game_num - 1],
                                              experiment_path)

                expand_config_file(experiment_path, grid_label, camera_offset, screenshot_alpha)

                # move config to Unity
                #util.copy_json_to_unity_resources(json_file_paths[game_num - 1], unity_executable_path)

                try:
                    # Start the Unity executable
                    #process = util.run_Unity_executable(unity_executable_path)
                    time.sleep(7)  # Wait for application startup to set up server

                    try:
                        # Run the action-perception loop
                        #actions, win = action_perception_loop(agent, max_game_length, experiment_path, single_images=single_images)

                        # Run the client
                        print("Start Action-Perception Client")
                        asyncio.run(client(agent, max_game_length, experiment_path, single_images=single_images))


                        #print(f"number of actions used: {actions}")
                        #print(f"game was won: {win}")

                        # Save results to CSV
                        #util.save_results_to_csv(experiment_path, actions, win)

                        print(experiment_path)
                        generate_episode_gif(experiment_path)

                    except Exception as e:
                        # Handle any errors that occur within the action-perception loop
                        print(f"An error occurred during the action-perception loop: {e}")
                        raise  # Re-raise the exception to propagate it after logging

                finally:
                    # Ensure the Unity process is closed even if an error occurs
                    # util.close_Unity_process(process)
                    pass


if __name__ == "__main__":
    # Generate a unique client ID for this session
    partner_id = ""
    network_id = ""

    max_game_length = 100  # Max amount of action-perception iterations with the environment
    num_game_env = {'ShapePuzzle': 1}  # Number of game environments, how many different tasks have to be solved
    #experiment_type = 'Puzzle'
    grid_label = 'none' #choices are between 'edge', 'cell' , 'both' and 'none'
    camera_offset = [0,0,0] #need to add to JSON
    screenshot_alpha = 0.0 #need to add to JSON
    instruction_prompt_file_path = r"../../Resources/instruction_prompts/instruction_prompt_1.txt"
    screenshotWidth = 0
    screenshotHeight = 0

    #Legacy params from old main
    single_images = True
    COT = True

    # Load LLMs and game configs for experiment
    agents = { 'UserInteractiveAgent': agent.UserInteractiveAgent(),
        #'AstarAgent': agent.AstarAgent(),
        #'GPT4Agent': agent.GPT4Agent(single_images=single_images, COT=COT),
        #          'ClaudeAgent': agent.ClaudeAgent(single_images= single_images, COT=COT)
        #          'GeminiAgent': agent.GeminiAgent(single_images= single_images, COT=COT)
    }  # Replace with LLMs here with same API as UserInteractiveAgent

    run_experiment(agents, grid_label, camera_offset, screenshot_alpha, max_game_length,
                   instruction_prompt_file_path, num_game_env)