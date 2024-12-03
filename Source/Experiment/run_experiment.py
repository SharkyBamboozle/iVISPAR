import asyncio
import os
from logging import raiseExceptions
from datetime import datetime

import agent_systems
import game_systems
import experiment_utilities as util
from visualise_episode import visualise_episode_interaction, visualize_state_combination
from web_and_socketserver import run_socketserver_in_background, run_WebSocket_server_in_background
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
    run_socketserver_in_background()

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
            config_file_paths = json_file_paths[:num_game_env]

            for config_file_path in config_file_paths:

                # Construct the subdirectory name
                json_base_name = os.path.splitext(os.path.basename(config_file_path))[0]
                experiment_path = f"experiment_{agent_type}_{game_type}_{json_base_name}"
                experiment_path = os.path.join(experiment_dir, experiment_path)
                os.makedirs(experiment_path, exist_ok=True)

                # Move the JSON and image files to the experiment path using the new utility function
                util.copy_json_to_experiment(config_file_path, experiment_path)
                config = util.expand_config_file(experiment_path,
                                                 sim_param.get('grid_label', None),
                                                 sim_param.get('camera_offset', None),
                                                 sim_param.get('camera_auto_override', None),
                                                 sim_param.get('screenshot_alpha', None))

                # Initialise agent
                agent_class = agent_details.get('class', None)
                if agent_type == 'AStarAgent':
                    agent = agent_class(config.get("shortest_move_sequence", []))
                elif agent_type == 'UserAgent':
                    agent = agent_class()
                elif (agent_type == 'GPT4Agent' or
                      agent_type == 'ClaudeAgent' or
                      agent_type == 'GeminiAgent'):
                    agent_parameters = agent_details.get('params', {})
                    agent = agent_class(single_images=agent_parameters.get('single_images', None),
                                        COT=agent_parameters.get('COT', None))
                else:
                    raise ValueError(f"Unsupported agent_type: {agent_type}")

                # Initialise game
                game_class = game_details.get('class', None)
                if game_type == 'InteractivePuzzle':
                    game = game_class(
                        experiment_path,
                        game_params.get("representation_type", None),
                        game_params.get("planning_steps", None),
                        game_params.get('max_game_length', None)
                    )

                try:
                    # Run the client
                    print(f"Start Game with Agent: {agent_type}, Game: {game_type}, Config: {config.get('config_instance_id', [])}")
                    await action_perception_loop(websocket, network_id, partner_id, agent, game, experiment_path)

                except Exception as e:
                    # Handle any errors that occur within the action-perception loop
                    print(f"An error occurred during the action-perception loop: {e}")
                    raise  # Re-raise the exception to propagate it after logging

    await websocket.close()

    return experiment_id


if __name__ == "__main__":

    # Agent parameter
    agents = {
        'UserAgent': agent_systems.UserAgent,
        'AStarAgent': {
            'class': agent_systems.AStarAgent
        },
        'GPT4Agent': {
            'class': agent_systems.GPT4Agent,
            'params': {
                'instruction_prompt_file_path': r"../../Resources/instruction_prompts/instruction_prompt_1.txt",
                'single_images': True,
                'COT': True,
            }
        },
        'ClaudeAgent': {
            'class': agent_systems.ClaudeAgent
        },
        'GeminiAgent': {
            'class': agent_systems.GeminiAgent
        },
    }

    # Game parameter
    games = {
        'InteractivePuzzle': {
            'class': game_systems.InteractivePuzzle,
            'params': {
                'config_id': "SGP_ID_20241202_155231",
                'num_game_env': 1000,  # Max amount of games to play (set to high value to play all configs)
                'max_game_length': 30,  # Max amount of action-perception iterations with the environment
                'representation_type': 'vision', #'text' 'both'
                'planning_steps': 1,
            }
        },
        'SceneUnderstanding': {
            'class': game_systems.SceneUnderstanding,
        }
    }

    # Simulation parameter
    sim_param = {
        'grid_label': 'both', #choices are between 'edge', 'cell' , 'both' and 'none'
        'camera_offset': [0,5.57,-3.68], #need to add to JSON
        'camera_auto_override': [6.8,-1,6.8],
        'screenshot_alpha': 1.0, #need to add to JSON
    }

    # Run the experiment
    experiment_id = asyncio.run(run_experiment(
        games={'InteractivePuzzle': games['InteractivePuzzle']},
        agents={'AStarAgent': agents['AStarAgent']},
        sim_param=sim_param)
    )
    print(f"Finished running experiments for experiment ID: {experiment_id}")

    # Visualize episode and state combination
    visualise_episode_interaction(experiment_id)
    visualize_state_combination(experiment_id)
