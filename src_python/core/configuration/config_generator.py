"""
Abstract Base Class for Generating Configuration-File Datasets for iVISPAR.

This class provides the core logic for dataset generation, including:
1. Creating and managing directory structures for configurations and datasets.
2. Loading configuration parameters and performing runtime validation.
3. Initializing a logger for tracking the dataset generation process.

### Usage:
- Subclass this class and implement the `generate_dataset()` method.
- Set a game_params_model subclass for parameter validation

### Automatic Subclass Selection:
This class uses the Factory Pattern, returning the appropriate subclass based on
the `game_type` parameter found in the JSON parameter file.
"""

from pathlib import Path
from abc import ABC, abstractmethod
from typing import Type, Callable, Optional, Dict, Any
import logging

from .param_model import BaseGameParamsModel, ConfigModel
from ..utility.data_path_handler import DataPathHandler
from ..utility.json_file_handler import JsonFileHandler
from ..utility.log_handler import LogHandler


class ConfigGenerator(ABC):
    """Generates configuration file dataset for iVISPAR experiments."""

    _registry: Dict[str, Type["ConfigGenerator"]] = {}  # Game ID → Subclass mapping
    game_params_model: Type[BaseGameParamsModel]  # Dynamically set in subclasses

    #-------------------------------#
    #       Special Methods         #
    #-------------------------------#
    def __new__(cls, config_param_signature: str) -> "ConfigGenerator":
        """Dynamically return an instance of the correct subclass based on game_type."""
        config_params: Dict[str, Any] = JsonFileHandler.load_json(config_param_signature, source_dir='params')
        game_type: str = config_params.get("game_type", None).lower()

        if game_type in cls._registry:
            instance = super().__new__(cls._registry[game_type])
            instance._config_params = config_params  # Pass loaded JSON to the instance
            return instance

        raise ValueError(f"Unknown game type: {game_type}. Available types: {list(cls._registry.keys())}")

    def __init__(self, config_param_signature: str):
        """Initialize configuration parameters from JSON."""
        config_params: ConfigModel =  ConfigModel(**self._config_params)

        self.config_id: str = config_params.config_id
        self.description: str = config_params.description
        self.game_type: str = config_params.game_type

        # Declare attributes for clarity, even if they will be set later
        self.config_dir: Path = Path()
        self.dataset_dir: Path = Path()
        self.config_logger: Optional[logging.Logger] = None

        # Dynamically validate game_params with the appropriate Pydantic model
        self.game_params: BaseGameParamsModel = self.validate_game_params(config_params.game_params)

        # Wrap generate_dataset_logic with setup enforcement
        self.generate_dataset = self._setup_wrapper(self.generate_dataset)


    #-------------------------------#
    #       Class Methods           #
    #-------------------------------#
    @classmethod
    def register_subclass(cls, game_type: str) -> Callable[[Type["ConfigGenerator"]], Type["ConfigGenerator"]]:
        """Decorator to register subclasses dynamically based on the game_type from config_param JSON file."""
        def decorator(subclass: Type["ConfigGenerator"]) -> Type["ConfigGenerator"]:
            cls._registry[game_type.lower()] = subclass
            return subclass
        return decorator


    #-------------------------------#
    #       Protected Methods       #
    #-------------------------------#
    def _setup_wrapper(self, user_method):
        """Wrapper to enforce setup logic before running the subclass's dataset generation."""

        def wrapped_method(*args, **kwargs):
            # Enforce common setup steps
            self.config_dir = DataPathHandler.ensure_dir(subdir_names=f'configs/{self.config_id}')
            self.dataset_dir = DataPathHandler.ensure_dir(subdir_names=f'configs/{self.config_id}/dataset')

            JsonFileHandler.save_json(data=self._config_params, file_signature=self.config_id, dest_dir= self.config_dir)

            #self.config_logger = LogHandler.get_logger(self.config_id) #TODO

            # Call the original method (subclass's generate_dataset)
            return user_method(*args, **kwargs)

        return wrapped_method


    #-------------------------------#
    #       Instance Methods        #
    #-------------------------------#
    def validate_game_params(self, game_params: Dict[str, Any]) -> BaseGameParamsModel:
        """Validate game_params using the appropriate Pydantic model."""
        return self.game_params_model.from_dict(game_params)


    #-------------------------------#
    #       Abstract Methods        #
    #-------------------------------#
    @abstractmethod
    def generate_dataset(self) -> None:
        """Default dataset generation method (override in subclasses)."""
        pass