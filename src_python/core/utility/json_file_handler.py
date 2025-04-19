import json
import shutil
import fnmatch
from pathlib import Path
from typing import Any, Dict, Union, List

from .data_path_handler import DataPathHandler


class JsonFileHandler:
    """Utility class for handling JSON files using PathHandler for directory management."""

    @staticmethod
    def load_json(file_signature: str, source_dir: Union[str, Path]) -> Dict[str, Any]:
        """Load JSON data from a file."""
        file_path: Path = Path(DataPathHandler.ensure_dir(source_dir)) / f"{file_signature}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with file_path.open('r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def load_all_jsons(source_dir: Union[str, Path], pattern: str = "*") -> List[Dict[str, Any]]:
        """
        Load all JSON files matching a filename pattern in a directory using the existing load_json() method.

        Args:
            source_dir (Union[str, Path]): The directory to search in.
            pattern (str): Filename pattern to match (e.g., 'config*.json').

        Returns:
            List[Dict[str, Any]]: A list of parsed JSON objects.
        """
        source_path = Path(DataPathHandler.ensure_dir(source_dir))
        matched_files = sorted([
            f for f in source_path.iterdir()
            if fnmatch.fnmatch(f.name, pattern) and f.suffix == ".json"
        ])

        json_objects = []
        for file_path in matched_files:
            file_signature = file_path.stem  # removes .json
            try:
                json_data = JsonFileHandler.load_json(file_signature, source_dir)
                json_objects.append(json_data)
            except Exception as e:
                print(f"Failed to load {file_signature}.json: {e}")

        return json_objects

    @staticmethod
    def save_json(data: Dict[str, Any], file_signature: str, dest_dir: Union[str, Path], overwrite: bool = False) -> None:
        """Save a Python dictionary as a JSON file."""
        file_path: Path = DataPathHandler.ensure_dir(dest_dir) / f"{file_signature}.json"

        try:
            with file_path.open('w' if overwrite else 'x', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except FileExistsError:
            raise FileExistsError(f"File already exists and overwrite=False: {file_path}")

    @staticmethod
    def move_json(file_signature: str, source_type: Union[str, Path], dest_dir: Union[str, Path]) -> Path:
        """Move a JSON file from one directory to another."""
        dir_path: Path = Path(DataPathHandler.ensure_dir(source_type))
        src_file_path: Path = dir_path / f"{file_signature}.json"
        dest_dir_path: Path = Path(dest_dir)
        dest_dir_path.mkdir(parents=True, exist_ok=True)  # Ensure destination directory exists

        if not src_file_path.exists():
            raise FileNotFoundError(f"Source file not found: {src_file_path}")

        dest_file_path: Path = dest_dir_path / f"{file_signature}.json"
        shutil.move(str(src_file_path), str(dest_file_path))
        return dest_file_path

    @staticmethod
    def copy_json(file_signature: str, source_type: Union[str, Path], dest_dir: Union[str, Path]) -> Path:
        """
        Copy a JSON file from one directory to another.

        Args:
            file_signature (str): The name of the file without the `.json` extension.
            source_type (str or Path): The source directory.
            dest_dir (str or Path): The destination directory.

        Returns:
            Path: The path to the copied JSON file in the destination.
        """
        dir_path: Path = Path(DataPathHandler.ensure_dir(source_type))
        src_file_path: Path = dir_path / f"{file_signature}.json"
        dest_dir_path: Path = Path(dest_dir)
        dest_dir_path.mkdir(parents=True, exist_ok=True)

        if not src_file_path.exists():
            raise FileNotFoundError(f"Source file not found: {src_file_path}")

        dest_file_path: Path = dest_dir_path / f"{file_signature}.json"
        shutil.copy2(str(src_file_path), str(dest_file_path))  # copy2 preserves metadata
        return dest_file_path

    @staticmethod
    def encode_json(data: Dict[str, Any]) -> str:
        """Convert a Python dictionary to a JSON-formatted string."""
        return json.dumps(data, indent=4, ensure_ascii=False)  # Preserve UTF-8 characters

    @staticmethod
    def expand_jsons(
        data: List[Dict[str, Any]],
        additional_params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Injects values from additional_params into each config in a list of config dictionaries.

        Args:
            configs (List[Dict]): A list of config dictionaries to expand.
            additional_params (Dict): A dictionary of key-value pairs to merge into each config.

        Returns:
            List[Dict]: The updated list of expanded configs (modified in-place).
        """
        for json_data in data:
            json_data.update(additional_params)
        return data
