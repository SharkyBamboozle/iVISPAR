import base64
import requests
import io
import os
from anthropic import Anthropic
import google.generativeai as genai
from abc import ABC, abstractmethod
import re


class Agent(ABC):
    """
    Abstract base class for agents.
    Provides a template for specific agents with standardized methods for interaction.
    """

    @abstractmethod
    def act(self, observation):
        """
        Abstract method to perform an action in the environment.

        Parameters:
            action (any): The action to perform.

        Returns:
            None
        """
        pass


class AStarAgent(Agent):
    def __init__(self, shortest_move_sequence):
        self.shortest_move_sequence = shortest_move_sequence

    def act(self, observation):
        if not self.shortest_move_sequence:
            return "AStar path empty"
        else:
            return self.shortest_move_sequence.pop(0)


class UserAgent:
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


class LLMAgent:
    """Parent class for LLM-based agents"""

    def __init__(self, api_key_file_path, instruction_prompt_file_path, single_images=True, COT=False):
        self.api_keys = load_api_keys(api_key_file_path)
        self.goal_state = None
        self.single_images = single_images
        self.COT = COT

        # Load system prompt from file
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.instruction_prompt_file_path = os.path.join(base_dir, instruction_prompt_file_path)
        with open(self.instruction_prompt_file_path, 'r') as f:
            self.system_prompt = f.read()

        # Add COT instruction if needed
        if COT:
            self.system_prompt += ("\nPlease explain your reasoning, then end with 'action: <your action>',"
                                   "no matter what always end with action: <your action> (dont add additional character"
                                   "after the word action)")
        else:
            self.system_prompt += "\nPlease output only the action, no explanations needed."

    def encode_image_from_pil(self, pil_image):
        """Convert PIL Image to base64 string for API consumption."""
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def process_goal_state(self, observation):
        """Process and store the goal state"""
        print("\n=== Receiving Goal State ===")
        self.goal_state = observation
        return "start"

    def parse_action(self, response):
        """Extract action from model response"""
        action = response.strip().lower()
        if self.COT:
            action = action.split("action:")[1].strip()
        return action

    def parse_action_rmv_special_chars(self, action):
        """
        Removes special characters (like **, __, etc.) from the input string.

        Args:
            action (str): The input string to parse and clean.

        Returns:
            str: The cleaned string with only alphanumeric characters and spaces.
        """
        # Use a regular expression to remove non-alphanumeric characters, except spaces
        cleaned_action = re.sub(r'[^a-zA-Z0-9\s]', '', action)
        return cleaned_action

def load_api_keys(api_key_file_path):
    """Load API keys from file"""
    keys = {}
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    api_key_file_path = os.path.join(base_dir, api_key_file_path)
    with open(api_key_file_path, 'r') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=')
                keys[key] = value
    return keys


class GPT4Agent(LLMAgent):
    def __init__(self, api_key_file_path, instruction_prompt_file_path, single_images=True, COT=False):
        super().__init__(api_key_file_path, instruction_prompt_file_path, single_images, COT)
        print(self.api_keys)
        self.api_key = self.api_keys['GPT4_API_KEY']
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.model = "gpt-4o"

    def act(self, observation):
        try:
            if self.goal_state is None:
                return self.process_goal_state(observation)

            print("\n=== Processing Current State ===")
            current_base64 = self.encode_image_from_pil(observation)

            if self.single_images:
                goal_base64 = self.encode_image_from_pil(self.goal_state)
                content = [
                    {"type": "text", "text": """The first image shows the goal state, and the second image shows
                      the current state. What action should be taken (so if you try to ask for an action and 
                     nothing moves, that means the action is not allowed; either blocked by another object or
                      our of the board move)?"""},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{goal_base64}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{current_base64}"}}
                ]
            else:
                content = [
                    {"type": "text", "text": """In this image you will see two boards, the one on the left is 
                     your current state (written in the bottom of the board) and the one on the right is your
                      goal state(written in the bottom of the board), what action you should take to match the
                      current state to the goal state?"""},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{current_base64}"}}
                ]

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": content}
                ],
                "max_tokens": 150
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.headers,
                json=payload
            )
            print(response.json())
            action = self.parse_action(response.json()['choices'][0]['message']['content'])
            print(f"\nGPT-4 Vision suggested action: {action}")
            return self.parse_action_rmv_special_chars(action)

        except Exception as e:
            print(f"\nError calling OpenAI API: {e}")
            return "error"



class ClaudeAgent(LLMAgent):
    def __init__(self, api_key_file_path, instruction_prompt_file_path, single_images=True, COT=False):
        super().__init__(instruction_prompt_file_path, api_key_file_path, single_images, COT)
        self.client = Anthropic(api_key=self.api_keys['CLAUDE_API_KEY'])
        self.model = "claude-3-5-sonnet-20241022"

    def act(self, observation):
        try:
            if self.goal_state is None:
                return self.process_goal_state(observation)

            print("\n=== Processing Current State ===")
            current_base64 = self.encode_image_from_pil(observation)

            if self.single_images:
                goal_base64 = self.encode_image_from_pil(self.goal_state)
                content = [
                    {"type": "text", "text": "obs_0_init"},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": goal_base64}},
                    {"type": "text", "text": "Current state:"},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": current_base64}},
                    {"type": "text", "text": """What action should be taken to match the goal state? 
                     (Keep in mind. if you ask for an action and nothing moves, that means the action is not allowed;
                      either blocked by another object or out of the board move, if you think all objects match
                      their position with the original, write done, if you write done, and the game continues, 
                     that means the objects are not placed in the correct positions, keep moving pieces around)"""}
                ]
            else:

                content = [
                    {"type": "text", "text": """In this image you will see two boards, the one on the left 
                    is your current state (written in the bottom of the board) and
                    the one on the right is your goal state(written in the bottom of the board).
                    Keep in mind, if you ask for an action and nothing moves,
                    that means the action is not allowed, either blocked by another object or out of the board move,if you think all objects match
                    their position with the original, write done, if you write done, and the game continues, 
                    that means the objects are not placed in the correct positions, keep moving pieces around.
                    what action you should take to match the current state to the goal state?"""},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": current_base64}}
                ]

            message = self.client.messages.create(
                model=self.model,
                max_tokens=150,
                system=self.system_prompt,
                temperature=0.5,  # maybe needs too be tuned
                messages=[{"role": "user", "content": content}]
            )

            action = self.parse_action(message.content[0].text)
            print(f"\nClaude suggested action: {action}")
            return action

        except Exception as e:
            print(f"\nError calling Claude API: {e}")
            return "error"


class GeminiAgent(LLMAgent):
    def __init__(self, api_key_file_path, instruction_prompt_file_path, single_images=True, COT=False):
        super().__init__(api_key_file_path, instruction_prompt_file_path, single_images, COT)
        self.api_key = self.api_keys['GEMINI_API_KEY']
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=self.system_prompt)

    def act(self, observation):
        try:
            if self.goal_state is None:
                return self.process_goal_state(observation)

            print("\n=== Processing Current State ===")
            # Convert PIL images to format expected by Gemini
            current_image = observation

            if self.single_images:
                goal_image = self.goal_state
                content = [
                    """What action should be taken to match the goal state? 
                     (Keep in mind. if you ask for an action and nothing moves, that means the action is not allowed;
                      either blocked by another object or out of the board move, if you think all objects match
                      their position with the original, write done, if you write done, and the game continues, 
                     that means the objects are not placed in the correct positions, keep moving pieces around)""",
                    goal_image,
                    current_image
                ]
            else:
                content = [
                    """In this image you will see two boards, the one on the left 
                    is your current state (written in the bottom of the board) and
                    the one on the right is your goal state(written in the bottom of the board).
                    Keep in mind, if you ask for an action and nothing moves,
                    that means the action is not allowed, either blocked by another object or out of the board move,if you think all objects match
                    their position with the original, write done, if you write done, and the game continues, 
                    that means the objects are not placed in the correct positions, keep moving pieces around.
                    what action you should take to match the current state to the goal state?""",
                    current_image
                ]

            response = self.model.generate_content(content)
            print(response.text)
            action = self.parse_action(response.text)
            print(f"\nGemini suggested action: {action}")
            return action

        except Exception as e:
            print(f"\nError calling Gemini API: {e}")
            return "error"