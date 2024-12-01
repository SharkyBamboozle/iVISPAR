import asyncio
import os
from logging import raiseExceptions
from datetime import datetime

import agent_systems
import experiment_utilities as util
from visualise_episode import visualise_episode_interaction, visualize_state_combination, parse_messages
from web_and_socketserver import run_socketserver_in_background, run_WebSocket_server_in_background
from action_perception_loop import initialize_connection, interact_with_server as action_perception_loop




async def run_experiment(config_id, agents, grid_label, camera_offset, camera_auto_override, screenshot_alpha, max_game_length, num_game_env):
    #replace this with new one file generation
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    config_dir = os.path.join(base_dir, 'Data', 'Configs', config_id)

    # Load all config files from config_ID collection
    json_file_paths = []
    for file_name in os.listdir(config_dir):
        # Check if the file has a .json extension
        if file_name.endswith(".json"):
            # Construct the full file path for the JSON file
            json_full_path = os.path.join(config_dir, file_name)
            json_file_paths.append(json_full_path)

    #json_file_paths = json_file_paths[:2]

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


    # Loop over the agents, game environments, and game instances
    for json_file_path in json_file_paths:
        for agent_type, agent_class in agents.items():
            for env_type, num_games in num_game_env.items():
                for game_num in range(1, num_games + 1):

                    # Construct the subdirectory name
                    json_base_name = os.path.splitext(os.path.basename(json_file_path))[0]
                    experiment_path = f"experiment_{agent_type}_{env_type}_{json_base_name}_Nr{game_num}"
                    experiment_path = os.path.join(experiment_dir, experiment_path)
                    os.makedirs(experiment_path, exist_ok=True)

                    print(f"Agent: {agent_type}, Environment: {env_type}, Game Instance: {game_num}")

                    # Move the JSON and image files to the experiment path using the new utility function
                    util.copy_json_to_experiment(json_file_path, experiment_path)
                    config = util.expand_config_file(experiment_path, grid_label, camera_offset, camera_auto_override, screenshot_alpha)

                    if agent_type == 'AStarAgent':
                        agent = agent_class(config.get("shortest_move_sequence", []))
                    elif agent_type == 'UserAgent':
                        agent = agent_class()
                    elif (agent_type == 'GPT4Agent' or
                          agent_type == 'ClaudeAgent' or
                          agent_type == 'GeminiAgent'):
                        agent = agent_class(single_images, COT)
                    else:
                        raise ValueError(f"Unsupported agent_type: {agent_type}")

                    try:
                        # Run the client
                        print("Start Action-Perception Client")
                        await action_perception_loop(websocket, network_id, partner_id, agent, experiment_path, max_game_length)

                        # Save results to CSV
                        #util.save_results_to_csv(experiment_path, actions, win)

                    except Exception as e:
                        # Handle any errors that occur within the action-perception loop
                        print(f"An error occurred during the action-perception loop: {e}")
                        raise  # Re-raise the exception to propagate it after logging

    await websocket.close()

    return experiment_id


if __name__ == "__main__":
    # Parameters
    config_id = "SGP_ID_20241201_111256"
    max_game_length = 100  # Max amount of action-perception iterations with the environment
    num_game_env = {'SlidingGeomPuzzle': 1}  #This param will now come from config_id
    grid_label = 'both' #choices are between 'edge', 'cell' , 'both' and 'none'
    camera_offset = [0,5.57,-3.68] #need to add to JSON
    camera_auto_override = [6.8,-1,6.8]
    screenshot_alpha = 1.0 #need to add to JSON
    instruction_prompt_file_path = r"../../Resources/instruction_prompts/instruction_prompt_1.txt"
    screenshotWidth = 0
    screenshotHeight = 0
    single_images = True
    COT = True

    # Load LLMs and game configs for experiment
    agents = {
        #'UserAgent': agent_systems.UserAgent,
        'AStarAgent': agent_systems.AStarAgent,
        # 'GPT4Agent': agent_systems.GPT4Agent,
        # 'ClaudeAgent': agent_systems.ClaudeAgent,
        # 'GeminiAgent': agent_systems.GeminiAgent,
    }

    experiment_id = asyncio.run(run_experiment(config_id, agents, grid_label, camera_offset, camera_auto_override, screenshot_alpha, max_game_length, num_game_env))
    print(f"Finished running experiments for all Sliding Geom Puzzle (SGP) configuration files for experiment ID: {experiment_id}")


    #Visualize episode and state combination
    visualise_episode_interaction(experiment_id)
    visualize_state_combination(experiment_id)
    parse_messages(experiment_id)
