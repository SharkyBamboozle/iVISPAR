"""
Abstract Base Class for Running iVISPAR Experiments
===================================================

This module defines the ExperimentRunner base class, which provides a
standardized interface for executing and managing experiment loops
within the iVISPAR framework.

Core Responsibilities:
----------------------
- Load experiment parameters from a config JSON file.
- Select the appropriate runner subclass based on game type (Factory Pattern).
- Set up directories for logging experiment data and results.
- Manage the run loop for agents interacting with environments.
- Return a unique experiment ID for traceability.

Usage:
------
1. Subclass this base class and implement the `run_episodes()` method.
2. Use the `@ExperimentRunner.register_subclass(game_type)` decorator
   to register your subclass.
3. Instantiate your runner using:

    runner = ExperimentRunner("your_param_file.json")
    experiment_id = runner.run_episodes()

4. The subclass should define the core experiment logic

Note:
-----
This class is intentionally decoupled from Gym and other frameworks to allow for
flexibility in running experiments with custom agents, planners, or evaluators.

"""

import os
import base64
import json
import shutil
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Type, Callable, Optional, Dict, Any
import logging
import websockets

from .webgl_socket_server import run_socketserver_in_background
from .web_server import run_WebSocket_server_in_background

from ..utility.data_path_handler import DataPathHandler
from ..utility.json_file_handler import JsonFileHandler


class ExperimentRunner(ABC):
    """Abstract base class for running iVISPAR experiment loops."""

    _registry: Dict[str, Type["ExperimentRunner"]] = {}  # game_type → subclass mapping

    #-------------------------------#
    #       Special Methods         #
    #-------------------------------#
    def __new__(cls, experiment_param_signature: str) -> "ExperimentRunner":
        config_params: Dict[str, Any] = JsonFileHandler.load_json(experiment_param_signature, source_dir='params')
        game_type: str = config_params["game"]["game_type"].lower()

        if game_type in cls._registry:
            instance = super().__new__(cls._registry[game_type])
            instance._experiment_params = config_params
            return instance

        raise ValueError(f"Unknown game type: {game_type}. Available types: {list(cls._registry.keys())}")

    def __init__(self, experiment_param_signature: str):
        self.experiment_id = self._experiment_params.get("experiment_id", "unknown_experiment")
        self.game_type = self._experiment_params.get("game_type", "unknown_game")

        self.experiment_dir: Path = Path()
        self.experiment_logger: Optional[logging.Logger] = None

        self.checkpoint_state = None
        self.websocket = None #Assigned in self.wrapped_method
        self.network_id = None #Assigned in self.wrapped_method
        self.partner_id = None #Assigned in self.wrapped_method

        # Wrap run_episodes with setup logic
        self.run_episodes = self._setup_wrapper(self.run_episodes)

    #-------------------------------#
    #       Class Methods           #
    #-------------------------------#
    @classmethod
    def register_subclass(cls, game_type: str) -> Callable[[Type["ExperimentRunner"]], Type["ExperimentRunner"]]:
        def decorator(subclass: Type["ExperimentRunner"]) -> Type["ExperimentRunner"]:
            cls._registry[game_type.lower()] = subclass
            return subclass
        return decorator

    #-------------------------------#
    #       Protected Methods       #
    #-------------------------------#
    def _setup_wrapper(self, user_method):
        async def wrapped_method(*args, **kwargs):
            # Enforce common setup steps
            self.experiment_dir = DataPathHandler.ensure_dir(subdir_names=f'experiments/{self.experiment_id}')

            # Save param file to experiment directory
            JsonFileHandler.save_json(data=self._experiment_params, file_signature=self.experiment_id,
                                      dest_dir=self.experiment_dir, overwrite=True)

            # Setup checkpoint file in experiment directory
            try:
                self.checkpoint_state = JsonFileHandler.load_json(
                    'experiment_checkpoint', source_dir=self.experiment_dir)
                print(f"Checkpoint data found, loading checkpoints from json file")
                self.remove_incomplete_episode()
            except FileNotFoundError as e:
                # Log it, warn the user, or silently continue
                print(f"No checkpoint yet, creating fresh checkpoint state: {e}")
                JsonFileHandler.save_json(
                    data={"completed": []},
                    file_signature='experiment_checkpoint',
                    dest_dir=self.experiment_dir,
                    overwrite=False
                )

            # Optional: Init logger (uncomment if needed)
            # self.experiment_logger = LogHandler.get_logger(self.experiment_id) #TODO

            # Run websocket server and WebGL server
            run_WebSocket_server_in_background()
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
            webApp_dir = os.path.join(base_dir, 'app_builds')
            print(webApp_dir)
            run_socketserver_in_background(webApp_dir)

            # Initialize connection for websocket server
            uri = "ws://localhost:1984" # optionally run ivispar on the server uri_remote = "wss://ivispar.microcosm.ai:1984"
            self.websocket = await websockets.connect(uri, max_size=10000000, ping_interval=10, ping_timeout=360)
            self.network_id = await self.get_network_id()
            self.partner_id = await self.initialize_connection()

            # Call subclass-defined episode loop
            await user_method(*args, **kwargs)

            # Return the experiment ID so we can track it
            return self.experiment_id

        return wrapped_method

    #-------------------------------#
    #       Instance Methods        #
    #-------------------------------#
    async def initialize_connection(self):
        """
        Initialize the WebSocket connection, perform the handshake, and register the partner ID.

        Args:
            uri (str): The WebSocket server URI.

        Returns:
            tuple: A tuple containing the WebSocket connection, network ID, and partner ID.
        """
        try:
            # Register partner ID
            is_connected = False
            partner_id = None
            while not is_connected:
                partner_id = input("Please enter the remote client id: ")
                print()  # This ensures the cursor moves to a new line

                await self.send_handshake(partner_id)
                logging.info("Sending handshake...")  # TODO reintroduce logging
                response = await self.websocket.recv()
                message_data = json.loads(response)
                command = message_data.get("command")
                logging.info(f"Received {command}: {message_data.get('messages')}")  # TODO reintroduce logging
                if command == "ACK":
                    is_connected = True

        except Exception as e:
            await self.websocket.close()
            raise e

        return partner_id

    async def send_handshake(self, partner_id):
        message_data = {
            "command": "Handshake",
            "from": self.network_id,
            "to": partner_id,
            "messages": ["Action Perception client attempting to register partner id with the game"],
            "payload": base64.b64encode(b"nothing here").decode("utf-8"),
        }
        await self.websocket.send(json.dumps(message_data))

    async def get_network_id(self):
        try:
            # Perform the handshake
            response = await self.websocket.recv()
            message_data = json.loads(response)
            if message_data.get("command") != "Handshake":
                # logging.error("Handshake failed: Unexpected response from server.") #TODO reintroduce logging
                raise RuntimeError("Handshake failed: Unexpected response from server.")

            network_id = message_data.get("to")
            logging.info(message_data.get("messages"))  # TODO reintroduce logging

        except Exception as e:
            await self.websocket.close()
            raise e

        return network_id

    async def send_setup(self, config_param_dict):
        message_data = {
            "command": "Setup",
            "from": self.network_id,
            "to": self.partner_id,
            "messages": [JsonFileHandler.encode_json(config_param_dict)],
            "payload": base64.b64encode(b"nothing here").decode("utf-8"),
        }
        await self.websocket.send(json.dumps(message_data))

    async def env_step(self, action):
        # Exit the loop if the user wants to close the connection
        if action.lower() == "reset":
            await self.send_reset()
            #break

            return {None}
        elif action.lower() == "exit":
            await self.send_reset()
            await self.websocket.close()
            #episode_logger.info("Connection closed")
            #break

            return {None}
        else:
            message_data = self.send_msg(user_message=action)

            return message_data

    async def send_reset(self):
        message_data = {
            "command": "Reset",
            "from": self.network_id,
            "to": self.partner_id,  # Server ID or specific target ID
            "messages": ["reset to main menu"],
            "payload": base64.b64encode(b"Optional binary data").decode("utf-8")
        }
        await self.websocket.send(json.dumps(message_data))

    async def send_msg(self, user_message):
        message_list = [msg.strip() for msg in user_message.split(",")]
        # Create a JSON-formatted message
        message_data = {
            "command": "GameInteraction",
            "from": self.network_id,
            "to": self.partner_id,  # Server ID or specific target ID
            "messages": message_list,
            "payload": base64.b64encode(b"Optional binary data").decode("utf-8")
        }
        await self.websocket.send(json.dumps(message_data))

        response = await self.websocket.recv()
        return json.loads(response)

    def add_checkpoint(self, episode_name):
        self.checkpoint_state["completed"].append(episode_name)
        JsonFileHandler.save_json(
            data=self.checkpoint_state,
            file_signature='experiment_checkpoint',
            dest_dir=self.experiment_dir,
            overwrite=True
        )

    def remove_incomplete_episode(self):
        """
        Removes any incomplete episode directories that are not marked as completed
        in the checkpoint checkpoint_state and stores information about removed episodes.

        Args:
            experiment_id (str): The ID of the experiment to clean up.
            checkpoint_state (dict): The current checkpoint checkpoint_state with completed episodes.
        """
        logging.info("Checking for incomplete episodes.")
        experiment_dir =  DataPathHandler.ensure_dir(subdir_names=f'experiments/{self.experiment_id}/episodes')

        # List all episode directories in the experiment folder
        all_episode_dirs = [
            d for d in os.listdir(experiment_dir)
            if os.path.isdir(os.path.join(experiment_dir, d))
        ]

        # Get the list of completed episodes from the checkpoint checkpoint_state
        completed_episodes = self.checkpoint_state.get("completed", [])
        removed_episodes = self.checkpoint_state.setdefault("removed", {})
        num_removed_episodes = 0

        # Iterate over all episode directories
        for episode_dir in all_episode_dirs:
            # If the episode is not marked as completed, remove it
            if episode_dir not in completed_episodes:
                episode_path = os.path.join(experiment_dir, episode_dir)

                # Store removal info
                removed_episodes[episode_dir] = {
                    "timestamp": datetime.now().isoformat(),
                    "reason": "Incomplete episode removal"
                }
                num_removed_episodes += 1
                logging.info(f"Removing incomplete episode {num_removed_episodes}: {episode_dir}")
                shutil.rmtree(episode_path)
        if num_removed_episodes == 0:
            logging.info("No incomplete episode found.")

        # Save the updated checkpoint checkpoint_state
        JsonFileHandler.save_json(
            data=self.checkpoint_state,
            file_signature='experiment_checkpoint',
            dest_dir=self.experiment_dir,
            overwrite=True
        )
        logging.info("Incomplete episode cleanup complete.")

    #-------------------------------#
    #       Abstract Methods        #
    #-------------------------------#
    @abstractmethod
    async def run_episodes(self) -> None:
        """Run evaluation or training loop. Must be implemented by subclasses."""
        pass