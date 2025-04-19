import os
import logging

class LogHandler:
    _loggers = {}  # Dictionary to store loggers by ID

    @staticmethod
    def get_logger(logger_id: str, base_dir: str = None):
        """
        Returns a logger instance for the given logger ID.
        If the logger does not exist, it creates a new one.

        Args:
            logger_id (str): Unique identifier for the logger.
            base_dir (str, optional): Base directory for log storage. Defaults to project root.

        Returns:
            logging.Logger: The logger instance.
        """
        if logger_id in LogHandler._loggers:
            return LogHandler._loggers[logger_id]  # Return existing logger

        # Define log directory and log file path
        if base_dir is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

        log_dir = os.path.join(base_dir, 'Data', 'Experiments', logger_id)
        os.makedirs(log_dir, exist_ok=True)  # Ensure the log directory exists

        log_file = os.path.join(log_dir, f"{logger_id}.log")

        # Create and configure logger
        logger = logging.getLogger(logger_id)
        logger.setLevel(logging.DEBUG)  # Capture all logs at DEBUG level

        # Prevent duplicate handlers in case get_logger() is called multiple times
        if not logger.hasHandlers():
            # File handler - logs everything to a file
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            file_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(file_format)

            # Console handler - restrict logs shown in the terminal
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_format = logging.Formatter("%(levelname)s - %(message)s")
            console_handler.setFormatter(console_format)

            # Attach handlers to the logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)

        # Store logger in the dictionary
        LogHandler._loggers[logger_id] = logger
        return logger
