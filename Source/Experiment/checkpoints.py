import json
import os
import logging
import shutil
from datetime import datetime


def save_checkpoint(experiment_id, checkpoint_state):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    experiment_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id)
    os.makedirs(os.path.dirname(experiment_dir), exist_ok=True)
    experiment_checkpoint_file = os.path.join(experiment_dir, 'experiment_checkpoint.json')
    with open(experiment_checkpoint_file, 'w') as f:
        json.dump(checkpoint_state, f, indent=4)  # Pretty-print with 4-space indentation
    logging.info(f"Saved checkpoint {experiment_checkpoint_file}")


def load_checkpoint(experiment_id):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    experiment_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id)
    experiment_checkpoint_file = os.path.join(experiment_dir, 'experiment_checkpoint.json')
    if os.path.exists(experiment_checkpoint_file):
        logging.info(f"Load checkpoint {experiment_checkpoint_file}")
        with open(experiment_checkpoint_file, 'r') as f:
            return json.load(f)
    else:
        logging.info(f"No checkpoint file found")
        return None


def remove_incomplete_episode(experiment_id, checkpoint_state):
    """
    Removes any incomplete episode directories that are not marked as completed
    in the checkpoint state and stores information about removed episodes.

    Args:
        experiment_id (str): The ID of the experiment to clean up.
        checkpoint_state (dict): The current checkpoint state with completed episodes.
    """
    logging.info("Checking for incomplete episodes.")
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    experiment_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id, 'Episodes')
    os.makedirs(experiment_dir, exist_ok=True)

    # List all episode directories in the experiment folder
    all_episode_dirs = [
        d for d in os.listdir(experiment_dir)
        if os.path.isdir(os.path.join(experiment_dir, d))
    ]

    # Get the list of completed episodes from the checkpoint state
    completed_episodes = checkpoint_state.get("completed", [])
    removed_episodes = checkpoint_state.setdefault("removed", {})
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
            num_removed_episodes +=1
            logging.info(f"Removing incomplete episode {num_removed_episodes}: {episode_dir}")
            shutil.rmtree(episode_path)
    if num_removed_episodes == 0:
        logging.info("No incomplete episode found.")

    # Save the updated checkpoint state
    save_checkpoint(experiment_id, checkpoint_state)

    logging.info("Incomplete episode cleanup complete.")
