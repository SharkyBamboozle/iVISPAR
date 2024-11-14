import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Models and Games
models = ["GPT-4o", "Claude", "Gemini"]
games = ["Puzzle", "Perspective", "Maze"]

# Correcting the success rate values to ensure the right values for each model across each game
data_custom_corrected = {
    "Model": np.repeat(models, len(games)),
    "Game": games * len(models),
    "Success Rate": [
        15, 35, 59,  # Puzzle (lowest success rates, GPT-4o, Claude, Gemini)
        17, 42, 63,  # Perspective (medium success rates, GPT-4o, Claude, Gemini)
        22, 45, 70   # Maze (highest success rates, GPT-4o, Claude, Gemini)
    ]
}

# Create corrected DataFrame
df_custom_corrected = pd.DataFrame(data_custom_corrected)

# Define bar width and positions for grouped bars
bar_width = 0.25
positions = np.arange(len(games))

# Initialize the figure
plt.figure(figsize=(10, 6))

# Plot each model's data as a separate set of bars for each game
for i, model in enumerate(models):
    success_rates = df_custom_corrected[df_custom_corrected["Model"] == model]["Success Rate"].values
    plt.bar(positions + i * bar_width, success_rates, width=bar_width, label=model)

# Customize tick positions and remove axis labels
plt.xticks(positions + bar_width, games)
plt.legend(title="Models")

plt.show()
