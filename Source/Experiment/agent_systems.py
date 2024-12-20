import base64
import requests
import io
import os
from anthropic import Anthropic
import google.generativeai as genai
from abc import ABC, abstractmethod
import re
from PIL import Image


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


class AIAgent(Agent):
    def __init__(self, move_sequence):
        self.move_sequence = move_sequence
        print("!")

    def act(self, observation):
        if not self.move_sequence:
            return "path empty"
        else:
            return self.move_sequence.pop(0)


class UserAgent(Agent):
    """
    A simple interactive agent that simulates the role of an LLM for user interaction.

    Instead of generating responses automatically, it prompts the user for manual input
    and returns that input as the action.
    """

    def __init__(self):
        pass

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
            self.system_prompt2 = f.read()

        # Add COT instruction if needed
        if COT:
            self.system_prompt2 += ("\nPlease explain your reasoning, then end with 'description: <your object coordinate list>',"
                                   "no matter what always end with description:<your object coordinate list> (dont add additional character"
                                   "after the word description)")
        else:
            self.system_prompt2 += "\nPlease output only the description, no explanations needed."


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

    def parse_action(self, response, split_at="action:"):
        """Extract action from model response"""
        action = response.strip().lower()
        thoughts=""
        if self.COT:
            thoughts = action.split(split_at)[0].strip()
            action = action.split(split_at)[1].strip()
        return action, thoughts

    def parse_action_rmv_special_chars(self, action):
        """
        Cleans the input string to ensure it is safe to use as part of a file name.

        Args:
            action (str): The input string to parse and clean.

        Returns:
            str: The cleaned string, safe for use in file names.
        """
        # Remove invalid file name characters
        cleaned_action = re.sub(r'[\\/*?:"<>|]', '', action)

        # Replace newlines, tabs, and control characters with spaces
        cleaned_action = re.sub(r'[\r\n\t]', ' ', cleaned_action)

        # Remove other special characters (excluding alphanumeric and spaces)
        cleaned_action = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned_action)

        # Remove leading backslashes or forward slashes
        cleaned_action = re.sub(r'^[\\/]+', '', cleaned_action)

        # Remove trailing single quotes or other special characters
        cleaned_action = cleaned_action.strip("'").strip()

        # Remove extra spaces
        cleaned_action = re.sub(r'\s+', ' ', cleaned_action).strip()

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

## used for debugging claude and gpt
def print_message_structure(messages):
    """
    Print message structure in a clean format, similar to:
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": [IMAGE]},
        ...
    ]
    """
    print("\nmessages=[")
    for msg in messages:
        content = msg['content']
        
        # Handle different content types
        if isinstance(content, list):
            # For messages with image content
            if len(content) == 1 and content[0].get('type') in ['image', 'image_url']:
                content_preview = "[IMAGE]"
            else:
                # For messages with multiple content items
                content_preview = "["
                for item in content:
                    if item['type'] in ['image', 'image_url']:
                        content_preview += "[IMAGE], "
                    elif item['type'] == 'text':
                        content_preview += f"text: '{item['text'][:50]}...', "
                content_preview = content_preview.rstrip(', ') + "]"
        elif isinstance(content, dict):
            # For single image messages
            if content.get('type') in ['image', 'image_url']:
                content_preview = "[IMAGE]"
            else:
                content_preview = str(content)
        else:
            # For simple text messages
            content_preview = f"'{content[:50]}...'" if len(str(content)) > 50 else f"'{content}'"
        
        print(f"    {{\"role\": \"{msg['role']}\", \"content\": {content_preview}}},")
    print("]")

def print_message_structure_gemini(content):
    """
    Print content structure in a clean format for Gemini API, similar to:
    content=[
        "instruction text...",
        [IMAGE],
        "Previous action taken: move_left",
        [IMAGE],
        ...
    ]
    """
    print("\ncontent=[")
    for item in content:
        # Handle different content types
        if isinstance(item, Image.Image):
            content_preview = "[IMAGE]"
        elif isinstance(item, str):
            content_preview = f"'{item[:50]}...'" if len(item) > 50 else f"'{item}'"
        else:
            content_preview = str(item)
        
        print(f"    {content_preview},")
    print("]")

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
        self.max_history = 2  # number of old conversations to keep in memory
        self.chat_history = []
        self.content = []  

    def act(self, observation):
        sceneUnderstanding = False #TODO dirty quick code to manually change agent for scene understanding
        if sceneUnderstanding:
            try:
                print("\n=== Processing Current State ===")
                current_base64 = self.encode_image_from_pil(observation)

                content = [
                    {"type": "text", "text": """In this image you will see the board, describe the board state. Only describe the objects with theird coordinates, don't describe empty fields."""},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{current_base64}"}}
                ]

                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.system_prompt2},
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
                action, thoughts = self.parse_action(response.json()['choices'][0]['message']['content'], split_at='description:')

                print(f"\nGPT-4 Vision suggested action: {action}")
                print(f"GPT-4 Vision thought: {thoughts}")
                return self.parse_action_rmv_special_chars(action)

            except Exception as e:
                print(f"\nError calling OpenAI API: {e}")
                return "error"


        elif isinstance(observation, Image.Image):
            try:
                if self.goal_state is None:
                    return self.process_goal_state(observation)

                print("\n=== Processing Current State ===")
                current_base64 = self.encode_image_from_pil(observation)
                goal_base64 = self.encode_image_from_pil(self.goal_state)
                messages = [{"role": "system", "content": self.system_prompt}]

                # Add history if available
                if self.max_history > 0:
                    for i, prev_exchange in enumerate(self.chat_history[-self.max_history:], 1):
                        prev_image_base64 = self.encode_image_from_pil(prev_exchange['observation'])
                        # User message with image
                        messages.append({
                            "role": "user", 
                            "content": [
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{prev_image_base64}"}}
                            ]
                        })
                        # Assistant response
                        messages.append({
                            "role": "assistant",
                            "content": f"Action: {prev_exchange['response']}"
                        })

                # Add goal state image
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{goal_base64}"}}
                    ]
                })

                # Add current state image
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{current_base64}"}}
                    ]
                })

                # Add instruction text
                messages.append({
                    "role": "user",
                    "content": """The last image shows the current state, and the second to last image shows
                          the goal state. (you are also shown the previous state image(s) and action suggested by you,
                          you can use them to determine the next action) 
                          What action should be taken? (Keep in mind, you are not allowed to have two objects in 
                          the same position)? If you asked for an action and nothing moves (check previous image and action), 
                          that means the action is not allowed, either blocked by another object or out of the board move. 
                          No matter what always end with action: <your action> (dont add additional character after the word action)"""
                })

                print_message_structure(messages) # use it for debugging make sure the input is correct

                payload = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 300
                }

                response = requests.post("https://api.openai.com/v1/chat/completions",
                    headers=self.headers,
                    json=payload
                )

                action, thoughts = self.parse_action(response.json()['choices'][0]['message']['content'])
                # Store the current exchange in history
                self.chat_history.append({
                    "observation": observation,
                    "response": action
                })

                print(f"\nGPT-4 Vision suggested action: {action}")
                print(f"GPT-4 Vision thoughts: {thoughts}")
                return self.parse_action_rmv_special_chars(action)

            except Exception as e:
                print(f"\nError calling OpenAI API: {e}")
                return "error"

        elif isinstance(observation, list) and all(isinstance(item, str) for item in observation):
            observation = '\n'.join(observation)

            try:
                if self.goal_state is None:
                    return self.process_goal_state(observation)

                print("\n=== Processing Current State ===")

                # Build messages with history
                messages = [{"role": "system", "content": self.system_prompt}]
                
                # Add conversation history
                if self.max_history > 0:
                    for i, prev_exchange in enumerate(self.chat_history[-self.max_history:], 1):
                        messages.extend([
                            {"role": "user", "content": f"Previous observation {i}: {prev_exchange['observation']}"},
                            {"role": "assistant", "content": f"Previous action {i}: {prev_exchange['response']}"}
                        ])

                # Add current observation
                current_content = [
                    {"type": "text", "text": f"""The first coordinates show the goal state, and the second coordinates show
                    the current state. What action should be taken (Keep in mind, you are not allowed to have two objects in the same position)?
                    If you asked for an action for an object, and you still see that this object is still in the same position, 
                    that means the action is not allowed, either blocked by another object or out of the board move,
                    The board is 4 by 4, coordinates go from a to d and 1 to 4 but not beyond that (there is no 0, so if you are at position A1,
                     you cannot go down or left, and if you are at position D4, you cannot go up or right).
                    goal state: {self.goal_state} 
                    current state: {observation}
                    no matter what always end with action: <your action> (dont add additional character
                    after the word action) """},
                ]
                messages.append({"role": "user", "content": current_content})

                payload = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 150,
                    "temperature": 0.5 # default is 0
                }
                

                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                print(response.json())
                action, thoughts = self.parse_action(response.json()['choices'][0]['message']['content'])

                # Store the exchange in history
                self.chat_history.append({
                    "observation": observation,
                    "response": action
                })

                return self.parse_action_rmv_special_chars(action)

            except Exception as e:
                print(f"\nError calling OpenAI API: {e}")
                return "error"

class ClaudeAgent(LLMAgent):

    def __init__(self, api_key_file_path, instruction_prompt_file_path, single_images=True, COT=False):
        super().__init__(api_key_file_path, instruction_prompt_file_path, single_images, COT)
        self.client = Anthropic(api_key=self.api_keys['CLAUDE_API_KEY'])
        self.model = "claude-3-5-sonnet-20241022"
        self.max_history = 2  
        self.chat_history = []
        self.content = []  
       
    def act(self, observation):
        if isinstance(observation, Image.Image):
            try:
                if self.goal_state is None:
                    return self.process_goal_state(observation)

                print("\n=== Processing Current State ===")
                current_base64 = self.encode_image_from_pil(observation)
                goal_base64 = self.encode_image_from_pil(self.goal_state)
                messages = []

                # Add history if available
                if self.max_history > 0:
                    for i, prev_exchange in enumerate(self.chat_history[-self.max_history:], 1):
                        prev_image_base64 = self.encode_image_from_pil(prev_exchange['observation'])
                        # Add previous image
                        messages.append({
                            "role": "user",
                            "content": [
                                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": prev_image_base64}}
                            ]
                        })
                        # Add assistant's response
                        messages.append({
                            "role": "assistant",
                            "content": f"Action: {prev_exchange['response']}"
                        })

                # Add goal state image
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": goal_base64}}
                    ]
                })

                # Add current state image
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": current_base64}}
                    ]
                })

                # Add instruction text
                messages.append({
                    "role": "user",
                    "content": """The last image shows the current state, and the second to last image shows
                          the goal state. (you are also shown the previous state image(s) and action suggested by you,
                          you can use them to determine the next action) 
                          What action should be taken? (Keep in mind, you are not allowed to have two objects in 
                          the same position)? If you asked for an action and nothing moves (check previous image and action), 
                          that means the action is not allowed, either blocked by another object or out of the board move. 
                          No matter what always end with action: <your action> (dont add additional character after the word action)"""
                })

                print_message_structure(messages)
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=150,
                    system=self.system_prompt,
                    temperature=0.5,
                    messages=messages
                )

                action, thoughts = self.parse_action(message.content[0].text)
                
                # Store the current exchange in history
                self.chat_history.append({
                    "observation": observation,
                    "response": action
                })
                
                print(f"\nClaude suggested action: {action}")
                print(f"\nClaude suggested thoughts: {thoughts}")
                return self.parse_action_rmv_special_chars(action)

            except Exception as e:
                print(f"\nError calling Claude API: {e}")
                return "error"

        elif isinstance(observation, list) and all(isinstance(item, str) for item in observation):
            
            observation = '\n'.join(observation)
            try:
                if self.goal_state is None:
                    return self.process_goal_state(observation)  
                print("\n=== Processing Current State ===")
                messages = []


                if self.max_history > 0:
                    for i, prev_exchange in enumerate(self.chat_history[-self.max_history:], 1):
                        messages.extend([
                            {"role": "user", "content": f"Previous observation {i}: {prev_exchange['observation']}"},
                            {"role": "assistant", "content": f"Previous action {i}: {prev_exchange['response']}"}
                        ])
                current_content = [
                    {"type": "text", "text": f"""The first coordinates show the goal state, and the second coordinates show
                    the current state. What action should be taken (Keep in mind, you are not allowed to have two objects in the same position)?
                    If you asked for an action for an object, and you still see that this object is still in the same position, 
                    that means the action is not allowed, either blocked by another object or out of the board move,
                    The board is 4 by 4, coordinates go from a to d and 1 to 4 but not beyond that (there is no 0, so if you are at position A1,
                     you cannot go down or left, and if you are at position D4, you cannot go up or right).
                    goal state: {self.goal_state} 
                    current state: {observation}
                    no matter what always end with action: <your action> (dont add additional character
                    after the word action) """},
                ]

                messages.append({"role": "user", "content": current_content})

                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=150,
                    system=self.system_prompt,
                    temperature=0.5,  # maybe needs too be tuned
                    messages= messages
                )

                action,thoughts = self.parse_action(message.content[0].text)
                self.chat_history.append({
                    "observation": observation,
                    "response": action
                })
                print(f"\nClaude suggested action: {action}")
                print(f"\nClaude suggested action: {thoughts}")
                return self.parse_action_rmv_special_chars(action) 

            except Exception as e:
                print(f"\nError calling Claude API: {e}")
                return "error"
            
class GeminiAgent(LLMAgent):
    def __init__(self, api_key_file_path, instruction_prompt_file_path, single_images=True, COT=False):
        super().__init__(api_key_file_path, instruction_prompt_file_path, single_images, COT)
        self.api_key = self.api_keys['GEMINI_API_KEY']
        print(self.api_keys['GEMINI_API_KEY'])
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name="models/gemini-2.0-flash-exp", system_instruction=self.system_prompt)
        self.max_history = 2
        self.chat_history = []
        self.content = [] 

    def act(self, observation):

        if isinstance(observation, Image.Image):
            try:
                if self.goal_state is None:
                    return self.process_goal_state(observation)

                print("\n=== Processing Current State ===")
                
                # Initialize content list for Gemini
                messages = []
                
                # Add history if available
                if self.max_history > 0:
                    for prev_exchange in self.chat_history[-self.max_history:]:
                        # Add previous image and its response to content
                        messages.extend([
                            prev_exchange['observation'],
                            f"Previous action: {prev_exchange['response']}"
                        ])

                # Add goal and current state images
                messages.extend([
                    self.goal_state,  # Goal state image
                    observation,      # Current state image
                ])

                # Add instruction text
                instruction = """The last image shows the current state, and the second to last image shows
                        the goal state. (you are also shown the previous state image(s) and action suggested by you,
                        you can use them to determine the next action) 
                        What action should be taken? (Keep in mind, you are not allowed to have two objects in 
                        the same position)? If you asked for an action and nothing moves (check previous image and action), 
                        that means the action is not allowed, either blocked by another object or out of the board move. 
                        No matter what always end with action: <your action> (dont add additional character after the word action)"""
            
                messages.extend([instruction])
                print_message_structure_gemini(messages) # use it for debugging make sure the input is correct

                # Generate response using Gemini
                response = self.model.generate_content(messages)
                
                action, thoughts = self.parse_action(response.text)
                
                # Store the current exchange in history
                self.chat_history.append({
                    "observation": observation,
                    "response": action
                })
            
                print(f"\nGemini suggested action: {action}")
                print(f"\nGemini suggested thoughts: {thoughts}")
                return self.parse_action_rmv_special_chars(action)

            except Exception as e:
                print(f"\nError calling Gemini API: {e}")
                return "error"
            
        elif isinstance(observation, list) and all(isinstance(item, str) for item in observation):
            
            observation = '\n'.join(observation)
            try:
                if self.goal_state is None:
                    return self.process_goal_state(observation)  
                print("\n=== Processing Current State ===")

                if self.max_history > 0:
                    history_context = ""
                    for prev_exchange in self.chat_history[-self.max_history:]:
                        history_context += f"Previous observation: {prev_exchange['observation']}\n"
                        history_context += f"Previous action: {prev_exchange['response']}\n\n"
                
                content = [f"""{history_context if self.max_history > 0 else ''}
                    The first coordinates show the goal state, and the second coordinates show
                    the current state. What action should be taken (Keep in mind, you are not allowed to have two objects in the same position)?
                    The board is 4 by 4, coordinates go from a to d and 1 to 4 but not beyond that.
                    goal state: {self.goal_state} 
                    current state: {observation}
                    no matter what always end with action: <your action> (dont add additional character
                    after the word action) """
                ]

                response = self.model.generate_content(content)
                print(response.text)
                action, thoughts = self.parse_action(response.text)
                self.chat_history.append({
                    "observation": observation,
                    "response": action
                    })

                print(f"\nGemini suggested action: {action}")
                print(f"\nGemini suggested action: {thoughts}")
                return self.parse_action_rmv_special_chars(action) 

            except Exception as e:
                print(f"\nError calling Gemini API: {e}")
                return "error"
            