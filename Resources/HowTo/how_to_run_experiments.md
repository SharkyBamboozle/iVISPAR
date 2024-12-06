<div id="readme-top"></div>

# How to run experiments

For general information on the installation and setup please refer to the main [README](../README.md).

## Table of Contents
1. [Where to start](#triangular_flag_on_post-Where-to-start)
2. [Running the experiment](#slot_machine-Running-the-experiment)
3. [Experiment Data](#test_tube-Experiment-Data)
4. [Parametrizing the experiment](#triangular_ruler-Parametrizing-the-experiment)
    1. [Agent](#space_invader-Agent)
    2. [Game](#joystick-Game)
    3. [Simulation](#chess_pawn-Simulation)


## :triangular_flag_on_post: Where to start?
The project includes a [main file](../Source/main.py) that demonstrates how to run the entire experiment workflow in sequence. However, due to the time-intensive nature of generating configurations and running experiments, it is not recommended to execute the entire code directly from this file.

Instead, it is advised to run the code in separate stages:

1. Generate a configuration set (or use one of the pre-existing sets available in the [Data/Configs](../Data/Configs) directory).
2. Execute the experiment with [Source/Experiment/run_experiment.py](../Source/Experiment/run_experiment.py) using the generated or pre-made configuration.
3. Evaluate the results afterward.

This approach allows for greater flexibility and efficiency when working with the code.


### :slot_machine: Running the experiment

To test the LLM interaction with the Sliding Geom Puzzle simulation:

1. Get a configuration ID from a self-generated configuration dataset or the provided pre-made dataset in [Data/Configs](../Data/Configs)
2. In [Source/Experiment/run_experiment.py](../Source/Experiment/run_experiment.py) set the `config_id` of the `games` dict to the config ID you selected
3. Run [Source/Experiment/run_experiment.py](../Source/Experiment/run_experiment.py), it will try to open the iVISPAR WebApp in the standard browser of your OS
4. Once the iVISPAR WebApp has loaded in your browser, the client ID should be copied automatically to your clipboard, or you can click on copy ID in the iVISPAR GUI in your browser
5. in your Python console, you’ll be asked to provide the client ID, paste the client ID into the Python console and press enter

You should be able to view the experiments running in your browser now

### :test_tube: Experiment Data

- The experiment data will be assigned a timestamped ID and saved to [Data/Experiments](../Data/Experiments) where you will find a new directory containing data or each game that was run
- This data includes

  1. The configuration file used to make the puzzle
  2. A video showing the interactions of the agent with the simulation
  3. A list of the chain of thoughts of the agent
  4. A list of the actions of the agent
  5. A list of the simulation logging

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## :triangular_ruler: Parametrizing the experiment
iVISPAR provides a high amount of parametrization to run your experiment:

### :space_invader: Agent
To add your agent, the agent class needs to be implemented in [Source/Experiment/agent_systems.py](../Source/Experiment/agent_systems.py). Then you can add your agent to the agents dictionary:

```Python
    agents = {
        'GPT4Agent': {
            'class': agent_systems.GPT4Agent,
            'params': {
                'instruction_prompt_file_path': instruction_prompt_file_path, # File path to the task instruction prompt the agent receives
                'api_keys_file_path': api_keys_file_path, # File path to the personal API key in case the agent uses an API
                'single_images': True, # Set whether state and goal images are added as a single file or as separate files
                'COT': True, # Set whether the chain of thoughts is prompted by the agent
            }
        }
    }
```

### :joystick: Game
To add changes to the game, the game class needs to be implemented in [Source/Experiment/game_systems.py](../Source/Experiment/game_systems.py). Then you can add your game to the games dictionary:

```Python
    games = {
        'InteractivePuzzle': {
            'class': game_systems.InteractivePuzzle,
            'params': {
                'config_id': config_id, # ID of the config file dataset
                'num_game_env': 2,  # Max amount of games to play (set to a high value to play all configs)
                'max_game_length': 50,  # Max amount of action-perception iterations with the environment
                'representation_type': 'vision', #'text' 'both' # Set whether the state is presented to the agent with images, text or both
                'planning_steps': 1, # Set how many moves the agent needs to plan, before getting a new image
                'instruction_prompt_file_path': instruction_prompt_file_path, # File path to the task instruction prompt the agent receives
                'chain_of_thoughts': True # Set whether the chain of thoughts is prompted by the agent
            }
        }
    }
```


### :chess_pawn: Simulation
```Python
    sim_param = {
        'grid_label': 'both', # Set whether the grid has visual cues, choices are between 'edge', 'cell', 'both' and 'none' 
        'camera_offset': [0,5.57,-3.68], # Set camera position
        'camera_auto_override': [6.8,-1,6.8], # Set camera position
        'screenshot_alpha': 0.0, # Set whether the image background should be transparent to add custom background colors
    }
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>
