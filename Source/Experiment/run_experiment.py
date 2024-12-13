import asyncio
import os
from logging import raiseExceptions
from datetime import datetime
import json
import base64

import agent_systems
import game_systems
import experiment_utilities as util
from visualise_episode import visualise_episode_interaction, visualize_state_combination, visualize_state_result
from webgl_socket_server import run_socketserver_in_background
from web_server import run_WebSocket_server_in_background
from action_perception_loop import initialize_connection, interact_with_server as action_perception_loop


async def run_experiment(games, agents, sim_param):

    # Set up experiment ID and directory
    experiment_id = datetime.now().strftime("experiment_ID_%Y%m%d_%H%M%S")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    experiment_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id)
    os.makedirs(experiment_dir, exist_ok=True)

    # Run the server
    print("starting WebSocket Server")
    run_WebSocket_server_in_background()

    # run WebGL Server
    print("starting WebGL Server")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    webApp_dir = os.path.join(base_dir, 'iVISPAR')
    run_socketserver_in_background(webApp_dir)

    uri = "ws://localhost:1984"
    websocket, network_id, partner_id = await initialize_connection(uri)

    # Loop over agents, games and game configurations
    for agent_type, agent_details in agents.items():
        for game_type, game_details in games.items():

            game_params = game_details.get('params', None)
            num_game_env = game_params.get('num_game_env', None)

            # replace this with new one file generation
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            config_dir = os.path.join(base_dir, 'Data', 'Configs', game_params.get('config_id', None))

            # Load all config files from config_ID collection
            json_file_paths = []
            for file_name in os.listdir(config_dir):
                # Check if the file has a .json extension
                if file_name.endswith(".json"):
                    # Construct the full file path for the JSON file
                    json_full_path = os.path.join(config_dir, file_name)
                    json_file_paths.append(json_full_path)

            # Validate parameters
            if num_game_env > len(json_file_paths):
                print(f"Number of game environments exceeds the number of config files in the dataset, setting num_game_env to {len(json_file_paths)}.")
                num_game_env = len(json_file_paths)
            config_file_paths = json_file_paths[:num_game_env] #TODO reverse

            for config_file_path in config_file_paths: #TODO reverse

                # Construct the subdirectory name
                json_base_name = os.path.splitext(os.path.basename(config_file_path))[0]
                episode_name = f"episode_{agent_type}_{game_type}_{json_base_name}"
                episode_path = os.path.join(experiment_dir, episode_name)
                os.makedirs(episode_path, exist_ok=True)

                # Move the JSON and image files to the experiment path using the new utility function
                util.copy_json_to_experiment(config_file_path, episode_path)
                config = util.expand_config_file(
                    experiment_path=episode_path,
                    grid_label=sim_param.get('grid_label', None),
                    camera_offset=sim_param.get('camera_offset', None),
                    camera_auto_override=sim_param.get('camera_auto_override', None),
                    screenshot_alpha=sim_param.get('screenshot_alpha', None)
                )

                # Initialise agent
                agent_class = agent_details.get('class', None)
                if agent_type == 'AIAgent':
                    agent_parameters = agent_details.get('params', {})
                    move_set = agent_parameters.get('move_set', None)
                    agent = agent_systems.AIAgent(config.get(move_set, []))
                elif agent_type == 'UserAgent':
                    agent = agent_systems.UserAgent()
                elif (agent_type == 'GPT4Agent' or
                      agent_type == 'ClaudeAgent' or
                      agent_type == 'GeminiAgent'):
                    agent_parameters = agent_details.get('params', {})
                    agent = agent_class(
                        api_key_file_path=agent_parameters.get('api_keys_file_path', None),
                        instruction_prompt_file_path=agent_parameters.get('instruction_prompt_file_path', None),
                        single_images=agent_parameters.get('single_images', True),
                        COT=agent_parameters.get('COT', False),
                    )
                else:
                    raise ValueError(f"Unsupported agent_type: {agent_type}")

                # Initialise game
                game_class = game_details.get('class', None)
                if game_type == 'InteractivePuzzle':
                    game = game_systems.InteractivePuzzle(
                        experiment_id=episode_path,
                        instruction_prompt_file_path=game_params.get("instruction_prompt_file_path", None),
                        chain_of_thoughts = game_params.get("chain_of_thoughts", None),
                        representation_type = game_params.get("representation_type", None),
                        planning_steps=game_params.get("planning_steps", None),
                        max_game_length=game_params.get('max_game_length', None),
                        predict_board_state=game_params.get('predict_board_state', False),
                    )
                if game_type == 'SceneUnderstanding':
                    game = game_class(
                        experiment_id=episode_path,
                        instruction_prompt_file_path=game_params.get("instruction_prompt_file_path", None),
                        chain_of_thoughts=game_params.get("chain_of_thoughts", None),
                    )

                try:

                    # Set up environment
                    setup_config_file = util.load_single_json_from_directory(episode_path)
                    message_data = {
                        "command": "Setup",
                        "from": network_id,
                        "to": partner_id,
                        "messages": [json.dumps(setup_config_file)],
                        "payload": base64.b64encode(b"nothing here").decode("utf-8"),
                    }
                    await websocket.send(json.dumps(message_data))



                    # Run the client
                    print(f"Start Game with Agent: {agent_type}, Game: {game_type}, Config: {config.get('config_instance_id', [])}")
                    await action_perception_loop(websocket, network_id, partner_id, agent, game)

                except Exception as e:
                    # Handle any errors that occur within the action-perception loop
                    print(f"An error occurred during the action-perception loop: {e}")
                    raise  # Re-raise the exception to propagate it after logging

    await websocket.close()

    return experiment_id


if __name__ == "__main__":
    # Load parameters from the JSON file
    params = util.load_params_from_json('params_experiment_example.json')

    # Run the experiment
    experiment_id = asyncio.run(run_experiment(
        games=params.get('games', {}),
        agents=params.get('agents', {}),
        sim_param=params.get('sim_param', {}))
    )
    print(f"Finished running experiments for experiment ID: {experiment_id}")

    # Visualize episode and state combination
    visualise_episode_interaction(experiment_id)
    visualize_state_combination(experiment_id)
    visualize_state_result(experiment_id)
    print(f"Finished visualizing experiments for experiment ID: {experiment_id}")
