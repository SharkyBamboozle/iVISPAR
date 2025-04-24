from tqdm import tqdm
import json

from .experiment_runner import ExperimentRunner
from ..utility.json_file_handler import JsonFileHandler
from ..utility.data_path_handler import DataPathHandler

# Agent imports
from ..agent.agent_observation import Observation
from ..agent.agent_action import Action
from ..agent.agent_systems import Agent
from ..agent.agent_system_user import UserAgent  # Required for Agent's factory pattern


@ExperimentRunner.register_subclass("geom_board")
class ExperimentRunnerGeomBoard(ExperimentRunner):

    def __init__(self, experiment_param_signature: str):
        super().__init__(experiment_param_signature)

        self.agent_params = self._experiment_params.get("agent", None)
        self.game_params = self._experiment_params.get("game", None)
        self.env_params = self._experiment_params.get("env", None)

        self.agent = Agent(self.agent_params)

        # Load dataset and expand config files with env params
        config_dataset_dict = JsonFileHandler.load_all_jsons(
            source_dir=f"configs/{self.game_params.get('config_id', None)}/dataset")
        print(f"configs/{self.game_params.get('config_id', None)}/dataset")
        print(len(config_dataset_dict))
        self.config_dataset_dict = JsonFileHandler.expand_jsons(config_dataset_dict, self.env_params)
        print(len(self.config_dataset_dict))

        # Create a dictionary to save env, agent, and game data
        self.metadata = {
            "env": self.env_params,
            "agent": self.agent_params,
            "game": self.game_params
        }

        self.episode_name_template = (f"episode_{self.agent_params['agent_type']}{self.agent_params['model_type']}"
                                      f"_{self.game_params['game_type']}{self.game_params['config_id']}"
                                      f"_{self.env_params['env_type']}_{{}}")

    async def run_episodes(self) -> None:
        """Run evaluation or training loop. Must be implemented by subclasses."""

        total_iterations = max(self.game_params.get('num_game_env', 0), len(self.config_dataset_dict))

        # Iterate through config files and update progress
        # Loop through env, agent and game
        with tqdm(total=total_iterations, desc="Total Progress") as pbar:
            for simulation_config in self.config_dataset_dict[:self.game_params.get('num_game_env', 0)]: # Limit to num_game_env

                # Construct the subdirectory name
                episode_name = self.episode_name_template.format(simulation_config.get('config_instance_id', 'unknown'))
                episode_path = DataPathHandler.ensure_dir(f"experiments/{self.experiment_id}/episodes/{episode_name}")

                if episode_name in self.checkpoint_state["completed"]:
                    # experiment_logger.info(f"Skipping completed episode: {episode_name}")
                    continue  # Skip if already completed

                # Move the JSON and image files to the experiment path using the new utility function
                # log_separator(episode_name, char="-")

                JsonFileHandler.save_json(data=simulation_config,
                                          file_signature="config",
                                          dest_dir=episode_path)

                # Save the metadata into a JSON file in the episode_path
                JsonFileHandler.save_json(data=self.metadata,
                                          file_signature='metadata.json',
                                          dest_dir=episode_path)

                # Set up logging for the episode
                # episode_logger = setup_episode_logging(episode_path, episode_name)

                try:
                    # episode_logger.info(f"Running episode: {episode_name}")

                    # Run the client
                    # experiment_logger.info(
                    #    f"Start Game with agent: {agent_name}, game: {game_name}, env: {env_name}, config: {config.get('config_instance_id', [])}")
                    # episode_logger.info(f"Completed episode: {episode_name}")

                    # Set up environment
                    await self.run_episode(simulation_config, episode_path)
                    self.add_checkpoint(episode_name)
                    # experiment_logger.info(f"Episode {episode_name} completed successfully.")

                except Exception as e:
                    # Handle any errors that occur within the action-perception loop
                    # experiment_logger.error(f"An error occurred during the action-perception loop: {e}")
                    # episode_logger.error(f"Error during episode {episode_name}: {e}")
                    raise  # Re-raise the exception to propagate it after logging

                pbar.update(1)

            await self.websocket.close()
            return self.experiment_id

    async def run_episode(self, simulation_config, episode_path) -> None:

        await self.send_setup(simulation_config)
        response = await self.websocket.recv()
        state = json.loads(response)

        #run steps
        while not self.is_done(state):
            observation = Observation(state)
            response = self.agent.act(observation)
            action = Action(response)

            # run predicted actions
            while not self.is_done(state):
                state = await self.env_step(action.get_action)
                self.save_episode_data(observation, action, state, episode_path)

        await self.send_reset()

    def is_done(self, state: dict) -> bool:
        """
        Checks if the episode should end based on:
        - 'game_done' flag in the only step of the state
        - Configured max_game_length

        Assumes state has exactly one key like 'step 0'.

        Args:
            state (dict): Single-step dictionary from the simulation.

        Returns:
            bool: True if done, else False.
        """
        step_key = next(iter(state))
        step_number = int(step_key.split(" ")[1])
        game_done = state[step_key].get("game_done", False)
        max_steps = self.game_params.get("max_game_length", float("inf"))

        return game_done or step_number >= max_steps

    def save_episode_data(self, observation, action, new_state, episode_path):

        try:
            episode_log = JsonFileHandler.load_json(file_signature="episode_log",
                                                    source_dir=f"experiment/{episode_path}")
        except FileNotFoundError:
            episode_log = {}

        new_step_dict = {
            f"step {observation.step_num}": {
                "prompt": observation.prompt,
                "observation": observation.state.board_state,
                "chain_of_thoughts": action.CoT,
                "action_list": action.action_list,
                "action_effective": new_state.action,
                "action_validity": new_state.validity,
                "game_done": new_state.done,
            }
        }

        episode_log = JsonFileHandler.expand_jsons(data=episode_log, additional_params=new_step_dict)
        JsonFileHandler.save_json(data=episode_log, file_signature="episode_log", dest_dir=episode_path)