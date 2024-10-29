import os
import socket
from PIL import Image

from util_functions import UserInteractiveAgent


def merge_images(single_img_filename, obs_dir, bar_width=10):
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
    result = Image.new('RGB', (total_width, img1.height), (255, 255, 255))  # White background

    # Paste the two images onto the result image
    result.paste(img1, (0, 0))  # Paste the first image on the left
    result.paste(img2, (img1.width + bar_width, 0))  # Paste the second image on the right

    # Split the filename and extension
    file_root, file_ext = os.path.splitext(single_img_filename)
    double_img_file_name = f"{file_root}_compare{file_ext}"

    # Save the result back to the output directory with the modified name
    output_path = os.path.join(obs_dir, os.path.basename(double_img_file_name))
    result.save(output_path)

    print(f"Merged image saved to {output_path}")



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

                merge_images(filename, obs_dir)




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
    user_interactive_agent = UserInteractiveAgent()
    max_game_length = 100
    experiment_path = r'C:\Users\Sharky\RIPPLE\data\experiment_ID_20241029_103746\experiment_UserInteractiveAgent_ShapePuzzle_1'

    actions, win = action_perception_loop(user_interactive_agent, max_game_length, experiment_path)