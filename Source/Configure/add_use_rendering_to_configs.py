import os
import json


def add_use_rendering_to_json(dir_path, use_rendering_value=True):
    """
    Reads all JSON files in the specified directory, adds the 'use_rendering' parameter if missing,
    and saves the updated files.

    Args:
        dir_path (str): Path to the directory containing JSON files.
        use_rendering_value (bool): Value to set for 'use_rendering' (default is True).
    """
    # Loop through all files in the directory
    for file_name in os.listdir(dir_path):
        if file_name.endswith(".json"):
            file_path = os.path.join(dir_path, file_name)

            try:
                # Read the JSON file
                with open(file_path, 'r') as f:
                    data = json.load(f)

                # Check if 'use_rendering' is missing and add it
                if 'use_rendering' not in data:
                    data['use_rendering'] = use_rendering_value
                    print(f"Added 'use_rendering' to {file_name}")

                    # Save the updated JSON back to the file
                    with open(file_path, 'w') as f:
                        json.dump(data, f, indent=4)
                        print(f"Updated {file_name} successfully.")

                else:
                    print(f"'use_rendering' already exists in {file_name}")

            except Exception as e:
                print(f"Error processing {file_name}: {e}")


# Example usage
if __name__ == "__main__":
    dir_path = r"C:\Users\Sharky\iVISPAR_dev\Data\Configs\ICML_checks_mod"
    add_use_rendering_to_json(dir_path)
