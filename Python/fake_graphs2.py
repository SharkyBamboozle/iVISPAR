# Define individual data for each subplot, including "Wins" and "Steps"
data = {
    ("Puzzle", "Iterative"): {
        "Complexity": [1, 2, 3, 4, 5],
        "GPT-4o_wins": [1.2, 1.4, 1.6, 1.8, 2.0],
        "Claude_wins": [1.3, 1.5, 1.7, 1.9, 2.1],
        "Gemini_wins": [1.4, 1.6, 1.8, 2.0, 2.2],
        "GPT-4o_steps": [2.2, 2.4, 2.6, 2.8, 3.0],
        "Claude_steps": [2.3, 2.5, 2.7, 2.9, 3.1],
        "Gemini_steps": [2.4, 2.6, 2.8, 3.0, 3.2]
    },
    ("Puzzle", "Planned"): {
        "Complexity": [1, 2, 3, 4, 5],
        "GPT-4o_wins": [2.1, 2.3, 2.5, 2.7, 2.9],
        "Claude_wins": [2.0, 2.2, 2.4, 2.6, 2.8],
        "Gemini_wins": [1.9, 2.1, 2.3, 2.5, 2.7],
        "GPT-4o_steps": [3.1, 3.3, 3.5, 3.7, 3.9],
        "Claude_steps": [3.0, 3.2, 3.4, 3.6, 3.8],
        "Gemini_steps": [2.9, 3.1, 3.3, 3.5, 3.7]
    },
    ("Puzzle", "Generalization"): {
        "Complexity": [1, 2, 3],
        "GPT-4o_wins": [3.3, 3.5, 3.7],
        "Claude_wins": [3.2, 3.4, 3.6],
        "Gemini_wins": [3.1, 3.3, 3.5],
        "GPT-4o_steps": [4.1, 4.3, 4.5],
        "Claude_steps": [4.0, 4.2, 4.4],
        "Gemini_steps": [3.9, 4.1, 4.3]
    },
    ("Perspective", "Iterative"): {
        "Complexity": [1, 2, 3, 4, 5],
        "GPT-4o_wins": [1.3, 1.5, 1.7, 1.9, 2.1],
        "Claude_wins": [1.4, 1.6, 1.8, 2.0, 2.2],
        "Gemini_wins": [1.5, 1.7, 1.9, 2.1, 2.3],
        "GPT-4o_steps": [2.4, 2.6, 2.8, 3.0, 3.2],
        "Claude_steps": [2.5, 2.7, 2.9, 3.1, 3.3],
        "Gemini_steps": [2.6, 2.8, 3.0, 3.2, 3.4]
    },
    ("Perspective", "Planned"): {
        "Complexity": [1, 2, 3, 4, 5],
        "GPT-4o_wins": [2.4, 2.6, 2.8, 3.0, 3.2],
        "Claude_wins": [2.3, 2.5, 2.7, 2.9, 3.1],
        "Gemini_wins": [2.2, 2.4, 2.6, 2.8, 3.0],
        "GPT-4o_steps": [3.4, 3.6, 3.8, 4.0, 4.2],
        "Claude_steps": [3.3, 3.5, 3.7, 3.9, 4.1],
        "Gemini_steps": [3.2, 3.4, 3.6, 3.8, 4.0]
    },
    ("Perspective", "Generalization"): {
        "Complexity": [1, 2, 3],
        "GPT-4o_wins": [4.0, 4.2, 4.4],
        "Claude_wins": [3.9, 4.1, 4.3],
        "Gemini_wins": [3.8, 4.0, 4.2],
        "GPT-4o_steps": [4.8, 5.0, 5.2],
        "Claude_steps": [4.7, 4.9, 5.1],
        "Gemini_steps": [4.6, 4.8, 5.0]
    },
    ("Maze", "Iterative"): {
        "Complexity": [1, 2, 3, 4, 5],
        "GPT-4o_wins": [1.4, 1.6, 1.8, 2.0, 2.2],
        "Claude_wins": [1.5, 1.7, 1.9, 2.1, 2.3],
        "Gemini_wins": [1.6, 1.8, 2.0, 2.2, 2.4],
        "GPT-4o_steps": [2.3, 2.5, 2.7, 2.9, 3.1],
        "Claude_steps": [2.4, 2.6, 2.8, 3.0, 3.2],
        "Gemini_steps": [2.5, 2.7, 2.9, 3.1, 3.3]
    },
    ("Maze", "Planned"): {
        "Complexity": [1, 2, 3, 4, 5],
        "GPT-4o_wins": [2.7, 2.9, 3.1, 3.3, 3.5],
        "Claude_wins": [2.6, 2.8, 3.0, 3.2, 3.4],
        "Gemini_wins": [2.5, 2.7, 2.9, 3.1, 3.3],
        "GPT-4o_steps": [3.5, 3.7, 3.9, 4.1, 4.3],
        "Claude_steps": [3.4, 3.6, 3.8, 4.0, 4.2],
        "Gemini_steps": [3.3, 3.5, 3.7, 3.9, 4.1]
    },
    ("Maze", "Generalization"): {
        "Complexity": [1, 2, 3],
        "GPT-4o_wins": [3.2, 3.4, 3.6],
        "Claude_wins": [3.1, 3.3, 3.5],
        "Gemini_wins": [3.0, 3.2, 3.4],
        "GPT-4o_steps": [3.7, 3.9, 4.1],
        "Claude_steps": [3.6, 3.8, 4.0],
        "Gemini_steps": [3.5, 3.7, 3.9]
    }
}

games = ["Puzzle", "Perspective", "Maze"]
settings = ["Iterative", "Planned", "Generalization"]

import matplotlib.pyplot as plt
import seaborn as sns

# Set Seaborn style
sns.set_theme(style="darkgrid")

# Define models and stronger pastel colors for distinct looks
models = ["GPT-4o", "Claude", "Gemini"]

# Use seaborn's "Set2" palette for more vibrant but soft red, green, and blue
custom_colors = sns.color_palette("Set2", 3)  # Distinctive and slightly stronger pastel-like shades
color_map = {model: color for model, color in zip(models, custom_colors)}

# Plotting
fig, axes = plt.subplots(3, 3, figsize=(20, 10), sharey=True)
fig.suptitle("Model Comparison with Incremental Values Across Complexity Levels", y=0.98, fontsize=18,
             fontweight='bold')

for row_idx, game in enumerate(games):
    for col_idx, setting in enumerate(settings):
        ax = axes[row_idx, col_idx]
        data_subset = data[(game, setting)]

        # Secondary y-axis for "Steps"
        ax_secondary = ax.twinx()

        for model in models:
            wins_data = data_subset[f"{model}_wins"]
            steps_data = data_subset[f"{model}_steps"]
            complexities = data_subset["Complexity"]

            # Use the same color for "wins" and "steps" for each model with Set2 colors
            ax.plot(complexities, wins_data, color=color_map[model], marker='o', linestyle='-', label=f"{model} Wins",
                    alpha=0.9)
            ax_secondary.plot(complexities, steps_data, color=color_map[model], marker='o', linestyle='--',
                              label=f"{model} Steps", alpha=0.9)

        ax.set_ylim(1, 5)
        ax_secondary.set_ylim(2, 5)

        if setting == "Generalization":
            ax.set_xticks([1, 2, 3])

        if col_idx == 0:
            ax.set_ylabel("Wins")
        else:
            ax.set_yticklabels([])

        if col_idx == 2:
            ax_secondary.set_ylabel("Steps")
        else:
            ax_secondary.set_yticklabels([])

# Set titles for each column
for ax, col in zip(axes[0], settings):
    ax.set_title(col, fontsize=15, pad=15)

# Set row labels for each game type
for ax, row in zip(axes[:, 0], games):
    ax.annotate(row, xy=(0, 0.5), xytext=(-40, 0),
                xycoords='axes fraction', textcoords='offset points',
                ha='center', va='center', rotation=90, fontsize=15, fontweight='bold')

# Create legend entries
handles, labels = [], []
for model in models:
    handles.append(
        plt.Line2D([0], [0], color=color_map[model], marker='o', linestyle='-', label=f"{model} Wins", alpha=0.9))
    handles.append(
        plt.Line2D([0], [0], color=color_map[model], marker='o', linestyle='--', label=f"{model} Steps", alpha=0.9))

# Display legend above plot
fig.legend(handles=handles, loc='upper center', ncol=6, bbox_to_anchor=(0.5, 0.95), frameon=False)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()