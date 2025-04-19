
import os
import Source.Evaluate.evaluation_utilities as util

def compile_all_actions(experiment_id, experiment_signature="InteractivePuzzle"):
    """
    Compile all agent_message_log.txt files from subdirectories into one consolidated text file.

    Args:
        experiment_id (str): The experiment ID to locate the directory.
        experiment_signature (str): Signature to filter subdirectories.
    """
    # Get experiment and results directories
    experiment_dir, results_dir = util.make_results_dir(experiment_id)
    sub_dirs = util.filter_experiment_sub_dirs(experiment_dir, experiment_signature)

    # Create a path for the consolidated log file
    consolidated_log_path = os.path.join(results_dir, "compiled_agent_logs.txt")

    with open(consolidated_log_path, 'w') as consolidated_log:
        # Iterate through each subdirectory
        for sub_dir in sub_dirs:
            log_file_path = os.path.join(sub_dir, "agent_message_log.txt")

            if os.path.exists(log_file_path):
                try:
                    with open(log_file_path, 'r') as log_file:
                        # Write the content to the consolidated log with a separator
                        consolidated_log.write(f"\n===== {os.path.basename(sub_dir)} =====\n")
                        consolidated_log.write(log_file.read())
                        consolidated_log.write("\n")

                except Exception as e:
                    print(f"Error reading log file in {sub_dir}: {e}")
            else:
                print(f"No agent_message_log.txt found in {sub_dir}, skipping...")

    print(f"Consolidated agent logs saved at {consolidated_log_path}")

if __name__ == "__main__":
    experiment_id = 'qwen_text'
    experiment_signature = "InteractivePuzzle"

    # Compile all actions into one text file
    compile_all_actions(experiment_id, experiment_signature=experiment_signature)
