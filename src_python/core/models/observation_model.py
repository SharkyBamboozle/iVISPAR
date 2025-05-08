from abc import ABC, abstractmethod
from typing import Dict, Type, Callable, Any


class ObservationModel(ABC):
    """
    Abstract base class for all observation models.

    Observation models provide a unified wrapper around environment state data,
    exposing common properties and utility functions for agents.

    Subclasses must be registered and implement this interface.
    """
    _registry: Dict[str, Type["ObservationModel"]] = {}

    def __new__(cls, observation_data: Dict[str, Any], goal_data: Dict[str, Any],
                game_params: Dict[str, Any]) -> "ObservationModel":
        """
        Factory method that returns the correct subclass based on the
        'observation_model_type' field in game_params.

        Args:
            observation_data (dict): The current simulation state.
            goal_data (dict): The goal state or reference state.
            game_params (dict): Experiment or game configuration.

        Returns:
            ObservationModel: The instantiated subclass.
        """
        model_type = game_params.get("observation_model_type", "").lower()
        if model_type not in cls._registry:
            raise ValueError(f"Unknown observation_model_type: {model_type}. Registered: {list(cls._registry)}")

        return super().__new__(cls._registry[model_type])

    def __init__(self, observation_data: Dict[str, Any], goal_data: Dict[str, Any], game_params: Dict[str, Any]):
        """
        Initializes the observation model. Subclasses must call this if overridden.

        Args:
            observation_data (dict): State data from the simulator.
            goal_data (dict): Target or goal state.
            game_params (dict): Configuration settings.
        """
        self.observation_data = observation_data
        self.goal_data = goal_data
        self.game_params = game_params

    @classmethod
    def register_subclass(cls, model_type: str) -> Callable[[Type["ObservationModel"]], Type["ObservationModel"]]:
        """
        Class decorator for registering observation model subclasses.

        Usage:
            @ObservationModel.register_subclass("geom_board")
            class GeomBoardObservationModel(ObservationModel):
                ...
        """

        def decorator(subclass: Type["ObservationModel"]) -> Type["ObservationModel"]:
            cls._registry[model_type.lower()] = subclass
            return subclass

        return decorator

    @abstractmethod
    def board_data(self) -> Any:
        """Return the current board configuration."""
        pass

    @abstractmethod
    def is_done(self) -> bool:
        """Return whether the game is complete."""
        pass

    @abstractmethod
    def step_num(self) -> int:
        """Return the current step number."""
        pass
