import asyncio
import os
from datetime import datetime
import json
import base64
import logging
from tqdm import tqdm
import fnmatch


import experiment_utilities as util
from webgl_socket_server import run_socketserver_in_background
from web_server import run_WebSocket_server_in_background
from init_experiment_components import init_env, init_agent, init_game
from action_perception_loop import initialize_connection, interact_with_server as action_perception_loop
from checkpoints import load_checkpoint, save_checkpoint, remove_incomplete_episode
from experiment_logging import setup_experiment_logging, setup_episode_logging, log_separator


async def run_experiment(games, agents, envs, experiment_id=None):

    # Set up experiment ID and directory
    experiment_id = experiment_id if experiment_id else datetime.now().strftime("experiment_ID_%Y%m%d_%H%M%S")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    experiment_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id)
    os.makedirs(experiment_dir, exist_ok=True)

    experiment_logger = setup_experiment_logging(experiment_id)
    log_separator(f"Experiment {experiment_id} started.")
    state = load_checkpoint(experiment_id) or {"completed": []}
    remove_incomplete_episode(experiment_id, state)

    # Run the server
    experiment_logger.info("Starting WebSocket Server...")
    run_WebSocket_server_in_background()

    # run WebGL Server
    experiment_logger.info("Starting WebGL Server...")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    webApp_dir = os.path.join(base_dir, 'iVISPAR')
    run_socketserver_in_background(webApp_dir)

    uri = "ws://localhost:1984"
    # the ivispar on the server
    uri_remote = "wss://ivispar.microcosm.ai:1984"
    websocket, network_id, partner_id = await initialize_connection(uri)

    log_separator(f"Start Experiment Loop.")

    # Calculate total iterations more efficiently
    total_iterations = sum(
        game_params.get('num_game_env', 0)  # Directly get the number of environments per game
        for game_params in games.values()
    ) * len(envs) * len(agents)  # Multiply by the number of environments and agents

    # Initialize a single progress bar
    with tqdm(total=total_iterations, desc="Total Progress") as pbar:
        for env_name, env_params in envs.items():
            for agent_name, agent_params in agents.items():
                for game_name, game_params in games.items():

                    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                    config_dir = os.path.join(base_dir, 'Data', 'Configs', game_params.get('config_id', None))

                    # Load all config files from config_ID collection
                    json_file_paths = []
                    for file_name in sorted(os.listdir(config_dir)):  # Sort the file names alphabetically
                        if fnmatch.fnmatch(file_name, "config*.json"):  # Match files like config*.json
                            json_file_paths.append(os.path.join(config_dir, file_name))

                    num_game_env = game_params.get('num_game_env', 0)
                    if num_game_env > len(json_file_paths):
                        experiment_logger.warning(
                            f"Number of game environments exceeds the number of config files in the dataset, "
                            f"setting num_game_env to {len(json_file_paths)}."
                        )
                        num_game_env = len(json_file_paths)

                        # Dynamically recalculate and update `pbar.total`
                        adjusted_iterations = sum(num_game_env for game_params in games.values()
                            ) * len(envs) * len(agents)
                        pbar.total = adjusted_iterations
                        pbar.refresh()  # Refresh to reflect the updated total

                    config_file_paths = json_file_paths[:num_game_env]  # Limit to num_game_env

                    # Iterate through config files and update progress
                    for config_file_path in config_file_paths:

                        # Construct the subdirectory name
                        json_base_name = os.path.splitext(os.path.basename(config_file_path))[0]
                        episode_name = f"episode_{agent_name}_{game_name}_{env_name}_{json_base_name}"
                        episode_path = os.path.join(experiment_dir,'Episodes', episode_name)
                        os.makedirs(episode_path, exist_ok=True)

                        if episode_name in state["completed"]:
                            experiment_logger.info(f"Skipping completed episode: {episode_name}")
                            continue  # Skip if already completed

                        # Move the JSON and image files to the experiment path using the new utility function
                        log_separator(episode_name, char="-")
                        util.copy_json_to_experiment(config_file_path, episode_path)

                        # Create a dictionary to save envs, agents, and games data
                        metadata = {
                            "env": {env_name: env_params},
                            "agent": {agent_name: agent_params},
                            "game": {game_name: game_params}
                        }

                        # Save the metadata into a JSON file in the episode_path
                        metadata_file_path = os.path.join(episode_path, 'metadata.json')
                        with open(metadata_file_path, 'w') as metadata_file:
                            json.dump(metadata, metadata_file, indent=4)

                        # Set up logging for the episode
                        episode_logger = setup_episode_logging(episode_path, episode_name)

                        config = init_env(env_params, episode_path, episode_logger)
                        agent = init_agent(agent_params, episode_path, config, episode_logger)
                        game = init_game(game_params, episode_path, episode_logger)

                        try:
                            episode_logger.info(f"Running episode: {episode_name}")
                            # Set up environment
                            setup_config_file = util.load_single_json_from_directory(episode_path)
                            message_data = {
                                "command": "Setup",
                                "from": network_id,
                                "to": partner_id,
                                "messages": [json.dumps(setup_config_file)],
                                "payload": base64.b64encode(b"nothing here").decode("utf-8"),
                            }
                            await websocket.send(json.dumps(message_data))

                            # Run the client
                            experiment_logger.info(f"Start Game with agent: {agent_name}, game: {game_name}, env: {env_name}, config: {config.get('config_instance_id', [])}")
                            episode_logger.info(f"Completed episode: {episode_name}")
                            await action_perception_loop(websocket, network_id, partner_id, agent, game, episode_logger)
                            state["completed"].append(episode_name)
                            save_checkpoint(experiment_id, state)
                            experiment_logger.info(f"Episode {episode_name} completed successfully.")


                        except Exception as e:
                            # Handle any errors that occur within the action-perception loop
                            experiment_logger.error(f"An error occurred during the action-perception loop: {e}")
                            episode_logger.error(f"Error during episode {episode_name}: {e}")
                            raise  # Re-raise the exception to propagate it after logging

                        pbar.update(1)


    log_separator(f"End of Experiment Loop.")
    await websocket.close()
    experiment_logger.info(f"Experiment {experiment_id} completed.")
    return experiment_id


if __name__ == "__main__":
    # Load parameters from the JSON file
    params = util.load_params_from_json('params_experiment_ICML.json')

    # Run the experiment
    experiment_id = asyncio.run(run_experiment(
        games=params.get('games', {}),
        agents=params.get('agents', {}),
        envs=params.get('envs', {}),
        experiment_id=params.get('experiment_id', None))
    )
    logging.info(f"Experiment {experiment_id} finished.")
    print(f"Finished running experiments for experiment ID: {experiment_id}")