from ..utility.json_file_handler import JsonFileHandler


class ExperimentDataModel:
    pass

    @staticmethod
    def save_episode_data(observation, action, observation_new, episode_dir):

        try:
            episode_log = JsonFileHandler.load_json(file_signature="episode_log",
                                                    source_dir=episode_dir)
        except FileNotFoundError:
            episode_log = {}

        new_step_dict = {
            f"step {observation.step_num}": {
                "prompt": observation.system_prompt,
                "observation": observation.board_data,
            }
        }

        episode_log = JsonFileHandler.expand_json(data=episode_log, additional_params=new_step_dict)
        JsonFileHandler.save_json(data=episode_log, file_signature="episode_log", dest_dir=episode_dir, overwrite=True)