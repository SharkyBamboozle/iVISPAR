import os.path

from pydantic import BaseModel, Field
from src_python.core.utility.json_file_handler import JsonFileHandler

class ConfigModel(BaseModel):

    def __init__(self):
        self.episode_signature = self.generate_episode_signature()

        #TODO: runtime validitdate param file values
        # validate values in config file, e.g. num geoms < board_size**
        # validate json file has all expected parameter
        # check all shape/color values are different and valid

        # TODO: change config ID to include action sets so one can have a unified ID for Geom Puzzles with Rotation and Move
        # TODO: generate example actions to include for instructions

        # TODO: possibly add config number to be able to sort them more effectively? (file name has this issue where 10 and 11 will come first then 1, 2, 3

    def generate_episode_signature(self):
        pass

    def encode_config_to_json(self):
        json = None
        return json

    def save_to_json(self, episode_dir):
        json = self.encode_config_to_json()
        file_path = os.path.join(self.episode_signature, episode_dir)
        JsonFileHandler.save_to_json(json, file_path)


import json
from typing import List, Dict

class Landmark:
    def __init__(self, geom_nr: int, body: str, color: str, start_coordinate: List[int], goal_coordinate: List[int]):
        self.geom_nr = geom_nr
        self.body = body
        self.color = color
        self.start_coordinate = start_coordinate
        self.goal_coordinate = goal_coordinate

    def to_dict(self):
        return {
            "geom_nr": self.geom_nr,
            "body": self.body,
            "color": self.color,
            "start_coordinate": self.start_coordinate,
            "goal_coordinate": self.goal_coordinate,
        }

class ConfigModel:
    def __init__(self, config_instance_id: str, experiment_type: str, complexity_c1: int, complexity_c2: int, grid_size: int):
        self.config_instance_id = config_instance_id
        self.experiment_type = experiment_type
        self.complexity_c1 = complexity_c1
        self.complexity_c2 = complexity_c2
        self.grid_size = grid_size
        self.landmarks: List[Landmark] = []

    def add_landmark(self, geom_nr: int, body: str, color: str, start_coordinate: List[int], goal_coordinate: List[int]):
        landmark = Landmark(geom_nr, body, color, start_coordinate, goal_coordinate)
        self.landmarks.append(landmark)

    def to_dict(self):
        return {
            "config_instance_id": self.config_instance_id,
            "experiment_type": self.experiment_type,
            "complexity_c1": self.complexity_c1,
            "complexity_c2": self.complexity_c2,
            "grid_size": self.grid_size,
            "landmarks": [landmark.to_dict() for landmark in self.landmarks]
        }

    def save_to_json(self, filename: str):
        with open(filename, 'w') as json_file:
            json.dump(self.to_dict(), json_file, indent=4)

if __name__ == "__main__":
    # Example usage
    config = ConfigModel(
        config_instance_id="ICML_b_4_g_2_c1_2_c2_0_i_3",
        experiment_type="SlidingGeomPuzzle",
        complexity_c1=2,
        complexity_c2=0,
        grid_size=4
    )

    config.add_landmark(geom_nr=1, body="pyramid", color="blue", start_coordinate=[0, 3], goal_coordinate=[0, 3])
    config.add_landmark(geom_nr=2, body="cylinder", color="blue", start_coordinate=[1, 3], goal_coordinate=[3, 3])

    config.save_to_json("config_example.json")
