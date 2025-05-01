from tqdm import tqdm

from .experiment_runner import ExperimentRunner

# Model imports
from ..models.observation_model import ObservationModel
from ..models.action_model import ActionModel
from ..models.experiment_model import ExperimentDataModel

# Agent imports
from ..agent.agent import Agent
from ..agent.agent_user import UserAgent  # Required for Agent's factory pattern

# Util imports
from ..utility.json_file_handler import JsonFileHandler
from ..utility.data_path_handler import DataPathHandler


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
        self.config_dataset_dict = JsonFileHandler.expand_jsons(config_dataset_dict, self.env_params)

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
                episode_signature = self.episode_name_template.format(simulation_config.get('config_instance_id', 'unknown'))
                episode_dir = f"experiments/{self.experiment_id}/episodes/{episode_signature}"

                if episode_signature in self.checkpoint_state["completed"]:
                    # experiment_logger.info(f"Skipping completed episode: {episode_signature}")
                    continue  # Skip if already completed

                # Move the JSON and image files to the experiment path using the new utility function
                # log_separator(episode_signature, char="-")

                JsonFileHandler.save_json(data=simulation_config,
                                          file_signature="config",
                                          dest_dir=episode_dir)

                # Save the metadata into a JSON file in the episode_path
                JsonFileHandler.save_json(data=self.metadata,
                                          file_signature='metadata',
                                          dest_dir=episode_dir)

                # Set up logging for the episode
                # episode_logger = setup_episode_logging(episode_path, episode_signature)

                try:
                    # episode_logger.info(f"Running episode: {episode_signature}")

                    # Run the client
                    # experiment_logger.info(
                    #    f"Start Game with agent: {agent_name}, game: {game_name}, env: {env_name}, config: {config.get('config_instance_id', [])}")
                    # episode_logger.info(f"Completed episode: {episode_signature}")

                    # Set up environment
                    await self.run_episode(simulation_config, episode_dir)
                    self.add_checkpoint(episode_signature)
                    # experiment_logger.info(f"Episode {episode_signature} completed successfully.")

                except Exception as e:
                    # Handle any errors that occur within the action-perception loop
                    # experiment_logger.error(f"An error occurred during the action-perception loop: {e}")
                    # episode_logger.error(f"Error during episode {episode_signature}: {e}")
                    raise  # Re-raise the exception to propagate it after logging

                pbar.update(1)

            await self.websocket.close()
            return self.experiment_id

    async def run_episode(self, simulation_config, episode_dir) -> None:

        simulation_data_state, simulation_data_init = await self.send_setup(simulation_config)
        observation = ObservationModel(simulation_data_state, simulation_data_init)

        #run steps until game done or max steps
        while not self.is_done(observation):

            response_prompt = self.agent.act(observation)
            action = ActionModel(response_prompt)

            # run predicted actions until game done, max steps or no predicted actions remain
            while not (self.is_done(observation) or action.is_empty):

                simulation_data_state = await self.env_step(action.pop_action())
                observation_new = ObservationModel(simulation_data_state, simulation_data_init)
                ExperimentDataModel.save_episode_data(observation, action, observation_new, episode_dir)

                observation = observation_new

        await self.send_reset()

    def is_done(self, observation: ObservationModel) -> bool:

        return observation.is_done or observation.step_num >= self.game_params.get("max_game_length", float("inf"))