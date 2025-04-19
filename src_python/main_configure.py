"""
Main entry point to generate a dataset of geom board environments for later experiments.
Minimal interface: adjust the config parameters signature to change the config set.
"""

from core.configuration.config_generator import ConfigGenerator
from core.configuration.vis_configs_geom_board import vis_configs_geom_board
from core.configuration.eval_configs_geom_board import eval_configs_geom_board
import core.configuration.config_generator_geom_board  # Required for ConfigGenerator's factory pattern

def main(config_params_signature: str) -> None:
    config_generator = ConfigGenerator(config_params_signature)

    print(f"Start generating configs for {config_generator.config_id}") #TODO replace with logging
    config_generator.generate_dataset()

    # TODO: Add logging
    vis_configs_geom_board()  # TODO: Replace or parameterize if needed
    eval_configs_geom_board()  # TODO: Replace or parameterize if needed

if __name__ == "__main__":
    config_params_signature = "params_geom_board_config_example"
    main(config_params_signature=config_params_signature)
