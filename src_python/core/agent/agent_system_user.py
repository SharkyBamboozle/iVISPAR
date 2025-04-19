from .agent_systems import Agent

class UserAgent(Agent):
    """
    A simple interactive agent that simulates the role of an LLM for user interaction.

    Instead of generating responses automatically, it prompts the user for manual input
    and returns that input as the action.
    """

    def act(self, observation):
        """
        Simulates the process of responding to an observation by asking for user input.

        Args:
            observation (str): A placeholder for the environment's observation. It is not used
                               for decision-making in this class, but passed for compatibility
                               with LLM-style interfaces.

        Returns:
            str: The user's input, simulating the action.
        """
        # Get user input (no validation)
        action = input("Enter action: ").strip()

        return action