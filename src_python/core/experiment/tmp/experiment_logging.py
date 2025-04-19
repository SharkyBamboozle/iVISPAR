import os
import logging

def setup_episode_logging(episode_dir, episode_name):
    """
    Sets up a dedicated logger for each episode.

    Args:
        episode_dir (str): Directory to save the episode log file.
        episode_name (str): Name of the episode (used for log file naming).
    """
    # Create unique log file for the episode
    episode_log_file = os.path.join(episode_dir, f'episode_log.log')

    # Set up logger
    logger = logging.getLogger(episode_name)
    logger.setLevel(logging.INFO)

    # Prevent propagation to parent loggers (like experiment-wide logger)
    logger.propagate = False

    # Avoid duplicate handlers
    if not logger.handlers:
        # File handler for episode log
        file_handler = logging.FileHandler(episode_log_file)
        file_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_format)

        # Add handler to logger
        logger.addHandler(file_handler)
        logger.info(f"Started logging for episode: {episode_name}")

    return logger


def setup_experiment_logging(experiment_id):
    # Create a log directory if it doesn't exist
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    experiment_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id)

    # Define log file path
    log_file = os.path.join(experiment_dir, f"experiment_log.log")

    # Set up root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all logs at DEBUG level for the file

    # File handler - logs everything to the file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)  # File logs capture all levels
    file_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_format)

    # Console handler - restricts logs shown in the terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only show WARNING and above in terminal
    console_format = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(console_format)

    # Attach handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def log_separator(title, char="#", length=30, logger=None):
    """
    Logs a visually distinct separator with a title to improve log readability.

    Args:
        title (str): The section title to include in the separator.
        char (str): The character used to create the separator line (default: '#').
        length (int): The length of the separator line (default: 30).
    """
    separator_line = char * length
    formatted_title = f"{char * 4} {title} {char * 4}"

    if logger:
        logger.info("\n%s\n%s\n%s\n", separator_line, formatted_title, separator_line)
    else:
        logging.info("\n%s\n%s\n%s\n", separator_line, formatted_title, separator_line)
