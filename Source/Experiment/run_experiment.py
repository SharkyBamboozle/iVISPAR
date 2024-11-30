import asyncio
from logging import raiseExceptions

import agent_systems
import experiment_utilities as util
from expand_json_with_additonal_param import expand_config_file
from visualise_episode import visualise_episode_interaction, visualize_state_combination
from webglserver import run_WebGL_server_in_background
from server import run_WebSocket_server_in_background
from action_perception_loop import client as action_perception_loop


def run_experiment(config_id, agents, grid_label, camera_offset, screenshot_alpha,
                   max_game_length, num_game_env):


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
    for agent_type, agent_class in agents.items():
        for env_type, num_games in num_game_env.items():
            for game_num in range(1, num_games + 1):

                print(f"Agent: {agent_type}, Environment: {env_type}, Game Instance: {game_num}")

                experiment_path = experiment_paths[agent_type][env_type][game_num]

                # Move the JSON and image files to the experiment path using the new utility function
                util.copy_json_to_experiment(json_file_paths[game_num - 1], experiment_path)
                config = expand_config_file(experiment_path, grid_label, camera_offset, screenshot_alpha)
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
                    asyncio.run(action_perception_loop(agent, max_game_length, experiment_path))

                    # Save results to CSV
                    #util.save_results_to_csv(experiment_path, actions, win)

                except Exception as e:
                    # Handle any errors that occur within the action-perception loop
                    print(f"An error occurred during the action-perception loop: {e}")
                    raise  # Re-raise the exception to propagate it after logging


    return experiment_paths #TODO change to ID


if __name__ == "__main__":
    # Parameters
    config_id = "SGP_ID_20241130_145237"
    max_game_length = 100  # Max amount of action-perception iterations with the environment
    num_game_env = {'SlidingGeomPuzzle': 1}  #This param will now come from config_id
    grid_label = 'both' #choices are between 'edge', 'cell' , 'both' and 'none'
    camera_offset = [0,0,0] #need to add to JSON
    screenshot_alpha = 1.0 #need to add to JSON
    instruction_prompt_file_path = r"../../Resources/instruction_prompts/instruction_prompt_1.txt"
    screenshotWidth = 0
    screenshotHeight = 0
    single_images = True
    COT = True

    # Load LLMs and game configs for experiment
    agents = {
        #'UserAgent': agent_systems.UserInteractiveAgent,
        'AStarAgent': agent_systems.AStarAgent,
        # 'GPT4Agent': agent_systems.GPT4Agent,
        # 'ClaudeAgent': agent_systems.ClaudeAgent,
        # 'GeminiAgent': agent_systems.GeminiAgent,
    }

    experiment_id = run_experiment(config_id, agents, grid_label, camera_offset, screenshot_alpha, max_game_length, num_game_env)

    #Visualize episode and state combination
    visualise_episode_interaction(experiment_id)
    visualize_state_combination(experiment_id)