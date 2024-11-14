data = {
    ("Puzzle", "Iterative"): {
        "Complexity": [1, 2, 3, 4, 5],
        "GPT-4o_wins": [19.53, 23.25, 24.02, 24.58, 30.54],
        "Claude_wins": [23.80, 24.96, 25.88, 28.82, 34.66],
        "Gemini_wins": [19.71, 19.76, 20.28, 21.70, 22.95],
        "GPT-4o_steps": [47.54, 47.16, 42.36, 39.95, 36.52],
        "Claude_steps": [49.21, 43.12, 38.50, 21.50, 20.78],
        "Gemini_steps": [47.01, 41.70, 27.58, 27.02, 20.54]
    },
    ("Puzzle", "Planned"): {
        "Complexity": [1, 2, 3, 4, 5],
        "GPT-4o_wins": [16.27, 23.58, 24.76, 26.63, 29.78],
        "Claude_wins": [22.07, 23.41, 25.83, 27.02, 31.48],
        "Gemini_wins": [21.31, 25.18, 30.46, 31.64, 33.02],
        "GPT-4o_steps": [48.30, 47.97, 39.82, 32.15, 23.33],
        "Claude_steps": [49.06, 48.02, 46.51, 26.67, 24.87],
        "Gemini_steps": [36.45, 36.14, 24.16, 21.80, 20.25]
    },
    ("Puzzle", "Generalization"): {
        "Complexity": [1, 2, 3],
        "GPT-4o_wins": [21.62, 24.12, 31.22],
        "Claude_wins": [15.68, 17.49, 27.86],
        "Gemini_wins": [25.29, 30.11, 33.86],
        "GPT-4o_steps": [48.51, 44.22, 21.59],
        "Claude_steps": [31.23, 27.21, 22.04],
        "Gemini_steps": [47.36, 45.16, 22.92]
    },
    ("Perspective", "Iterative"): {
        "Complexity": [1, 2, 3, 4, 5],
        "GPT-4o_wins": [17.56, 25.32, 26.31, 27.02, 27.06],
        "Claude_wins": [21.23, 22.86, 28.05, 30.72, 34.38],
        "Gemini_wins": [18.96, 19.05, 32.32, 32.90, 33.22],
        "GPT-4o_steps": [49.81, 42.53, 40.02, 33.29, 27.72],
        "Claude_steps": [36.36, 27.64, 23.50, 22.82, 20.98],
        "Gemini_steps": [48.00, 46.83, 45.57, 37.92, 25.42]
    },
    ("Perspective", "Planned"): {
        "Complexity": [1, 2, 3, 4, 5],
        "GPT-4o_wins": [15.22, 15.80, 20.53, 24.49, 32.14],
        "Claude_wins": [15.62, 22.24, 24.01, 24.21, 26.15],
        "Gemini_wins": [17.78, 19.97, 20.03, 21.77, 25.79],
        "GPT-4o_steps": [30.51, 28.92, 27.17, 24.54, 24.19],
        "Claude_steps": [49.18, 36.10, 30.22, 27.98, 22.15],
        "Gemini_steps": [45.96, 45.48, 37.84, 37.14, 31.22]
    },
    ("Perspective", "Generalization"): {
        "Complexity": [1, 2, 3],
        "GPT-4o_wins": [19.82, 27.20, 30.41],
        "Claude_wins": [18.35, 26.34, 28.70],
        "Gemini_wins": [26.03, 30.60, 33.25],
        "GPT-4o_steps": [47.45, 28.20, 22.81],
        "Claude_steps": [45.28, 40.62, 32.76],
        "Gemini_steps": [39.46, 33.77, 21.07]
    },
    ("Maze", "Iterative"): {
        "Complexity": [1, 2, 3, 4, 5],
        "GPT-4o_wins": [15.93, 16.17, 23.77, 25.42, 31.87],
        "Claude_wins": [19.94, 21.64, 24.87, 30.04, 30.05],
        "Gemini_wins": [19.14, 23.56, 24.86, 30.25, 31.47],
        "GPT-4o_steps": [47.02, 43.93, 33.45, 27.10, 26.99],
        "Claude_steps": [39.45, 39.02, 33.93, 24.59, 23.81],
        "Gemini_steps": [42.19, 39.67, 31.33, 30.89, 25.95]
    },
    ("Maze", "Planned"): {
        "Complexity": [1, 2, 3, 4, 5],
        "GPT-4o_wins": [17.88, 20.52, 20.74, 23.13, 34.60],
        "Claude_wins": [20.89, 21.35, 26.09, 28.13, 34.06],
        "Gemini_wins": [15.71, 16.87, 27.37, 31.80, 34.51],
        "GPT-4o_steps": [41.44, 40.20, 27.61, 24.77, 20.13],
        "Claude_steps": [47.69, 30.24, 30.10, 29.53, 20.22],
        "Gemini_steps": [45.53, 44.99, 29.34, 26.67, 22.42]
    },
    ("Maze", "Generalization"): {
        "Complexity": [1, 2, 3],
        "GPT-4o_wins": [15.10, 31.19, 33.28],
        "Claude_wins": [18.20, 18.33, 28.08],
        "Gemini_wins": [17.23, 23.28, 28.22],
        "GPT-4o_steps": [45.59, 31.17, 29.62],
        "Claude_steps": [45.10, 41.76, 29.34],
        "Gemini_steps": [49.54, 46.21, 33.14]
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