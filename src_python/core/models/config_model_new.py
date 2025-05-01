import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np


class ConfigModel:
    def __init__(
        self,
        config_instance_id: str,
        experiment_type: str,
        complexity_c1: int,
        complexity_c2: int,
        grid_size: int,
    ):
        self.config_instance_id = config_instance_id
        self.experiment_type = experiment_type
        self.complexity_c1 = complexity_c1
        self.complexity_c2 = complexity_c2
        self.grid_size = grid_size
        self.payload: Dict[str, Any] = {}

    def add(self, value: Any, key: str):
        """Add a data field to the config. Converts NumPy arrays to lists if needed."""
        if isinstance(value, np.ndarray):
            self.payload[key] = value.tolist()
        else:
            self.payload[key] = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "config_instance_id": self.config_instance_id,
            "experiment_type": self.experiment_type,
            "complexity_c1": self.complexity_c1,
            "complexity_c2": self.complexity_c2,
            "grid_size": self.grid_size,
            "data": self.payload,
        }

    def save_to_json(self, dest_dir: Path):
        dest_dir.mkdir(parents=True, exist_ok=True)
        file_path = dest_dir / f"{self.config_instance_id}.json"
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        return file_path


# Example usage
if __name__ == "__main__":
    config = ConfigModel(
        config_instance_id="ICML_b_4_g_2_c1_2_c2_0_i_3",
        experiment_type="SlidingGeomPuzzle",
        complexity_c1=2,
        complexity_c2=0,
        grid_size=4,
    )

    # Sample data
    config.add(np.array([[1, 0, 2], [2, 0, 3]]), key="start_state")
    config.add(np.array([[1, 0, 5], [2, 0, 6]]), key="goal_state")
    config.add([{"type": "cube", "color": "red"}, {"type": "pyramid", "color": "blue"}], key="geom_sample")
    config.add({"move": True, "flip": True}, key="action_set")
    config.add(["move 0 up", "flip 1 right"], key="optimal_path")

    saved_path = config.save_to_json(Path("./test_output"))
    saved_path
