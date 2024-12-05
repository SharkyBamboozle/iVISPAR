Installation

For general information and how to install the software please refer to the README.

```
## Table of Contents
- [Features](#features)
- [**Getting Started**](#getting-started)
- [**Quick Start**](#q**uick-start**)
- [**Citation**](#c**itation**)
```

## Running

This main file serves as an example how to run the entire code for an experiment in order. However, due to the timedemand of the configurations and experiments it is not recommended to run the entire code from here. It is recommendedto rather run the code in individual sections, first generating a configuration set (or using one of the ready-made onesin the Data/Configs dir) then running the experiment and later evaluating it.

### Running the experiment

- run /run_experiment to evaluate your results
- the script will try to open the iVISPAR web app in the standard browser of your OS
- once the iVISPAR web app has loaded in your browser, the client ID should be copied automaccily to your clipboard, or you can click on copy ID in the iVISAR GUI in your browser
- in your Python console, you’ll be asked to provide the client ID, paste the client ID into the Python console and press enter
- You should be able to view the experiments running in your browser now

### Experiment Data

- The experiment data will be assigned a timestamped ID and saved to data/experiments
- you will find a new directory under data/experiments containing a directory for each game that was run
- This data includes

### Parametrizing the experiment

- iVISPAR provides a high amount of parametrization to run your experiment
- This includes parameters for the
    - agents
    - game
    - simulation

### Agent

### Game

### Simulation