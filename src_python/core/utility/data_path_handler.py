from pathlib import Path
from typing import Optional, Union

class DataPathHandler:
    """Handles predefined data directories for experiments and configurations."""

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent

    @staticmethod
    def ensure_dir(subdir_names: Union[str, Path]) -> Path:
        """
        Get or create a directory within the project's fixed `data/` directory.

        Args:
            subdir_names (Union[str, Path]): A string with '/'-separated subdirectories (e.g., 'configs/experiment_42').

        Returns:
            Path: The resolved base directory or subdirectory path.
        """
        # Ensure the input is always a Path object
        subdir_path = Path(subdir_names)

        # Automatically calculate base directory
        dir_path = Path(__file__).resolve().parent.parent.parent.parent / "data" / subdir_path

        # Ensure the directory exists
        dir_path.mkdir(parents=True, exist_ok=True)

        return dir_path


    @staticmethod
    def get_app_builds_dir() -> Path:

        # Automatically calculate base directory
        dir_path = Path(__file__).resolve().parent.parent.parent.parent / "app_builds"

        return dir_path