import os
import shutil
import subprocess
import time
import csv
from datetime import datetime
import base64
import requests
from PIL import Image
import io
from anthropic import Anthropic
import google.generativeai as genai

class UserInteractiveAgent:
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
    
    def __init__(self, single_images=True, COT=False):
        self.goal_state = None
        self.single_images = single_images
        self.COT = COT
        self.system_prompt = """
You are an AI solving a shape puzzle game. Your task is to move objects on the board, 
to match the goal state shown in the image. Study the goal state carefully. Every object can occupy only one tile on the board at a time (so if you try
to ask for an action and nothing moves, that means the action is not allowed; either blocked by another object or our of the board move).
Available actions:
- "move {object color} {object shape} {direction}": Moves an object of a specific color and shape in the specified direction (do not use quotation marks ) 
- "done": Write done when you think the current state matches the goal state (if you write done, and the game does not end, this means that you did not succefully solve it, keep trying)

Colors: green, red, blue
Shapes: cube, ball, pyramid
Directions: up, down, left, right
""" + ("Please explain your reasoning, then end with 'action: <your action>'," 
       "no matter what always end with action: <your action> (dont add additional character"
       "after the word action)" if COT else "Please output only the action, no explanations needed.")
        
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

class GPT4Agent(LLMAgent):
    def __init__(self, single_images=True, COT=False):
        super().__init__(single_images, COT)
        self.api_key = "your_api_key"
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
            return action

        except Exception as e:
            print(f"\nError calling OpenAI API: {e}")
            return "error"

class ClaudeAgent(LLMAgent):
    def __init__(self, single_images=True, COT=False):
        super().__init__(single_images, COT)
        self.client = Anthropic(api_key="your_api_key")
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
                temperature= 0.5, # maybe needs too be tuned
                messages=[{"role": "user", "content": content}]
            )
            
            action = self.parse_action(message.content[0].text)
            print(f"\nClaude suggested action: {action}")
            return action

        except Exception as e:
            print(f"\nError calling Claude API: {e}")
            return "error"

class GeminiAgent(LLMAgent):
    def __init__(self, single_images=True, COT=False):
        super().__init__(single_images, COT)
        self.api_key = "your_api_key"  # Replace with your actual API key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction= self.system_prompt)

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


def run_Unity_executable(executable_path, *args):
    """
    Runs the Unity executable with optional command-line arguments and returns the process handle.

    Args:
        executable_path (str): The path to the Unity executable.
        *args: Optional command-line arguments to pass to the Unity executable.

    Returns:
        process: The subprocess.Popen process handle.
    """
    try:
        # Create the command to run the Unity executable
        command = [executable_path] + list(args)

        # Run the executable using Popen to get a process handle
        process = subprocess.Popen(command)

        print(f"Unity executable '{executable_path}' started.")

        return process  # Return the process handle so we can close it later

    except FileNotFoundError:
        print(f"The file '{executable_path}' was not found.")
        return None


def close_Unity_process(process):
    """
    Terminates the Unity executable process.

    Args:
        process: The process handle of the Unity executable.

    Returns:
        None
    """
    if process:
        process.terminate()  # This will attempt to terminate the process
        process.wait()  # Wait for the process to fully close
        print("Unity executable closed.")
    else:
        print("No process to terminate.")


def load_config_paths(config_dir):
    """
    Loads all JSON config file paths and their corresponding .png image file paths (start and goal) from the given directory.
    Assumes image files have the same base name as the JSON files, with _start.png and _goal.png extensions.

    Args:
        config_dir (str): The path to the directory containing the JSON config and image files.

    Returns:
        tuple: A tuple of two lists:
               - List of file paths to the JSON config files.
               - List of dictionaries with paths to the corresponding start and goal image files.
    """
    # Lists to store file paths
    json_file_paths = []
    image_file_paths = []

    # Iterate over all files in the directory
    for file_name in os.listdir(config_dir):
        # Check if the file has a .json extension
        if file_name.endswith(".json"):
            # Construct the full file path for the JSON file
            json_full_path = os.path.join(config_dir, file_name)
            json_file_paths.append(json_full_path)

            # Construct the corresponding image file paths for start and goal images
            base_name = os.path.splitext(file_name)[0]  # Remove the .json extension
            image_start_full_path = os.path.join(config_dir, base_name + "_start.png")
            image_goal_full_path = os.path.join(config_dir, base_name + "_goal.png")

            # Add the image file paths to the list, as a dictionary for start and goal
            image_file_paths.append({
                'start_image': image_start_full_path,
                'goal_image': image_goal_full_path
            })

    return json_file_paths, image_file_paths



def copy_json_to_unity_resources(json_config_path, unity_executable_path):
    """
    Copies a JSON config file to the Unity executable's Resources folder and renames it to puzzle.json.

    Args:
        json_config_path (str): The path to the JSON configuration file.
        unity_executable_path (str): The path to the Unity executable (e.g., 'D:/RIPPLE EXEC/RIPPLE.exe').

    Returns:
        str: The full path to the copied JSON file in the Resources folder.
    """
    # Construct the path to the Unity Resources folder
    unity_resources_folder = os.path.join(os.path.dirname(unity_executable_path), 'RIPPLE_Data', 'Resources')

    # Ensure the Resources folder exists
    if not os.path.exists(unity_resources_folder):
        raise FileNotFoundError(f"The Resources folder does not exist at: {unity_resources_folder}")

    # Define the destination path for the copied JSON file
    destination_path = os.path.join(unity_resources_folder, 'puzzle.json')

    # Copy and rename the JSON config file to the Resources folder as puzzle.json
    shutil.copy(json_config_path, destination_path)

    return destination_path


def create_experiment_directories(num_game_env, agents):
    """
    Creates a 'data/experiment_ID_{ID}/experiment_{agent_type}_{env_type}_{game_num}' subdirectory for every combination of
    agents and game environments, and for the number of games specified in num_game_env.

    Args:
        num_game_env (dict): A dictionary where keys are environment types and values are the number of games.
        agents (dict): A dictionary where keys are agent types and values are agent instances.

    Returns:
        dict: A dictionary mapping (agent_type, env_type, game_num) to the full path of each experiment directory.
    """
    # Get the current working directory (this should be inside 'source/')
    current_dir = os.getcwd()

    # Get the parent directory of 'source/' (one level up)
    parent_dir = os.path.dirname(current_dir)

    # Define the path for the 'data/' directory (one level above 'source/')
    data_dir = os.path.join(parent_dir, 'data')

    # Ensure the 'data/' directory exists (create it if it doesn't)
    os.makedirs(data_dir, exist_ok=True)

    # Generate a unique ID based on the current date and time (format: YYYYMMDD_HHMMSS)
    experiment_id = datetime.now().strftime("experiment_ID_%Y%m%d_%H%M%S")

    # Create the path for the main experiment directory
    experiment_dir = os.path.join(data_dir, experiment_id)

    # Ensure the experiment directory is created
    os.makedirs(experiment_dir, exist_ok=True)

    # Dictionary to store all created subdirectory paths
    experiment_subdirs = {}

    # Loop over each agent and game environment
    for agent_type, agent in agents.items():
        if agent_type not in experiment_subdirs:
            experiment_subdirs[agent_type] = {}

        for env_type, num_games in num_game_env.items():
            if env_type not in experiment_subdirs[agent_type]:
                experiment_subdirs[agent_type][env_type] = {}

            for game_num in range(1, num_games + 1):
                # Construct the subdirectory name
                subdir_name = f"experiment_{agent_type}_{env_type}_{game_num}"

                # Create the subdirectory path inside the main experiment directory
                subdir_path = os.path.join(experiment_dir, subdir_name)

                # Ensure the subdirectory is created
                os.makedirs(subdir_path, exist_ok=True)

                # Store the path in the nested dictionary
                experiment_subdirs[agent_type][env_type][game_num] = subdir_path

    # Return the dictionary of subdirectory paths
    return experiment_subdirs


def copy_files_to_experiment(json_file_path, image_file_paths, experiment_path):
    """
    Copies the JSON and image files (start and goal) to the specified experiment path.

    Args:
        json_file_path (str): The full path of the JSON file to be copied.
        image_file_paths (dict): A dictionary containing the full paths of the start and goal image files to be copied.
        experiment_path (str): The path to the experiment directory where the files should be copied.
    """
    try:
        # Ensure the experiment directory exists
        if not os.path.exists(experiment_path):
            os.makedirs(experiment_path)

        # Copy the JSON file to the experiment directory
        json_file_dest = os.path.join(experiment_path, os.path.basename(json_file_path))
        shutil.copy(json_file_path, json_file_dest)
        print(f"JSON file copied to {json_file_dest}")

        # Copy the start and goal image files to the experiment directory
        for key, image_file_path in image_file_paths.items():
            image_file_dest = os.path.join(experiment_path, os.path.basename(image_file_path))
            shutil.copy(image_file_path, image_file_dest)
            print(f"{key.replace('_', ' ').capitalize()} copied to {image_file_dest}")

    except Exception as e:
        print(f"Error copying files: {e}")



def save_results_to_csv(experiment_path, i, win):
    """
    Saves the results (i and win) to a CSV file named 'results.csv' in the specified experiment path.

    Args:
        experiment_path (str): The path to the experiment directory where the CSV file should be saved.
        i (int): The number of actions used.
        win (bool): Whether the game was won.
    """
    # Define the path for the CSV file
    csv_file_path = os.path.join(experiment_path, 'results.csv')

    # Check if the file exists to determine whether to write the header
    file_exists = os.path.isfile(csv_file_path)

    # Open the CSV file in append mode
    with open(csv_file_path, mode='a', newline='') as csv_file:
        writer = csv.writer(csv_file)

        # Write the header if the file is new
        if not file_exists:
            writer.writerow(['Game Number', 'Actions Used', 'Win'])

        # Write the result row
        writer.writerow([i, win])

    print(f"Results saved to {csv_file_path}")


from PIL import Image, ImageDraw, ImageFont
import os


def merge_images(single_img_filename, obs_dir, bar_width=40, bar_height=40, text_fraction=0.1):
    """
    Merges two images side by side with a white bar in between, and adds a white bar underneath
    with centered text indicating "Current State" and "Goal State", dynamically adjusting font size.

    Args:
        single_img_filename (str): Path to the first image file.
        obs_dir (str): Directory containing the second image file named "obs_1_init.png".
        bar_width (int): Width of the white bar between the images.
        bar_height (int): Height of the white bar below the images for text labels.
        text_fraction (float): Portion of image width for the text size (0 < text_fraction <= 1).
    """
    # Path to the second image (always named obs_1_init in obs_dir)
    second_image_path = os.path.join(obs_dir, "obs_1_init.png")

    # Load the two images
    img1 = Image.open(single_img_filename)
    img2 = Image.open(second_image_path)

    # Ensure both images have the same height
    if img1.height != img2.height:
        raise ValueError("Both images should have the same height for merging.")

    # Create a new image with width = sum of both image widths + the white bar width
    total_width = img1.width + img2.width + bar_width
    total_height = img1.height + bar_height  # Additional space at the bottom for text labels
    result = Image.new('RGB', (total_width, total_height), (255, 255, 255))  # White background

    # Paste the two images onto the result image
    result.paste(img1, (0, 0))  # Paste the first image on the left
    result.paste(img2, (img1.width + bar_width, 0))  # Paste the second image on the right

    # Draw the text labels on the white bar below the images
    draw = ImageDraw.Draw(result)

    # Text labels
    text_current = "Current State"
    text_goal = "Goal State"

    # Dynamically adjust font size based on image width and text_fraction
    fontsize = 1  # Start with font size 1
    font_path = "arial.ttf"  # Use a default or available TTF font path on your system
    font = ImageFont.truetype(font_path, fontsize)

    # Increase font size until it fits the desired fraction of image width
    while draw.textbbox((0, 0), text_current, font=font)[2] < text_fraction * img1.width:
        fontsize += 1
        font = ImageFont.truetype(font_path, fontsize)

    # Optionally decrease by 1 to ensure it's less than or equal to the desired fraction
    fontsize -= 1
    font = ImageFont.truetype(font_path, fontsize)

    # Calculate text width and position based on the new font size
    current_text_width = draw.textbbox((0, 0), text_current, font=font)[2]  # Use textbbox
    goal_text_width = draw.textbbox((0, 0), text_goal, font=font)[2]  # Use textbbox

    # Calculate text positions to center them below each image
    current_text_x = (img1.width - current_text_width) // 2
    goal_text_x = img1.width + bar_width + (img2.width - goal_text_width) // 2

    text_y = img1.height + (bar_height // 4)  # Adjust text height to be centered in the bar

    # Draw the text labels
    draw.text((current_text_x, text_y), text_current, fill="black", font=font)
    draw.text((goal_text_x, text_y), text_goal, fill="black", font=font)

    # Split the filename and extension
    file_root, file_ext = os.path.splitext(single_img_filename)
    double_img_file_name = f"{file_root}_compare{file_ext}"

    # Save the result back to the output directory with the modified name
    output_path = os.path.join(obs_dir, os.path.basename(double_img_file_name))
    result.save(output_path)

    print(f"Merged image saved to {output_path}")


if __name__ == "__main__":
    # Example usage
    Unity_executable_path = r'D:\RIPPLE EXEC\RIPPLE.exe'

    # Start the Unity executable
    process = run_Unity_executable(Unity_executable_path)

    # Wait for a while (e.g., 10 seconds) before closing it
    time.sleep(10)  # You can replace this with your actual logic to determine when to close it

    # Close the Unity executable
    close_Unity_process(process)
