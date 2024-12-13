"""This main file serves as an example how to run the entire code for an experiment in order."""

import asyncio
import os
import sys

# Dynamically add the parent directories of the source files to the path
subdirs = ['Configuration', 'Experiment', 'Evaluation']
sys.path.extend([os.path.abspath(os.path.join(os.path.dirname(__file__), subdir)) for subdir in subdirs])

import Configuration.configuration_utilities as util
from Configuration.generate_SGP_configs import generate_SGP_configs
from Configuration.visualise_configs_statistics import visualise_config_stats
from Experiment.run_experiment import run_experiment
from Experiment.visualise_episode import visualise_episode_interaction, visualize_state_combination, visualize_state_result
from Evaluation.evaluate_a_star_heuristic import evaluate_a_star_heuristic


####################################################
##########    Generate Configurations     ##########
####################################################

# Load parameters from the JSON file
params = util.load_params_from_json('params_SGP_config_example.json')

# Generate Sliding Geom Puzzle (SGP) configuration files
config_id = generate_SGP_configs(board_size=params.get('board_size', 5),
                                 num_geoms_min_max=params.get('num_geoms_min_max', {"min": 8, "max": 8}),
                                 complexity_min_max=params.get('complexity_min_max', {"c1": {"min": 16, "max": 16},
                                                                                      "c2": {"min": 0, "max": 0}}),
                                 complexity_bin_size=params.get('complexity_bin_size', 1),
                                 shapes=params.get('shapes', ['sphere', 'cylinder', 'cone']),
                                 colors=params.get('colors', ['red', 'green', 'blue']))
print(f"Finished Generate Sliding Geom Puzzle (SGP) configuration files with ID: {config_id}")

# Visualise config stats
visualise_config_stats(config_id)


####################################################
##########         Run Experiment         ##########
####################################################

# Load parameters from the JSON file
params = util.load_params_from_json('params_experiment_example.json')
params['games']['InteractivePuzzle']['params']['config_id'] = config_id

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


####################################################
##########      Evaluate Experiment       ##########
####################################################

# Evaluate the experiment
print(f"Evaluate experiment {experiment_id}")
evaluate_a_star_heuristic(experiment_id)