from abc import ABC, abstractmethod
from typing import Type, Callable, Dict, Any, List, Tuple
import logging


class Agent(ABC):
    """
    Abstract base class for agents.
    Provides a template for specific agents with standardized methods for interaction.
    """

    _registry: Dict[str, Type["Agent"]] = {}

    def __new__(cls, agent_params: Dict[str, Any]) -> "Agent":
        agent_type = agent_params.get("agent_type", "").lower()
        if agent_type in cls._registry:
            instance = super().__new__(cls._registry[agent_type])
            instance._agent_params = agent_params
            return instance
        raise ValueError(f"Unknown agent type: {agent_type}. Available types: {list(cls._registry.keys())}")

    def __init__(self, agent_params: Dict[str, Any]):
        self.agent_id = agent_params.get("agent_id", "unknown_agent")
        self.episode_path = agent_params.get("episode_path", None)

        # Wrap the abstract act method with the processing pipeline
        self.act = self._wrap_act(self.act)

    @classmethod
    def register_subclass(cls, agent_type: str) -> Callable[[Type["Agent"]], Type["Agent"]]:
        def decorator(subclass: Type["Agent"]) -> Type["Agent"]:
            cls._registry[agent_type.lower()] = subclass
            return subclass
        return decorator

    def _wrap_act(self, act_method):
        def wrapped(state):

            # Run subclass's act logic to get raw model output (prompt)
            response = act_method(state)

            return response  # returns list of actions and CoT (not Action object for now)

        return wrapped

    @abstractmethod
    def act(self, state: Any) -> str:
        """
        Abstract method to be implemented by subclasses to produce a raw response string.
        """
        pass
