def load_params_from_json(file_name):
    """
    Loads parameters from a JSON file and returns them as a dictionary.

    Args:
        file_path (str): Path to the JSON file containing the parameters.

    Returns:
        dict: A dictionary containing all the parameters from the JSON file.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    file_path = os.path.join(base_dir, 'Data', 'Params', file_name)
    try:
        with open(file_path, 'r') as file:
            params = json.load(file)
        return params
    except Exception as e:
        return {}


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
    json_files = [f for f in os.listdir(directory_path) if fnmatch.fnmatch(f, 'config*.json')]

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