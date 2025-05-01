import base64
from logging import raiseExceptions

import requests
import io
import os
from anthropic import Anthropic
import google.generativeai as genai
from abc import ABC, abstractmethod
import re
import logging
from PIL import Image, ImageDraw, ImageFont
import experiment_utilities as util

# open source deps
from qwen_vl_utils import process_vision_info
from transformers import AutoProcessor, AutoTokenizer
from vllm import LLM, SamplingParams

DEBUG = False


class LLMAgent:
    """Parent class for LLM-based agents"""

    def __init__(self, episode_path, episode_logger, api_key_file_path, instruction_prompt_file_path,
                 visual_state_embedding='label', single_images=True, COT=False, delay=0, max_history=0):
        self.max_history = max_history
        self.api_keys = load_api_keys(api_key_file_path)
        self.goal_state = None
        self.single_images = single_images
        self.COT = COT
        self.color_codes = util.load_params_from_json('color_codes.json')
        self.visual_state_embedding = visual_state_embedding
        self.episode_logger = episode_logger
        self.delay = delay

        # Create the 'obs' subdirectory inside the save path
        self.obs_dir = os.path.join(episode_path, 'obs')
        os.makedirs(self.obs_dir, exist_ok=True)


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
            self.system_prompt += (
            """
                ## Explain Your Reasoning
                - Before every action, explain your reasoning clearly.
                - At the end of every response, include this line exactly:
                action: <your action>
                - Replace <your action> with the valid move action based on your reasoning.
                - Do not add any characters after the word action.
            """)
        else:
            self.system_prompt += "\nPlease output only the action, no explanations needed."

    def encode_image_from_pil(self, pil_image):
        """Convert PIL Image to base64 string for API consumption."""
        buffer = io.BytesIO()
        pil_image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def process_goal_state(self, observation):
        """Process and store the goal checkpoint_state"""
        self.episode_logger.info("\n=== Receiving Goal State ===")
        self.goal_state = observation
        return "start"


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
def format_message_structure(messages, cutoff=None):
    """
    Format message structure in a clean format, similar to:
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": [IMAGE]},
        ...
    ]

    Args:
        messages (list): List of message dictionaries.
        cutoff (int, optional): Length at which to truncate text. If None, full text is shown.

    Returns:
        str: Formatted string representing the message structure.
    """
    result = ["\nmessages=["]
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
                        text = item['text']
                        if cutoff and len(text) > cutoff:
                            content_preview += f"text: '{text[:cutoff]}...', "
                        else:
                            content_preview += f"text: '{text}', "
                content_preview = content_preview.rstrip(', ') + "]"
        elif isinstance(content, dict):
            # For single image messages
            if content.get('type') in ['image', 'image_url']:
                content_preview = "[IMAGE]"
            else:
                content_preview = str(content)
        else:
            # For simple text messages
            if cutoff and len(str(content)) > cutoff:
                content_preview = f"'{content[:cutoff]}...'"
            else:
                content_preview = f"'{content}'"

        result.append(f"    {{\"role\": \"{msg['role']}\", \"content\": {content_preview}}},")

    result.append("]")

    # Join the list into a single string with line breaks
    return "\n".join(result)


def format_message_structure_gemini(content, cutoff=None):
    """
    Format content structure in a clean format for Gemini API, similar to:
    content=[
        "instruction text...",
        [IMAGE],
        "Previous action taken: move_left",
        [IMAGE],
        ...
    ]

    Args:
        content (list): List of content items, including text and images.
        cutoff (int, optional): Length at which to truncate text. If None, full text is shown.

    Returns:
        str: Formatted string representing the content structure.
    """
    result = ["\ncontent=["]

    for item in content:
        # Handle different content types
        if isinstance(item, Image.Image):
            content_preview = "[IMAGE]"
        elif isinstance(item, str):
            if cutoff and len(item) > cutoff:
                content_preview = f"'{item[:cutoff]}...'"
            else:
                content_preview = f"'{item}'"
        else:
            content_preview = str(item)

        result.append(f"    {content_preview},")

    result.append("]")

    # Join the list into a single string with line breaks
    return "\n".join(result)


class GPT4Agent(LLMAgent):
    def __init__(self, episode_path, episode_logger, api_key_file_path, instruction_prompt_file_path,
                 visual_state_embedding, single_images=True, COT=False, delay=0, max_history=0):
        super().__init__(episode_path, episode_logger, api_key_file_path, instruction_prompt_file_path,
                         visual_state_embedding, single_images, COT, delay, max_history)
        self.api_key = self.api_keys['GPT4_API_KEY']
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.model = "gpt-4o"
        self.chat_history = []
        self.content = []

    def act(self, observation, loop_iteration):
        sceneUnderstanding = False  # TODO dirty quick code to manually change agent for scene understanding
        if sceneUnderstanding:
            try:
                self.episode_logger.info("\n=== Processing Current State ===")
                current_base64 = self.encode_image_from_pil(observation)
                RGB_blue = (82, 138, 174)  # "blue"
                current_base64_colored = self.color_code_observation(current_base64.copy(), RGB_blue)

                content = [
                    {"type": "text",
                     "text": """In this image with blue background you will see the board, describe the board checkpoint_state. Only describe the objects with their coordinates, don't describe empty fields."""},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{current_base64_colored}"}}
                ]

                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": self.system_prompt2},
                        {"role": "user", "content": content}
                    ],
                    "max_tokens": 500
                }

                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=self.headers,
                    json=payload
                )

                action, thoughts = self.parse_action(response.json()['choices'][0]['message']['content'],
                                                     split_at='description:')
                thoughts = self.parse_action_rmv_special_chars(thoughts)
                action = self.parse_action_rmv_special_chars(action)
                self.episode_logger.info(f"\nGPT suggested thoughts: {thoughts}")
                self.episode_logger.info(f"\nGPT suggested action: {action}")

                # Store the current exchange in history
                self.chat_history.append({
                    "observation": observation,
                    "response": action
                })

                return action


            except Exception as e:
                logging.error(f"\nError calling OpenAI API: {e}")
                return "error"


        elif isinstance(observation, Image.Image):
            try:
                if self.goal_state is None:
                    return self.process_goal_state(observation)

                self.episode_logger.info("\n=== Processing Current State ===")

                # Block of code that embeds information what this image represents, e.g. active (current) checkpoint_state, goal checkpoint_state
                # or past checkpoint_state (later). There are several settings we can check for where the information about the
                # checkpoint_state the image represents is marked by color, label, both or none
                if self.visual_state_embedding == 'color':
                    current = self.color_code_observation(observation.copy(),
                                                          tuple(self.color_codes['active_1']['rgb']))
                    goal = self.color_code_observation(self.goal_state.copy(), tuple(self.color_codes['goal_1']['rgb']))
                elif self.visual_state_embedding == 'label':
                    current = self.color_code_observation(observation.copy(),
                                                          tuple(self.color_codes['active_1']['rgb']))
                    goal = self.color_code_observation(self.goal_state.copy(),
                                                       tuple(self.color_codes['active_1']['rgb']))
                    current = self.add_action_text(current.copy(), 'active')
                    goal = self.add_action_text(goal.copy(), 'goal')
                elif self.visual_state_embedding == 'both':
                    current = self.color_code_observation(observation.copy(),
                                                          tuple(self.color_codes['active_1']['rgb']))
                    goal = self.color_code_observation(self.goal_state.copy(), tuple(self.color_codes['goal_1']['rgb']))
                    current = self.add_action_text(current.copy(), 'active')
                    goal = self.add_action_text(goal.copy(), 'goal')
                elif self.visual_state_embedding == 'none':
                    current = self.color_code_observation(observation.copy(),
                                                          tuple(self.color_codes['active_1']['rgb']))
                    goal = self.color_code_observation(self.goal_state.copy(),
                                                       tuple(self.color_codes['active_1']['rgb']))

                current_base64 = self.encode_image_from_pil(current)
                goal_base64 = self.encode_image_from_pil(goal)

                messages = [{"role": "system", "content": self.system_prompt}]

                # Add history if available
                if self.max_history > 0:
                    for i, prev_exchange in enumerate(self.chat_history[-self.max_history:], 1):

                        # Block of code that embeds information what this image represents, here past checkpoint_state.
                        # There are several settings we can check for where the information about the
                        # checkpoint_state the image represents is marked by color, label, both or none
                        if self.visual_state_embedding == 'color':
                            prev_image_colored = self.color_code_observation(prev_exchange['observation'].copy(),
                                                                             tuple(self.color_codes['past']['rgb']))
                        elif self.visual_state_embedding == 'label':
                            prev_image_colored = self.color_code_observation(prev_exchange['observation'].copy(),
                                                                             tuple(self.color_codes['active_1']['rgb']))
                            prev_image_colored = self.add_action_text(prev_image_colored.copy(), 'past')
                        elif self.visual_state_embedding == 'both':
                            prev_image_colored = self.color_code_observation(prev_exchange['observation'].copy(),
                                                                             tuple(self.color_codes['past']['rgb']))
                            prev_image_colored = self.add_action_text(prev_image_colored.copy(), 'past')
                        elif self.visual_state_embedding == 'none':
                            prev_image_colored = self.color_code_observation(prev_exchange['observation'].copy(),
                                                                             tuple(self.color_codes['active_1']['rgb']))

                        prev_image_base64 = self.encode_image_from_pil(prev_image_colored)
                        # User message with image
                        messages.append({
                            "role": "user",
                            "content": [
                                {"type": "image_url",
                                 "image_url": {"url": f"data:image/png;base64,{prev_image_base64}"}}
                            ]
                        })
                        # Assistant response
                        messages.append({
                            "role": "assistant",
                            "content": f"Action: {prev_exchange['response']}"
                        })

                # Add goal checkpoint_state image
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{goal_base64}"}}
                    ]
                })

                # Add current checkpoint_state image
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{current_base64}"}}
                    ]
                })

                # Debug block that saves the images with the colors or text labels into debug_obs to check if
                # The code works correctly
                if DEBUG:
                    parent_dir = os.path.dirname(self.obs_dir)  # Get parent directory of obs_dir
                    debug_dir = os.path.join(parent_dir, 'debug_obs')  # Create debug_obs next to obs_dir

                    os.makedirs(debug_dir, exist_ok=True)

                    filename_obs_current = os.path.join(debug_dir, f"{loop_iteration}_current")
                    # Save the image as a PNG file
                    filepath_obs_current = f"{filename_obs_current}.png"
                    try:
                        current.save(filepath_obs_current)  # Save the image as a PNG
                    except Exception as e:
                        logging.error(f"Error saving image to {filename_obs_current}.png: {e}")

                    filename_obs_goal = os.path.join(debug_dir, f"{loop_iteration}_goal")
                    # Save the image as a PNG file
                    filepath_obs_goal = f"{filename_obs_goal}.png"
                    try:
                        goal.save(filepath_obs_goal)  # Save the image as a PNG
                    except Exception as e:
                        logging.error(f"Error saving image to {filename_obs_goal}.png: {e}")

                    filename_obs_past = os.path.join(debug_dir, f"{loop_iteration}_past")
                    # Save the image as a PNG file
                    filepath_obs_past = f"{filename_obs_past}.png"
                    if self.max_history > 0:
                        for i, prev_exchange in enumerate(self.chat_history[-self.max_history:], 1):
                            try:
                                prev_image_colored.save(filepath_obs_past)  # Save the image as a PNG
                            except Exception as e:
                                logging.error(f"Error saving image to {filename_obs_past}.png: {e}")

                    # Block of code that add to the prompt information what states the images represent,  e.g. active (current)
                    # checkpoint_state, goal checkpoint_state or past checkpoint_state. There are several settings we can check for where the
                    # information about the checkpoint_state the image represents is marked by color, label, both or none
                if self.visual_state_embedding == 'both':
                    text_snippet_active = f"marked with the label {self.color_codes['active_1']['type']} in the image and a {self.color_codes['active_1']['color']} background"
                    text_snippet_goal = f"marked with the label {self.color_codes['goal_1']['type']} in the image and a {self.color_codes['goal_1']['color']} background"
                    text_snippet_past = f"marked with the label {self.color_codes['past']['type']} in the image and a {self.color_codes['past']['color']} background"
                elif self.visual_state_embedding == 'color':
                    text_snippet_active = f" with a {self.color_codes['active_1']['color']} background"
                    text_snippet_goal = f" with a {self.color_codes['goal_1']['color']} background"
                    text_snippet_past = f" with a {self.color_codes['past']['color']} background"
                elif self.visual_state_embedding == 'label':
                    text_snippet_active = f"showing the label in the image {self.color_codes['active_1']['type']}"
                    text_snippet_goal = f"showing the label in the image {self.color_codes['goal_1']['type']}"
                    text_snippet_past = f"showing the label in the image {self.color_codes['past']['type']}"
                elif self.visual_state_embedding == 'none':
                    text_snippet_active = ""
                    text_snippet_goal = ""
                    text_snippet_past = ""
                else:
                    raise ValueError("No viable image checkpoint_state embedding set for agent.")

                # Add instruction text
                messages.append({
                    "role": "user",
                    "content": f"""
                        ## Analyze the Images
                        You can view your current active board checkpoint_state in the last image {text_snippet_active}. Study this image and the objects with their positions carefully.
                        Your goal is to match the goal checkpoint_state, shown in the image {text_snippet_goal}. Study this image and the objects with their positions carefully.

                        ## Additionally, you are provided with:
                        - The previous checkpoint_state image(s) {text_snippet_past}.
                        - Your previous suggested action
                        - Use this information by comparing it to your current active checkpoint_state to determine your next action.

                        ## Invalid Actions:
                        - No Overlap: You are not allowed to position two objects in the same tile.
                        - If the suggested action does not move any objects, it is invalid (e.g., blocked by another object or out of bounds).
                        - Use the previous image(s) and action to understand why it failed and suggest a different action.

                        It is of most importance you always end your response with this exact format:

                        action: move <object color> <object shape> <direction>
                        where you replace <object color> <object shape> <direction> with the valid move action based on your reasoning and do not add any characters after your action.
                """
                })

                formatted_message = format_message_structure(
                    messages)  # use it for debugging make sure the input is correct
                self.episode_logger.info(formatted_message)

                payload = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 500
                }

                response = requests.post("https://api.openai.com/v1/chat/completions",
                                         headers=self.headers,
                                         json=payload
                                         )

                action, thoughts = self.parse_action(response.json()['choices'][0]['message']['content'])
                thoughts = self.parse_action_rmv_special_chars(thoughts)
                action = self.parse_action_rmv_special_chars(action)
                self.episode_logger.info(f"\nGPT suggested thoughts: {thoughts}")
                self.episode_logger.info(f"\nGPT suggested action: {action}")

                # Store the current exchange in history
                self.chat_history.append({
                    "observation": observation,
                    "response": action
                })

                return action

            except Exception as e:
                logging.error(f"\nError calling OpenAI API: {e}")
                return "error"

        elif isinstance(observation, list) and all(isinstance(item, str) for item in observation):
            observation = '\n'.join(observation)

            try:
                if self.goal_state is None:
                    return self.process_goal_state(observation)

                self.episode_logger.info("\n=== Processing Current State ===")

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
                    {"type": "text", "text": f"""
                        ## Analyze the States
                        The goal checkpoint_state is provided as the first set of coordinates: 
                        {self.goal_state}.
                        The current checkpoint_state is provided as the second set of coordinates: 
                        {observation}.
                        Study both states carefully and determine how to move objects in the current checkpoint_state to match the goal checkpoint_state.

                        ## Additionally, you are provided with:
                        - The previous states.
                        - Your previous suggested action
                        - Use this information by comparing it to your current active checkpoint_state to determine your next action.

                        ## Invalid Actions:
                        - No Overlap: You are not allowed to position two objects in the same tile.
                        - If the suggested action does not move any objects, it is invalid (e.g., blocked by another object or out of bounds).
                        - Use the previous image(s) and action to understand why it failed and suggest a different action.

                        It is of most importance you always end your response with this exact format:

                        action: move <object color> <object shape> <direction>
                        where you replace <object color> <object shape> <direction> with the valid move action based on your reasoning and do not add any characters after your action.
                    """}, ]
                messages.append({"role": "user", "content": current_content})

                formatted_message = format_message_structure(messages)
                self.episode_logger.info(formatted_message)

                payload = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 500,
                    "temperature": 0.5  # default is 0
                }

                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=self.headers,
                    json=payload
                )

                action, thoughts = self.parse_action(response.json()['choices'][0]['message']['content'])
                thoughts = self.parse_action_rmv_special_chars(thoughts)
                action = self.parse_action_rmv_special_chars(action)
                self.episode_logger.info(f"\nGPT suggested thoughts: {thoughts}")
                self.episode_logger.info(f"\nGPT suggested action: {action}")

                # Store the exchange in history
                self.chat_history.append({
                    "observation": observation,
                    "response": action
                })

                return action

            except Exception as e:
                logging.error(f"\nError calling OpenAI API: {e}")
                return "error"