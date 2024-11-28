"""
Main file to generate a set of config files for the Sliding Geom Puzzle (SGP) and the Scene Understanding Problem (SUP).
"""

# Import statements
import os
from datetime import datetime

from puzzle_config_builder import build_SGP_configs
from puzzle_config_builder import build_SUP_configs
from puzzle_config_visualizer import visualize_config_stats
from puzzle_config_visualizer import visualize_configs
#from puzzle_config_visualizer import visualize_shortest_sequence
#from puzzle_viz_3 import process_json_files


def _prepare_generate_configs(puzzle_type, board_size, num_geoms, shapes, colors):

    geoms = [(shape, color) for shape in shapes for color in colors]
    config_id = datetime.now().strftime("%Y%m%d_%H%M%S")  # Setup ID directly assigned here

    # Validate parameters
    if num_geoms > board_size ** 2:
        raise ValueError("Number of geoms exceeds the total cells on the board.")
    if num_geoms > len(geoms):
        raise ValueError("Number of geoms exceeds the total number of geoms available.")

    # Set up directories
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    config_dir = os.path.join(base_dir, 'Data', 'Configs', f"{puzzle_type}_ID_{config_id}")
    os.makedirs(config_dir, exist_ok=True)

    return geoms, config_id, config_dir



def generate_SGP_configs(board_size, num_geoms, complexity_min_max, complexity_bin_size, shapes, colors):

    # Prepare config generation
    geoms, config_id, config_dir = _prepare_generate_configs("SGP", board_size, num_geoms, shapes, colors)

    # Generate configs
    build_SGP_configs(board_size, num_geoms, complexity_min_max, complexity_bin_size, geoms, config_id, config_dir)

    # Generate visualisations
    visualize_config_stats(config_dir)
    #visualize_configs(config_dir)
    #visualize_shortest_sequence(config_dir)
    #process_json_files(config_dir)


def generate_SUP_configs(board_size, num_geoms_min_max, complexity_bin_size, shapes, colors):

    # Prepare config generation
    geoms, config_id, config_dir = _prepare_generate_configs("SUP", board_size, num_geoms_min_max[1], shapes, colors)

    # Generate configs
    build_SUP_configs(board_size, num_geoms_min_max, complexity_bin_size, geoms, config_id, config_dir)

    # Generate visualisations
    visualize_config_stats(config_dir)
    visualize_configs(config_dir)


if __name__ == "__main__":

    # Parameters
    board_size = 4
    num_geoms = 15
    complexity_min_max = [0, 50]  # smallest and highest complexity to be considered
    complexity_bin_size = 100*1000  # how many puzzles per complexity
    shapes = ['cube', 'sphere', 'pyramid']#, 'cylinder', 'cone'] #prism
    colors = ['red', 'green', 'blue', 'yellow', 'purple'] #orange

    # Generate Sliding Geom Puzzle (SGP) configuration files
    generate_SGP_configs(board_size, num_geoms, complexity_min_max, complexity_bin_size, shapes, colors)

    # Parameters
    num_geoms_min_max = [1, 5]

    # Generate Scene Understanding Problem (SUP) configuration files
    #generate_SUP_configs(board_size, num_geoms_min_max, complexity_bin_size, shapes, colors)
