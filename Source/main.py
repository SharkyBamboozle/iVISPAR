from Configuration.generate_sgp_configs import generate_sgp_configs
from Visualisation.visualise_config_set_statistics import visualize_config_stats
from Experiment.main2 import run_experiment
from Evaluation.evaluate_results_main import evaluate

# Generate configuration files for the experiment

# Parameters
board_size = 5
num_geoms = 5
complexity_min_max = {"c1": {"min": 10, "max": 15},  # smallest and highest c1 complexity to be considered
                      "c2": {"min": 0, "max": 1}}  # smallest and highest c2 complexity to be considered
complexity_bin_size = 2  # amount of puzzle configs per complexity bin
shapes = ['cube', 'sphere', 'pyramid']  # , 'cylinder', 'cone', 'prism']
colors = ['red', 'green', 'blue']  # , 'yellow', 'purple', 'orange']

# Generate Sliding Geom Puzzle (SGP) configuration files
config_id = generate_sgp_configs(board_size, num_geoms, complexity_min_max, complexity_bin_size, shapes, colors)
print(f"Finished Generate Sliding Geom Puzzle (SGP) configuration files with ID: {config_id}")
visualize_config_stats(config_id)


# Run the experiment
run_experiment()

# Evaluate the experiment
evaluate()