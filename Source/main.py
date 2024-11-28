from Configuration.puzzle_config_main import generate_SUP_configs, generate_SGP_configs
from Experiment.main2 import run_experiment
from Evaluation.evaluate_results_main import evaluate

# Generate configuration files for the experiment

# Parameters
board_size = 5
num_geoms = 5
complexity_min_max = [5, 20]  # smallest and highest complexity to be considered
complexity_bin_size = 10  # how many puzzles per complexity
shapes = ['cube', 'sphere', 'pyramid', 'cylinder', 'cone']
colors = ['red', 'green', 'blue', 'yellow', 'purple']

# Generate Sliding Geom Puzzle (SGP) configuration files
generate_SGP_configs(board_size, num_geoms, complexity_min_max, complexity_bin_size, shapes, colors)

# Parameters
num_geoms_min_max = [1, 10]

# Generate Scene Understanding Problem (SUP) configuration files
generate_SUP_configs(board_size, num_geoms_min_max, complexity_bin_size, shapes, colors)

# Run the experiment
run_experiment()

# Evaluate the experiment
evaluate()