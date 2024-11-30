"""This main file serves as an example how to run the entire code for an experiment in order. However, due to the time
demand of the configurations and experiments it is not recommended to run the entire code from here. It is recommended
to rather run the code in individual sections, first generating a configuration set (or using one of the ready-made ones
in the Data/Configs dir) then running the experiment and later evaluating it."""

from Configuration.generate_sgp_configs import generate_sgp_configs
from Configuration.generate_sut_configs import generate_sut_configs
from Configuration.visualise_configs_statistics import visualise_config_stats
from Configuration.retrieve_config_visualisations import retrieve_config_visualisations
from Experiment import agent_systems
from Experiment.run_experiment import run_experiment
from Experiment.visualise_episode import visualise_episode_interaction, visualize_state_combination
from Evaluation.evaluate_results_main import evaluate


####################################################
##########    Generate configurations     ##########
####################################################

# Parameters
experiment_types = {
    "SGP": "SlidingGeomPuzzle",
    "SUT": "SceneUnderstandingTask"
}
experiment_type = experiment_types['SGP']
board_size = 5
num_geoms = 5
complexity_min_max = {"c1": {"min": 10, "max": 15},  # smallest and highest c1 complexity to be considered
                      "c2": {"min": 0, "max": 1}}  # smallest and highest c2 complexity to be considered
complexity_bin_size = 2  # amount of puzzle configs per complexity bin
shapes = ['cube', 'sphere', 'pyramid']  # , 'cylinder', 'cone', 'prism']
colors = ['red', 'green', 'blue']  # , 'yellow', 'purple', 'orange']

# Generate Sliding Geom Puzzle (SGP) configuration files
if experiment_type == "SlidingGeomPuzzle":
    config_id = generate_sgp_configs(board_size, num_geoms, complexity_min_max, complexity_bin_size, shapes, colors)
    print(f"Finished Generate Sliding Geom Puzzle (SGP) configuration files with ID: {config_id}")

# Generate Scene Understanding Task (SUT) configuration files
elif experiment_type == "SceneUnderstandingTask":
    num_geoms_min_max = {"min": 1, "max": 9}
    config_id = generate_sut_configs(board_size, num_geoms_min_max, complexity_bin_size, shapes, colors)
    print(f"Finished Generate Scene Understanding Task (SUT) configuration files with ID: {config_id}")

# Visualise config stats
visualise_config_stats(config_id)


####################################################
##########         Run experiment         ##########
####################################################

# Parameters
max_game_length = 100  # Max amount of action-perception iterations with the environment
num_game_env = {'SlidingGeomPuzzle': 1}  # This param will now come from config_id
grid_label = 'both'  # choices are between 'edge', 'cell' , 'both' and 'none'
camera_offset = [0, 0, 0]  # need to add to JSON
screenshot_alpha = 0.0  # need to add to JSON
instruction_prompt_file_path = r"../../Resources/instruction_prompts/instruction_prompt_1.txt"
screenshotWidth = 0
screenshotHeight = 0
single_images = True
COT = True

# Load LLMs and game configs for experiment
agents = {
    # 'UserAgent': agent_systems.UserInteractiveAgent,
    'AStarAgent': agent_systems.AStarAgent,
    # 'GPT4Agent': agent_systems.GPT4Agent,
    # 'ClaudeAgent': agent_systems.ClaudeAgent,
    # 'GeminiAgent': agent_systems.GeminiAgent,
}

experiment_id = run_experiment(config_id, agents, grid_label, camera_offset, screenshot_alpha, max_game_length,
                                num_game_env)

# Visualize episode and state combination
visualise_episode_interaction(experiment_id)
visualize_state_combination(experiment_id)
retrieve_config_visualisations(config_id, experiment_id)


####################################################
##########      Evaluate experiment       ##########
####################################################

# Evaluate the experiment
evaluate(experiment_ids)