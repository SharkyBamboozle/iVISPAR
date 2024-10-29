import os
import socket
import time
from PIL import Image

from util_functions import UserInteractiveAgent


def action_perception_loop(user_agent, max_game_length, save_path, HOST="127.0.0.1", PORT=1984):
    """
    Connects to the server via a socket and handles the receiving of observations and sending of actions
    over TCP to simulate the action-perception loop between the Unity environment and the multimodal-LLM.

    Args:
        user_agent (UserInteractiveAgent): The user agent for interacting with the environment.
        max_game_length (int): Maximum number of actions in the game loop.
        save_path (str): The directory path where the observations will be saved.
        HOST (str): The server's hostname or IP address (default is localhost).
        PORT (int): The server's port (default is 1984).

    Returns:
        int, bool: The number of actions performed and whether the game was won.
    """
    # Ensure the save path exists
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Create the 'obs' subdirectory inside the save path
    obs_dir = os.path.join(save_path, 'obs')
    os.makedirs(obs_dir, exist_ok=True)  # Create 'obs' directory if it doesn't exist

    win = False  # Set to true only if Game ends within max_game_length

    # Connect socket to server's hostname or IP address (here localhost) and port used by the server (here Unity)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        observation = s.recv(100 * 1024 * 1024)  # Receive up to 100MB of data

        # Convert the raw bytes to an image RGB or RGBA
        image = Image.frombytes('RGBA', (1200, 900), observation, 'raw')
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        # Save the initial observation image as a PNG inside the 'obs' directory
        filename = os.path.join(obs_dir, "obs_0_init.png")
        image.save(filename)  # Save the image as a PNG
        print(f"Saved image to {filename}")
        time.sleep(1)  # Wait for 1 second

        action = 'start'
        s.sendall(action.encode())

        try:
            for i in range(1, max_game_length + 1):
                # Wait and receive observation data from Unity (blocking call until data arrives)
                observation = s.recv(100 * 1024 * 1024)  # Receive up to 100MB of data

                # Check if the server has closed the connection (observation will be empty)
                if not observation:
                    print("Connection closed by the server.")
                    win = True  # If the connection is closed, assume the game was completed successfully
                    i -= 1
                    break

                # Convert the raw bytes to an image RGB or RGBA
                image = Image.frombytes('RGBA', (1200, 900), observation, 'raw')
                image = image.transpose(Image.FLIP_TOP_BOTTOM)

                # Save the observation image with a sequential filename inside the 'obs' directory
                filename = os.path.join(obs_dir, f"obs_{i+1}_{action}.png")
                image.save(filename)  # Save the image as a PNG
                print(f"Saved image to {filename}")

                # Process the observation using the user_agent
                action = user_agent.act(image)
                s.sendall(action.encode())  # Send action encoded as bits back to Unity
                time.sleep(1)  # Wait for 1 second

        except (ConnectionResetError, ValueError, socket.error, BrokenPipeError) as e:
            print("Connection error or game ended prematurely:", e)
        finally:
            # Always ensure the socket is closed properly
            s.close()

    return i, win


    # Return number of actions used and whether the env was completed successfully
    return i, win


if __name__ == "__main__":
    # Example usage
    user_interactive_agent = UserInteractiveAgent()
    max_game_length = 100
    experiment_path = r'C:\Users\Sharky\RIPPLE\data\experiment_ID_20241029_103746\experiment_UserInteractiveAgent_ShapePuzzle_1'

    actions, win = action_perception_loop(user_interactive_agent, max_game_length, experiment_path)