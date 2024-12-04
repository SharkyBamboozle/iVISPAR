import os
import json
from PIL import Image
import base64

class GameSystem:

    def __init__(self, experiment_path, instruction_prompt_file_path, chain_of_thoughts):
        """
        Initialize the GameSystem.
        Args:
            experiment_path (str): The path where the log files will be saved.
        """
        self.experiment_path = experiment_path
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        instruction_prompt_file_path = os.path.join(base_dir, instruction_prompt_file_path)
        with open(instruction_prompt_file_path, 'r') as f:
            self.instruction_prompt = f.read()

        # Create the 'obs' subdirectory inside the save path
        self.obs_dir = os.path.join(experiment_path, 'obs')
        os.makedirs(self.obs_dir, exist_ok=True)

        # Add COT instruction if needed
        if chain_of_thoughts:
            self.instruction_prompt += ("\nPlease explain your reasoning, then end with 'action: <your action>',"
                                   "no matter what always end with action: <your action> (dont add additional character"
                                   "after the word action)")
        else:
            self.instruction_prompt += "\nPlease output only the action, no explanations needed."

        self.is_done = False
        self.agent_message_log = []
        self.sim_message_log = []

    def feed_agent_response(self, agent_message):
        """
        Add an agent message to the log.
        Args:
            agent_message (str): The message from the agent.
        """
        self.agent_message_log.append(agent_message)

    def feed_sim_response(self, response, i):
        """
        Process a response from the simulation.
        Args:
            sim_message (str or dict): The message from the simulation.
        """

        sim_message = response.get("messages")[0]
        try:
            # Check if sim_message is a string and parse it as JSON
            if isinstance(sim_message, str):
                sim_message = json.loads(sim_message)

            if isinstance(sim_message, dict):
                self.sim_message_log.append(sim_message)
                self.is_done = sim_message.get("game_done", False)
            else:
                print("Invalid simulation message format. Must be a dictionary after parsing.")
        except json.JSONDecodeError as e:
            print(f"Error decoding simulation message: {e}")

        encoded_data = response.get("payload")
        observation = base64.b64decode(encoded_data)
        image = Image.frombytes('RGBA', (1200, 900), observation, 'raw')
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        if response.get("command") == "Screenshot":
            color = (100,191,106) #"green"
        else:
            color = (82, 138, 174) #"blue"
        image_colored = self.color_code_observation(image.copy(), color)

        if response.get("command") == "Screenshot":
            filename = os.path.join(self.obs_dir, f"obs_0_goal.png")
        else:
            filename = os.path.join(self.obs_dir, f"obs_{i}_{self.agent_message_log[-1]}.png")
        image_colored.save(filename)  # Save the image as a PNG

        return image_colored


    def check_done(self):
        """
        Check if the game system is done.
        Returns:
            bool: True if the game is done, False otherwise.
        """
        if self.is_done:
            self._save_logs()
        return self.is_done


    def end_game(self):
        """
        End the game, append an ending message, and save logs.
        """
        #self.sim_message_log.append({"message": "Game was ended, possibly due to running out of steps"})
        self._save_logs()


    def _save_logs(self):
        """
        Save the agent message log to a text file and the sim message log to a JSON file.
        """
        os.makedirs(self.experiment_path, exist_ok=True)

        # Save agent message log as a simple text file
        agent_message_log_path = os.path.join(self.experiment_path, "agent_message_log.txt")
        try:
            with open(agent_message_log_path, "w") as log_file:
                log_file.write("\n".join(self.agent_message_log))
            print(f"Agent log saved successfully to {agent_message_log_path}")
        except IOError as e:
            print(f"Error saving agent log: {e}")

        # Save sim message log as a JSON file
        sim_message_log_path = os.path.join(self.experiment_path, "sim_message_log.json")
        try:
            with open(sim_message_log_path, "w") as log_file:
                json.dump(self.sim_message_log, log_file, indent=4)
            print(f"Simulation log saved successfully to {sim_message_log_path}")
        except IOError as e:
            print(f"Error saving simulation log: {e}")


    def color_code_observation(self, observation, background_color):
        """
        Preprocesses an images by removing transparency and setting a solid background.
        """
        background = Image.new('RGB', observation.size, background_color)
        background.paste(observation, mask=observation.getchannel('A') if 'A' in observation.getbands() else None)
        return background



class InteractivePuzzle(GameSystem):

    def __init__(self, experiment_id, instruction_prompt_file_path, chain_of_thoughts, representation_type, planning_steps, max_game_length):
        super().__init__(experiment_id, instruction_prompt_file_path, chain_of_thoughts)
        self.representation_type = representation_type
        self.planning_steps = planning_steps
        self.max_game_length = max_game_length


class SceneUnderstanding(GameSystem):

    def __init__(self, experiment_id):
        super().__init__(experiment_id)