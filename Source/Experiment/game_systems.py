import os
import json
from PIL import Image
import base64

class GameSystem:

    def __init__(self, experiment_path, instruction_prompt_file_path, chain_of_thoughts, representation_type, predict_board_state):
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

        self.representation_type = representation_type
        self.predict_board_state = predict_board_state
        self.is_done = False
        self.agent_message_log = []
        self.sim_message_log = {}  # Changed to a dictionary

    def feed_agent_response(self, agent_message):
        """
        Add an agent message to the log.
        Args:
            agent_message (str): The message from the agent.
        """

        self.agent_message_log.append(agent_message)

    def feed_sim_response(self, response, i): #TODO make this i step number internal param of game
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
                self.is_done = sim_message.get("game_done", False)
                step_key = f"step {i}"  # Create the step key as "step 1", "step 2", etc.
                self.sim_message_log[step_key] = sim_message  # Add the message to the log
            else:
                print("Invalid simulation message format. Must be a dictionary after parsing.")
        except json.JSONDecodeError as e:
            print(f"Error decoding simulation message: {e}")

        encoded_data = response.get("payload")
        observation = base64.b64decode(encoded_data)
        image = Image.frombytes('RGBA', (1200, 900), observation, 'raw')
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        if i==0:
            color = (100,191,106) #"green"
        else:
            color = (82, 138, 174) #"blue"
        image_colored = self.color_code_observation(image.copy(), color)

        filename = os.path.join(self.obs_dir, f"obs_{i}")

        # Save the image as a PNG file
        try:
            image_path = f"{filename}.png"
            image_colored.save(image_path)  # Save the image as a PNG
        except Exception as e:
            print(f"Error saving image to {filename}.png: {e}")

        current_board_state = ""
        if isinstance(sim_message, dict):
            # Extract the board state
            current_board_state = sim_message.get("board_state", [])

            # Save the board state as a JSON file
            try:
                json_path = f"{filename}.json"
                with open(json_path, 'w') as f:
                    json.dump(current_board_state, f, indent=4)
            except Exception as e:
                print(f"Error saving board state to {filename}.json: {e}")

        return current_board_state if self.representation_type=='text' else image_colored


    def check_done(self, response):
        """
        Check if the game system is done.
        Returns:
            bool: True if the game is done, False otherwise.
        """
        sim_message = response.get("messages")[0]
        print(sim_message)
        sim_message_dict = json.loads(sim_message)  # Convert JSON string to dict
        self.is_done = sim_message_dict.get("game_done", False)

        if self.is_done:
            self._save_logs() #TODO rather make this explicit
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
        except IOError as e:
            print(f"Error saving agent log: {e}")

        # Save sim message log as a JSON file
        sim_message_log_path = os.path.join(self.experiment_path, "sim_message_log.json")
        try:
            with open(sim_message_log_path, "w") as log_file:
                json.dump(self.sim_message_log, log_file, indent=4)
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

    def __init__(self, experiment_id, instruction_prompt_file_path, chain_of_thoughts, representation_type, planning_steps, max_game_length,predict_board_state):
        super().__init__(experiment_id, instruction_prompt_file_path, chain_of_thoughts, representation_type, predict_board_state)
        self.planning_steps = planning_steps
        self.max_game_length = max_game_length
        self.iteration = 0

    def check_done(self, response):
        is_done = super().check_done(response)
        reached_max_steps =  self.iteration >= self.max_game_length

        return is_done or reached_max_steps


    def feed_sim_response(self, response, i):
        # Call the parent method to do all the processing
        result = super().feed_sim_response(response, i)

        # Add additional logic
        self.iteration = i

        return result

class SceneUnderstanding(GameSystem):

    def __init__(self, experiment_id, instruction_prompt_file_path, chain_of_thoughts):
        super().__init__(experiment_id, instruction_prompt_file_path, chain_of_thoughts, representation_type='vision', predict_board_state=True)

    def feed_sim_response(self, response, i):
        # Call the parent method to do all the processing
        result = super().feed_sim_response(response, i)

        # Add additional logic
        self.is_done = True

        return result