import os
import json

class GameSystem:

    def __init__(self, experiment_path):
        """
        Initialize the GameSystem.
        Args:
            experiment_path (str): The path where the log files will be saved.
        """
        self.experiment_path = experiment_path
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

    def feed_sim_response(self, sim_message):
        """
        Process a response from the simulation.
        Args:
            sim_message (str or dict): The message from the simulation.
        """
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



class InteractivePuzzle(GameSystem):

    def __init__(self, experiment_id, representation_type, planning_steps, max_game_length):
        super().__init__(experiment_id)
        self.representation_type = representation_type
        self.planning_steps = planning_steps
        self.max_game_length = max_game_length


class SceneUnderstanding(GameSystem):

    def __init__(self, experiment_id):
        super().__init__(experiment_id)