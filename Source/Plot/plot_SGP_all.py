from plot_episodes_progress_lineplot import plot_episode_evaluate_a_star_heuristic
from plot_lineplot import plot_csv_with_confidence_interval
from plot_heatmap import plot_heat_map_episode_level_average
from plot_barplot_old import plot_bar_plot_with_baselines

experiment_id = 'Merged_all_49_checks_2nd_try'

agents = ['Claude']#, 'Gemini', 'GPT-4', 'Qwen', 'InternVL']
#modalities = ['text-h5', 'text-h4', 'text', 'vision-both-COT', 'vision-both-COT-History', 'vision-both', 'vision', 'vision-label', 'vision-color', 'vision-none']
#modalities = ['text-h4'] #, 'vision-both', 'vision-none', 'vision-label-noCOT', 'vision-color-noCOT']
modalities = ['text-h5', 'text-h4','text-h3', 'text-h2', 'text-h1', 'text-h0', 'vision-h4', 'vision-h3', 'vision-both', 'vision-h1', 'vision-h0']
baseline_agents = ['OptimalAgentBaseline', 'RandomInvalidAgentBaseline', 'RandomValidAgentBaseline']
baseline_modalities = ['text', 'vision']

#plot_episode_evaluate_a_star_heuristic(experiment_id, experiment_signature="InteractivePuzzle")

# Evaluate and plot for each episode of the experiment
plot_bar_plot_with_baselines(
    experiment_id=experiment_id,
    agents=agents,
    modalities=modalities,
    baseline_agents=baseline_agents,
    baseline_modalities=None
)

# Evaluate and plot for each episode of the experiment
plot_heat_map_episode_level_average(
    experiment_id=experiment_id,
    agents=agents,
    modalities=modalities
)

# Evaluate and plot for each episode of the experiment
plot_csv_with_confidence_interval(
    experiment_id=experiment_id,
    agents=agents,
    modalities=modalities,
    show_confidence_interval=False
)

