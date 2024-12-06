import os
import json
from datetime import datetime

from plot_results import plot_results


def load_result_files(experiment_id):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    experiment_dir = os.path.join(base_dir, 'Data', 'Experiments', experiment_id)

    results = []

    # Iterate through subdirectories of the experiment directory
    for subdir in os.listdir(experiment_dir):
        subdir_path = os.path.join(experiment_dir, subdir)

        print(subdir_path)

        if not os.path.isdir(subdir_path):
            continue  # Skip non-directory files

        # Ensure the images exist
        if not os.path.exists(subdir_path):
            print(f"Missing images in {subdir_path}. Skipping...")
            continue

        # Iterate through files in the directory
        for filename in os.listdir(subdir_path):
            if filename == 'results.json':
                filepath = os.path.join(subdir_path, filename)
                with open(filepath, 'r') as file:
                    try:
                        results.append(json.load(file))

                    except json.JSONDecodeError:
                        print(f"Error decoding {filename}, skipping.")

        return results


def structure_results(results):
    return results


def evaluate(experiment_id):

    # Set up experiment ID and directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    results_dir = os.path.join(base_dir, 'Data', 'Results', experiment_id)
    os.makedirs(results_dir, exist_ok=True)

    results = load_result_files(experiment_id)
    structured_results = structure_results(results)
    #save results


if __name__ == "__main__":

    experiment_id = "experiment_ID_20241203_104853"

    print(f"Evaluate experiment {experiment_id}")
    evaluate(experiment_id)

    plot_results(experiment_id)