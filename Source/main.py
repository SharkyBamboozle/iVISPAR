"""This main file serves as an example how to run the entire code for an experiment in order."""

import asyncio
import os
import sys

# Dynamically add the parent directories of the source files to the path
subdirs = ['Configuration', 'Experiment', 'Evaluation', 'Visualization', 'Plot']
sys.path.extend([os.path.abspath(os.path.join(os.path.dirname(__file__), subdir)) for subdir in subdirs])

# Configure
import Configure.configuration_utilities as util
from Configure.generate_SGP_configs import generate_SGP_configs
from Source.Plot.visualise_configs_statistics import visualise_config_stats

# Experiment
from Experiment.run_experiment import run_experiment

# Visualize
from Visualize.visualize_episode_states import visualize_full_state_progression
from Visualize.visualise_episode_interaction import visualise_episode_interaction

# Evaluate
from Evaluate.evaluate_episodes_sgp import evaluate_episodes
from Evaluate.compile_experiment_steps_evaluation import compile_experiment_evaluation
from Evaluate.compile_experiment_wins_evaluation import compile_episode_evaluation
from Evaluate.compile_experiment_statistics import compile_experiment_statistics

# Plot
from Plot.plot_episodes_progress_lineplot import plot_episode_evaluate_a_star_heuristic
from Plot.plot_lineplot import plot_csv_with_confidence_interval
from Plot.plot_heatmap import plot_heat_map_episode_level_average
from Plot.plot_barplot_old import plot_bar_plot_with_baselines

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
params = util.load_params_from_json('params_experiment_test_auto_done.json')
params['games']['InteractivePuzzle']['params']['config_id'] = config_id

# Run the experiment
experiment_id = asyncio.run(run_experiment(
    games=params.get('games', {}),
    agents=params.get('agents', {}),
    envs=params.get('envs', {}),
    experiment_id='Test_Auto_Done')
)
print(f"Finished running experiments for experiment ID: {experiment_id}")

# Visualize episode and state combination
visualize_full_state_progression(experiment_id)
visualise_episode_interaction(experiment_id)
print(f"Finished visualizing experiments for experiment ID: {experiment_id}")


####################################################
##########      Evaluate Experiment       ##########
####################################################

experiment_signature = "InteractivePuzzle"

# Evaluate the experiment
print(f"Evaluate experiment {experiment_id}")
evaluate_episodes(experiment_id)
compile_experiment_evaluation(experiment_id, experiment_signature)
compile_episode_evaluation(experiment_id, experiment_signature)
compile_experiment_statistics(experiment_id, experiment_signature)


####################################################
##########        Plot Experiment         ##########
####################################################

agents = ['Claude', 'Gemini', 'GPT-4', 'Qwen']
modalities = ['text', 'vision']
baseline_agents = ['OptimalAgentBaseline', 'RandomInvalidAgentBaseline', 'RandomValidAgentBaseline']
baseline_modalities = ['text', 'vision']

plot_episode_evaluate_a_star_heuristic(experiment_id, experiment_signature="InteractivePuzzle")

# Evaluate and plot for each episode of the experiment
plot_heat_map_episode_level_average(
    experiment_id=experiment_id,
    agents=agents,
    modalities=modalities
)

# Evaluate and plot for each episode of the experiment
plot_csv_with_confidence_interval(
    experiment_id=experiment_id,
    agents=agents,
    modalities=modalities,
    show_confidence_interval=False
)

# Evaluate and plot for each episode of the experiment
plot_bar_plot_with_baselines(
    experiment_id=experiment_id,
    agents=agents,
    modalities=modalities,
    baseline_agents=baseline_agents,
    baseline_modalities=None
)