import os
import json

def load_single_json_from_directory(directory_path):
    """
    Finds and loads a single JSON file from the specified directory.

    Parameters:
        directory_path (str): Path to the directory containing the JSON file.

    Returns:
        dict: Parsed JSON content as a dictionary.

    Raises:
        FileNotFoundError: If no JSON files are found in the directory.
        ValueError: If more than one JSON file is found in the directory.
        json.JSONDecodeError: If the file content is not valid JSON.
    """
    if not os.path.isdir(directory_path):
        raise FileNotFoundError(f"The directory does not exist: {directory_path}")

    # Find all JSON files in the directory
    json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]

    if len(json_files) == 0:
        raise FileNotFoundError(f"No JSON files found in the directory: {directory_path}")
    if len(json_files) > 1:
        raise ValueError(f"Multiple JSON files found in the directory: {json_files}. Specify the exact file.")

    # Load the single JSON file
    file_path = os.path.join(directory_path, json_files[0])
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Error decoding JSON file: {file_path}. Details: {str(e)}")

# Example usage:
directory_path = "/path/to/your/json_directory"
try:
    json_data = load_single_json_from_directory(directory_path)
    print("JSON data loaded successfully:", json_data)
except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
    print(e)
