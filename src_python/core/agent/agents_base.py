from abc import ABC, abstractmethod
from typing import Type, Callable, Dict, Any
import requests
import logging

from ..models.observation_model import ObservationModel
from ..utility.json_file_handler import JsonFileHandler

class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    Agents are responsible for producing actions in response to environment observations.
    Subclasses must implement the full action pipeline:
      - build_messages: convert observations into prompts
      - run_model: execute model call
      - parse_response: extract final string action
    """
    _registry: Dict[str, Type["BaseAgent"]] = {}

    def __new__(cls, agent_params: Dict[str, Any]) -> "BaseAgent":
        """
         Factory method to create agent instances based on the 'agent_type' field.
         Automatically looks up the correct registered subclass.

         Args:
             agent_params (Dict[str, Any]): Configuration parameters for the agent.

         Returns:
             BaseAgent: Instantiated subclass matching the 'agent_type'.
         """
        agent_type = agent_params.get("agent_type", "").lower()
        if agent_type in cls._registry:
            instance = super().__new__(cls._registry[agent_type])
            instance._agent_params = agent_params
            return instance
        raise ValueError(f"Unknown agent type: {agent_type}. Available types: {list(cls._registry.keys())}")

    def __init__(self, agent_params: Dict[str, Any]):
        """
        Base initialization for all agents.

        Loads API keys and stores basic metadata. Subclasses may extend.
        """
        self.agent_type = agent_params["agent_type"]
        self.model_type = agent_params["agent_params"]["model_type"]
        self.max_tokens = agent_params["agent_params"]["max_tokens"]
        self.temperature = agent_params["agent_params"]["temperature"]
        self.api_keys = JsonFileHandler.load_json(file_signature="api_keys", source_dir="settings")

    @classmethod
    def register_subclass(cls, agent_type: str) -> Callable[[Type["BaseAgent"]], Type["BaseAgent"]]:
        """
        Class decorator to register agent subclasses for use in the factory.

        Example:
            @BaseAgent.register_subclass("openai_gpt")
            class GPTAgent(BaseAgent):
                ...
        """
        def decorator(subclass: Type["BaseAgent"]) -> Type["BaseAgent"]:
            cls._registry[agent_type.lower()] = subclass
            return subclass
        return decorator

    @abstractmethod
    def act(self, observation: ObservationModel) -> str:
        """
        Executes the full action-generation pipeline.

        Args:
            observation (ObservationModel): Current environment state.

        Returns:
            str: Model-generated response string.
        """
        pass

@BaseAgent.register_subclass("user")
class UserAgent(BaseAgent):
    """
    A manual agent for debugging and interactive testing.

    Prompts the user to type an action at each step. Useful for step-by-step exploration
    or validating environment behavior without relying on an automated model.
    """

    def act(self, observation: ObservationModel) -> str:
        """
        Asks the user to enter an action manually.

        Args:
            observation (ObservationModel): The current environment state (not used).

        Returns:
            str: The user's input formatted as an action string.
        """
        return f"action: {input('Enter action: ').strip()}"