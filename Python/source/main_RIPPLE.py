import time

import util_functions as util
from config_generation_ShapePuzzle import generate_ShapePuzzle_configs
from action_perception_loop import action_perception_loop
from generate_episode_GIF import generate_episode_gif


max_game_length = 100  # Max amount of action-perception iterations with the environment
num_game_env = {'ShapePuzzle': 1}  # Number of game environments, how many different tasks have to be solved
board_size = 5 # Size of the game board environment (square)
num_landmarks = 9 # Number of different landmarks for the ShapePuzzle game
unity_executable_path = 'D:\RIPPLE EXEC\RIPPLE.exe'

# Generate configuration files for the game environments specified in num_game_env
for env_type, num_games in num_game_env.items():
    if env_type == 'ShapePuzzle':
        # Generate ShapePuzzle configurations
        configs_path = generate_ShapePuzzle_configs(
            num_configs=num_games,  # Number of games for this environment
            board_size=board_size,
            num_landmarks=num_landmarks
        )
    else:
        print(f"No configuration generator available for environment type: {env_type}")

json_file_paths, image_file_paths = util.load_config_paths(configs_path)

# Load LLMs and game configs for experiment
agents = {'UserInteractiveAgent': util.UserInteractiveAgent()} # Replace with LLMs here with same API as UserInteractiveAgent

experiment_paths = util.create_experiment_directories(num_game_env, agents)

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

            #move config to Unity
            util.copy_json_to_unity_resources(json_file_paths[game_num-1], unity_executable_path)

            try:
                # Start the Unity executable
                process = util.run_Unity_executable(unity_executable_path)
                time.sleep(5)  # Wait for application startup to set up server

                try:
                    # Run the action-perception loop
                    actions, win = action_perception_loop(agent, max_game_length, experiment_path)

                    print(f"number of actions used: {actions}")
                    print(f"game was won: {win}")

                    # Save results to CSV
                    util.save_results_to_csv(experiment_path, actions, win)

                    print(experiment_path)
                    generate_episode_gif(experiment_path)

                except Exception as e:
                    # Handle any errors that occur within the action-perception loop
                    print(f"An error occurred during the action-perception loop: {e}")
                    raise  # Re-raise the exception to propagate it after logging

            finally:
                # Ensure the Unity process is closed even if an error occurs
                util.close_Unity_process(process)


