from evaluate_episodes_sgp import evaluate_episodes
from compile_experiment_steps_evaluation import compile_experiment_evaluation
from compile_experiment_wins_evaluation import compile_episode_evaluation
from compile_experiment_statistics import compile_experiment_statistics

experiment_id = 'Merged_all_49_checks_2nd_try'
experiment_signature = "InteractivePuzzle"

# Evaluate the experiment
print(f"Evaluate experiment {experiment_id}")

#this evaluates all single episodes individually in their episode subdir
evaluate_episodes(experiment_id)

# this compiles the step based data for all episodes into a csv results
compile_experiment_evaluation(experiment_id, experiment_signature)

# this compiles the results of the episodes
compile_episode_evaluation(experiment_id, experiment_signature)

compile_experiment_statistics(experiment_id, experiment_signature)
