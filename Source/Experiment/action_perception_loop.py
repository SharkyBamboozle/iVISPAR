import os
import socket
from PIL import Image

import util_functions as util
import agent

def action_perception_loop(user_agent, max_game_length, save_path, HOST="127.0.0.1", PORT=1984, single_images=True):
    """
    Connects to the server via a socket and handles the receiving of observations and sending of actions
    over TCP to simulate the action-perception loop between the Unity environment and the multimodal-LLM.

    Args:
        user_agent (UserInteractiveAgent): The user agent for interacting with the environment.
        max_game_length (int): Maximum number of actions in the game loop.
        single_images (bool): If False, uses merged comparison images for agent decisions. If True, gets two states seperatly.
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

        action = "init"

        try:
            for i in range(1, max_game_length + 1):

                required_bytes = 1200 * 900 * 4  # Calculate the number of bytes required
                observation = bytearray()  # Create a mutable byte array to store data

                # Keep receiving until we have the required number of bytes
                while len(observation) < required_bytes:
                    # Wait and receive observation data from Unity (blocking call until data arrives)
                    packet = s.recv(4096)  # Adjust chunk size as needed
                    if not packet:
                        # The connection was closed by the server
                        print("Connection closed by the server.")
                        win = True  # Set win condition to true if the connection is closed
                        i -= 1
                        break  # Exit the loop
                    observation.extend(packet)  # Append the received packet to our byte array

                # Convert the raw bytes to an image RGB or RGBA
                image = Image.frombytes('RGBA', (1200, 900), observation, 'raw')
                image = image.transpose(Image.FLIP_TOP_BOTTOM)

                # Save the observation image with a sequential filename inside the 'obs' directory
                filename = os.path.join(obs_dir, f"obs_{i}_{action}.png")
                image.save(filename)  # Save the image as a PNG
                print(f"Saved image to {filename}")

                util.merge_images(filename, obs_dir)
                if not single_images:
                    # Construct the path to the merged image
                    file_root, file_ext = os.path.splitext(filename)
                    merged_image_path = os.path.join(obs_dir, f"{os.path.basename(file_root)}_compare{file_ext}")
                    # Load the merged image
                    image = Image.open(merged_image_path)




                # Process the observation using the user_agent
                action = user_agent.act(image)
                s.sendall(action.encode())  # Send action encoded as bits back to Unity


        except (ConnectionResetError, ValueError, socket.error, BrokenPipeError) as e:
            print("Connection error or game ended prematurely:", e)
        finally:
            # Always ensure the socket is closed properly
            s.close()

    # Return number of actions used and whether the env was completed successfully
    return i, win


if __name__ == "__main__":
    # Example usage
    user_interactive_agent = agent.UserInteractiveAgent()
    max_game_length = 100
    experiment_path = r'C:\Users\Sharky\RIPPLE\data\experiment_ID_20241101_161534\2'

    actions, win = action_perception_loop(user_interactive_agent, max_game_length, experiment_path)