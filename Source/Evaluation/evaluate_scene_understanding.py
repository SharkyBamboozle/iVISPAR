import os
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from evaluation_utilities import make_results_dir

def plot_board_state_prediction_results(experiment_id):
    """
    Plots the results of board state prediction for all scene_understanding_results_*.json files
    in the given experiment_id directory. Plots are saved to the results directory.

    Args:
        experiment_id (str): The experiment ID to plot results for.
    """
    experiment_dir, results_dir = make_results_dir(experiment_id)

    # Get all JSON files matching the pattern scene_understanding_results_*.json
    result_files = [f for f in os.listdir(results_dir) if f.startswith('scene_understanding_results_') and f.endswith('.json')]

    if not result_files:
        print(f"No results files found for {experiment_id} in {results_dir}")
        return

    # Load data from all result files into a DataFrame
    all_results = []
    for result_file in result_files:
        file_path = os.path.join(results_dir, result_file)
        try:
            with open(file_path, 'r') as f:
                result_data = json.load(f)
                result_data['file'] = result_file  # Track the source file for debugging
                all_results.append(result_data)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    # Convert the results into a DataFrame
    df = pd.DataFrame(all_results)

    if df.empty:
        print(f"No valid results loaded for {experiment_id}.")
        return

    # Plot the metrics using Seaborn
    sns.set(style="whitegrid")

    # Plot 1: Precision Distribution
    plt.figure(figsize=(8, 6))
    sns.histplot(df['precision'], kde=True, color='skyblue', bins=20)
    plt.title('Precision Distribution')
    plt.xlabel('Precision')
    plt.ylabel('Frequency')
    precision_plot_path = os.path.join(results_dir, 'precision_distribution.png')
    plt.savefig(precision_plot_path)
    plt.close()

    # Plot 2: Recall Distribution
    plt.figure(figsize=(8, 6))
    sns.histplot(df['recall'], kde=True, color='orange', bins=20)
    plt.title('Recall Distribution')
    plt.xlabel('Recall')
    plt.ylabel('Frequency')
    recall_plot_path = os.path.join(results_dir, 'recall_distribution.png')
    plt.savefig(recall_plot_path)
    plt.close()

    # Plot 3: F1 Score Distribution
    plt.figure(figsize=(8, 6))
    sns.histplot(df['f1_score'], kde=True, color='green', bins=20)
    plt.title('F1 Score Distribution')
    plt.xlabel('F1 Score')
    plt.ylabel('Frequency')
    f1_score_plot_path = os.path.join(results_dir, 'f1_score_distribution.png')
    plt.savefig(f1_score_plot_path)
    plt.close()

    # Plot 4: Scatter plot of Precision vs Recall
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=df['precision'], y=df['recall'], hue=df['f1_score'], palette='viridis', size=df['f1_score'], sizes=(20, 200))
    plt.title('Precision vs Recall')
    plt.xlabel('Precision')
    plt.ylabel('Recall')
    precision_recall_plot_path = os.path.join(results_dir, 'precision_vs_recall.png')
    plt.savefig(precision_recall_plot_path)
    plt.close()

    # Plot 5: Number of Correct Matches
    plt.figure(figsize=(8, 6))
    sns.histplot(df['num_correct_matches'], kde=False, color='red', bins=20)
    plt.title('Number of Correct Matches')
    plt.xlabel('Number of Correct Matches')
    plt.ylabel('Frequency')
    correct_matches_plot_path = os.path.join(results_dir, 'num_correct_matches.png')
    plt.savefig(correct_matches_plot_path)
    plt.close()

    print(f"Plots saved in {results_dir}")


def check_board_state_prediction(board_state, predicted_board_state, save_path="board_state_results.json"):
    """
    Checks how much of the predicted board state matches the actual board state
    and saves the result, board state, and predicted board state in a JSON file.

    Args:
        board_state (list of str): The actual board state.
        predicted_board_state (list of str): The predicted board state.
        save_path (str): Path to the file where the results will be saved.

    Returns:
        dict: A dictionary containing the number of correct matches, total items in board_state,
              total items in predicted_board_state, and the match accuracy.
    """
    # Convert to sets for unordered comparison
    board_state_set = set(board_state)
    predicted_board_state_set = set(predicted_board_state)

    # Calculate correct matches
    correct_matches = board_state_set.intersection(predicted_board_state_set)  # Elements in both sets
    num_correct_matches = len(correct_matches)

    # Calculate the total number of items
    total_board_state = len(board_state_set)
    total_predicted_board_state = len(predicted_board_state_set)

    # Calculate accuracy measures
    precision = num_correct_matches / total_predicted_board_state if total_predicted_board_state > 0 else 0  # How precise was the prediction?
    recall = num_correct_matches / total_board_state if total_board_state > 0 else 0  # How much of the true board was recalled?
    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    # Combine all the results into one dictionary
    results = {
        'board_state': board_state,
        'predicted_board_state': predicted_board_state,
        'num_correct_matches': num_correct_matches,
        'total_board_state': total_board_state,
        'total_predicted_board_state': total_predicted_board_state,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score
    }

    # Save results to a JSON file
    try:
        with open(save_path, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"Results saved to {save_path}")
    except Exception as e:
        print(f"Error saving results to {save_path}: {e}")

    return results


def evaluate_scene_understanding(experiment_id):
    """
    Evaluate the scene understanding for a specific experiment by comparing the board state
    from obs_0.json with the predicted state in agent_message_log.txt.

    Args:
        experiment_id (str): The experiment ID to evaluate.
    """
    experiment_dir, results_dir = make_results_dir(experiment_id)


    # Initialize board_state and predicted_board_state
    board_state = []
    predicted_board_state = []

    i = 0
    # Loop through subdirectories in the experiment directory
    for subdir in os.listdir(experiment_dir):
        subdir_path = os.path.join(experiment_dir, subdir)

        # Only consider directories that have "SceneUnderstanding" in their name
        if not os.path.isdir(subdir_path) or 'SceneUnderstanding' not in subdir:
            continue

        # **Load board state from obs_0.json**
        obs_path = os.path.join(subdir_path, 'obs', 'obs_0.json')
        if os.path.exists(obs_path):
            try:
                with open(obs_path, 'r') as f:
                    board_state = json.load(f)  # Load the board state as a list of strings
            except Exception as e:
                print(f"Error loading board state from {obs_path}: {e}")
        else:
            print(f"obs_0.json not found in {obs_path}. Skipping this directory.")
            continue

        # **Load predicted board state from agent_message_log.txt**
        agent_message_log_path = os.path.join(subdir_path, 'agent_message_log.txt')
        if os.path.exists(agent_message_log_path):
            try:
                with open(agent_message_log_path, 'r') as f:
                    # Load each non-empty line from the file as a list of strings
                    predicted_board_state = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"Error loading predicted board state from {agent_message_log_path}: {e}")
        else:
            print(f"agent_message_log.txt not found in {agent_message_log_path}. Skipping this directory.")
            continue

        # **Evaluate the scene understanding by comparing board_state and predicted_board_state**
        try:
            results_path = os.path.join(results_dir, f"scene_understanding_results_{i}.json")
            results = check_board_state_prediction(board_state, predicted_board_state, save_path=results_path)
            i+=1
        except Exception as e:
            print(f"Error evaluating board state prediction for {subdir}: {e}")


if __name__ == "__main__":

    experiment_id = "experiment_ID_20241207_163017"

    evaluate_scene_understanding(experiment_id)
    plot_board_state_prediction_results(experiment_id)