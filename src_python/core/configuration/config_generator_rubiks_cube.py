from .config_generator import ConfigGenerator

@ConfigGenerator.register_subclass("rubiks_cube")
class ConfigGeneratorRubiksCube(ConfigGenerator):
    """Configuration generator for the 'rubiks_cube' puzzle game."""

    def generate_dataset(self) -> None:
        pass