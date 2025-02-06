"""
- This code compiles the evaluation from individual episodes into csv files for the different statistics
- The csv file gets saved into the results dir with the same ID name as the experiment
- From this csv file the evaluation can be plotted
"""
import os
import pandas as pd
import Source.Evaluate.evaluation_utilities as util
from scipy.stats import sem, t

def compile_experiment_statistics(experiment_id, confidence_level=0.95):
    """
    Compile standard deviation and confidence interval statistics into one CSV.
    """
    experiment_dir, results_dir = util.make_results_dir(experiment_id)
    data_path = os.path.join(results_dir, 'episode_outcomes_evaluation.csv')

    if not os.path.exists(data_path):
        print(f"No data found at {data_path}")
        return

    df = pd.read_csv(data_path)

    # Compute standard deviation and confidence intervals
    std_df = compute_standard_deviation(df)
    ci_df = compute_confidence_intervals(df, confidence_level)

    # Merge results into one DataFrame
    merged_df = pd.merge(std_df, ci_df, on=['model_type', 'representation_type', 'scenario'], how='outer')

    # Save the compiled CSV
    output_csv_path = os.path.join(results_dir, 'experiment_statistics_evaluation.csv')
    merged_df.to_csv(output_csv_path, index=False)
    print(f"Experiment statistics compiled and saved to {output_csv_path}")


def compute_standard_deviation(df):
    """
    Compute the standard deviation for relevant metrics.
    """
    metrics = ['min_path_length', 'spl_value', 'won', 'won_at_spl']

    # Group by agent, modality, and scenario
    std_df = (
        df.groupby(['model_type', 'representation_type', 'scenario'])[metrics]
        .std()
        .reset_index()
        .rename(columns={metric: f'{metric}_std' for metric in metrics})
    )

    return std_df


def compute_confidence_intervals(df, confidence_level=0.95):
    """
    Compute confidence intervals for relevant metrics.
    """
    metrics = ['min_path_length', 'spl_value', 'won', 'won_at_spl']
    ci_data = []

    for (model_type, representation_type, scenario), group in df.groupby(['model_type', 'representation_type', 'scenario']):
        ci_entry = {
            'model_type': model_type,
            'representation_type': representation_type,
            'scenario': scenario,
        }
        for metric in metrics:
            values = group[metric].dropna()
            n = len(values)
            if n > 1:
                mean = values.mean()
                se = sem(values)
                interval = t.ppf((1 + confidence_level) / 2, n - 1) * se
                ci_entry[f'{metric}_ci_lower'] = mean - interval
                ci_entry[f'{metric}_ci_upper'] = mean + interval
            else:
                # Handle cases with 1 or 0 data points
                ci_entry[f'{metric}_ci_lower'] = values.mean() if n == 1 else 0
                ci_entry[f'{metric}_ci_upper'] = values.mean() if n == 1 else 0

        ci_data.append(ci_entry)

    ci_df = pd.DataFrame(ci_data)
    return ci_df


if __name__ == "__main__":
    experiment_id = 'baselines'
    compile_experiment_statistics(experiment_id)