from tqdm import tqdm
import json

from src_python.core.experiment.experiment_runner import ExperimentRunner
from src_python.core.utility.json_file_handler import JsonFileHandler
from src_python.core.utility.data_path_handler import DataPathHandler
from src_python.core.models.tmp.observation_model2 import Observation
from src_python.core.models.tmp.action_model2 import ActionModel
from src_python.core.agent.agent import Agent


@ExperimentRunner.register_subclass("geom_board")
class ExperimentRunnerGeomBoard(ExperimentRunner):

    def __init__(self, experiment_param_signature: str):
        super().__init__(experiment_param_signature)

        self.agents = self._experiment_params.get("agents", None)
        self.games = self._experiment_params.get("games", None)
        self.envs = self._experiment_params.get("envs", None)

    async def run_episodes(self) -> None:
        """Run evaluation or training loop. Must be implemented by subclasses."""

        # Calculate total iterations more efficiently
        total_iterations = sum(
            game_params.get('num_game_env', 0)  # Directly get the number of environments per game
            for game_params in self.games.values()
        ) * len(self.envs) * len(self.agents)  # Multiply by the number of environments and agents

        # Loop through envs, agents and games
        with tqdm(total=total_iterations, desc="Total Progress") as pbar:
            for agent_name, agent_params in self.agents.items():
                agent = Agent(agent_params)

                for env_name, env_params in self.envs.items():

                    for game_name, game_params in self.games.items():

                        #Load dataset and expand config files with env params
                        config_param_dicts = JsonFileHandler.load_all_jsons(
                            source_dir=f"configs/{game_params.get('config_id', None)}/dataset")
                        config_param_dicts = JsonFileHandler.expand_jsons(config_param_dicts, env_params)
                        num_game_env = game_params.get('num_game_env', 0)

                        # Adjust progress bar to limited env number
                        if num_game_env > len(config_param_dicts):
                            #experiment_logger.warning(
                            #    f"Number of game environments exceeds the number of config files in the dataset, "
                            #    f"setting num_game_env to {len(json_file_paths)}."
                            #)
                            num_game_env = len(config_param_dicts)

                            # Dynamically recalculate and update `pbar.total`
                            adjusted_iterations = sum(num_game_env for game_params in self.games.values()
                                                      ) * len(self.envs) * len(self.agents)
                            pbar.total = adjusted_iterations
                            pbar.refresh()  # Refresh to reflect the updated total

                        config_param_dicts = config_param_dicts[:num_game_env]  # Limit to num_game_env

                        # Iterate through config files and update progress
                        for config_param_dict in config_param_dicts:

                            # Construct the subdirectory name
                            episode_name = f"episode_{agent_name}_{game_name}_{env_name}_{config_param_dict.get('config_instance_id', None)}"
                            episode_path = DataPathHandler.ensure_dir(f"experiments/{self.experiment_id}/episodes/{episode_name}")

                            if episode_name in self.checkpoint_state["completed"]:
                                #experiment_logger.info(f"Skipping completed episode: {episode_name}")
                                continue  # Skip if already completed

                            # Move the JSON and image files to the experiment path using the new utility function
                            #log_separator(episode_name, char="-")

                            JsonFileHandler.save_json(data=config_param_dict,
                                                      file_signature="config",
                                                      dest_dir=episode_path)

                            # Create a dictionary to save envs, agents, and games data
                            metadata = {
                                "env": {env_name: env_params},
                                "agent": {agent_name: agent_params},
                                "game": {game_name: game_params}
                            }

                            # Save the metadata into a JSON file in the episode_path
                            JsonFileHandler.save_json(data=metadata,
                                                      file_signature='metadata.json',
                                                      dest_dir=episode_path)
                            # Set up logging for the episode
                            #episode_logger = setup_episode_logging(episode_path, episode_name)

                            try:
                                #episode_logger.info(f"Running episode: {episode_name}")
                                # Set up environment
                                await self.send_setup(config_param_dict)

                                # Run the client
                                #experiment_logger.info(
                                #    f"Start Game with agent: {agent_name}, game: {game_name}, env: {env_name}, config: {config.get('config_instance_id', [])}")
                                #episode_logger.info(f"Completed episode: {episode_name}")

                                response = await self.websocket.recv()
                                state = json.loads(response)

                                while not self.is_done(state):
                                    observation = Observation(state)
                                    response = agent.act(observation)
                                    action = ActionModel(response)

                                    state = await self.env_step(action.get_action)
                                    self.save_episode_data(observation, action, state)

                                await self.send_reset()

                                self.add_checkpoint(episode_name)
                                #experiment_logger.info(f"Episode {episode_name} completed successfully.")

                            except Exception as e:
                                # Handle any errors that occur within the action-perception loop
                                #experiment_logger.error(f"An error occurred during the action-perception loop: {e}")
                                #episode_logger.error(f"Error during episode {episode_name}: {e}")
                                raise  # Re-raise the exception to propagate it after logging

                            pbar.update(1)

        await self.websocket.close()
        return self.experiment_id

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
        max_steps = self.games.get("max_game_length", float("inf"))

        return game_done or step_number >= max_steps

    def save_episode_data(self, observation_object, action_object, new_state):
        # load json
        # log step1
        # obs.prompt
        # obs.state.board_state
        # act.CoT
        # act.action_list
        # state.action
        # state.validity
        # state.done
        pass