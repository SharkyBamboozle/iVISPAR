"""This main file serves as an example how to run the entire code for an experiment in order. However, due to the time
demand of the configurations and experiments it is not recommended to run the entire code from here. It is recommended
to rather run the code in individual sections, first generating a configuration set (or using one of the ready-made ones
in the Data/Configs dir) then running the experiment and later evaluating it."""

import asyncio
import os
import sys

# Dynamically add the parent directories of the source files to the path
subdirs = ['Configuration', 'Experiment', 'Evaluation']
sys.path.extend([os.path.abspath(os.path.join(os.path.dirname(__file__), subdir)) for subdir in subdirs])

from Configuration.generate_configs import generate_configs
from Configuration.visualise_configs_statistics import visualise_config_stats
from Configuration.retrieve_config_visualisations import retrieve_config_visualisations
from Experiment import agent_systems
from Experiment import game_systems
from Experiment.run_experiment import run_experiment
from Experiment.visualise_episode import visualise_episode_interaction, visualize_state_combination
from Evaluation.evaluate_results import evaluate
from Evaluation.plot_results import plot_results


####################################################
##########    Generate configurations     ##########
####################################################

# Parameters
board_size = 4
num_geoms_min_max = {"min": 4, "max": 6}
complexity_min_max = {"c1": {"min": 10, "max": 11},  # smallest and highest c1 complexity to be considered
                      "c2": {"min": 0, "max": 0}}  # smallest and highest c2 complexity to be considered
complexity_bin_size = 1  # amount of puzzle configs per complexity bin
shapes = ['cube', 'sphere', 'pyramid']  # , 'cylinder', 'cone', 'prism']
colors = ['red', 'green', 'blue']  # , 'yellow', 'purple', 'orange']

# Generate Sliding Geom Puzzle (SGP) configuration files
config_id = generate_configs(board_size, num_geoms_min_max, complexity_min_max, complexity_bin_size, shapes, colors)
print(f"Finished Generate Sliding Geom Puzzle (SGP) configuration files with ID: {config_id}")

# Visualise config stats
visualise_config_stats(config_id)


####################################################
##########         Run experiment         ##########
####################################################

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
        'class': agent_systems.ClaudeAgent,
        'params': {
            'instruction_prompt_file_path': r"../../Resources/instruction_prompts/instruction_prompt_1.txt",
            'single_images': True,
            'COT': True,
        }
    },
    'GeminiAgent': {
        'class': agent_systems.GeminiAgent,
        'params': {
            'instruction_prompt_file_path': r"../../Resources/instruction_prompts/instruction_prompt_1.txt",
            'single_images': True,
            'COT': True,
        }
    },
}

# Game parameter
games = {
    'InteractivePuzzle': {
        'class': game_systems.InteractivePuzzle,
        'params': {
            'config_id': config_id,
            'num_game_env': 2,  # Max amount of games to play (set to high value to play all configs)
            'max_game_length': 30,  # Max amount of action-perception iterations with the environment
            'representation_type': 'vision',  # 'text' 'both'
            'planning_steps': 1,
        }
    },
    'SceneUnderstanding': {
        'class': game_systems.SceneUnderstanding,
        'params': {
            'config_id': config_id,
        }
    }
}

# Simulation parameter
sim_param = {
    'grid_label': 'both',  # choices are between 'edge', 'cell' , 'both' and 'none'
    'camera_offset': [0, 5.57, -3.68],  # need to add to JSON
    'camera_auto_override': [6.8, -1, 6.8],
    'screenshot_alpha': 1.0,  # need to add to JSON
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

retrieve_config_visualisations(config_id, experiment_id)

####################################################
##########      Evaluate experiment       ##########
####################################################

# Evaluate the experiment
print(f"Evaluate experiment {experiment_id}")
evaluate(experiment_id)
plot_results(experiment_id)