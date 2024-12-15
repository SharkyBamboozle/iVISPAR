<div id="readme-top"></div>


![Build](https://img.shields.io/github/actions/workflow/status/username/repository/build.yml?branch=main)


# :jigsaw: iVISPAR
The Interactive Visual-Spatial Reasoning (iVISPAR) benchmark assesses the visual-spatial reasoning abilities of humans and artificial agents. It features a fully customizable sliding tile puzzle simulator using 3D geoms and a natural language API, allowing large vision-language models (LVLMs) to interact with the scene. The benchmark supports evaluation through both vision modality and text-based representations of geoms and their coordinates. The sliding geom puzzle challenges agents to demonstrate visual-spatial scene understanding and effective spatial planning capabilities.


<img src="Resources/README/sliding_geom_puzzle_viz.gif" alt="Sliding Geom Puzzle" width="700"/>


## Table of Contents
1. [Features](#joystick-features)
2. [Environments](#video_game-environments)
3. [Results](#test_tube-results)
4. [Overview](#mount_fuji-overview)
5. [Setup](#package-setup)
6. [Quick Start](#rocket-quick-start)
7. [Citation](#bookmark-citation)
8. [Contact](#mailbox_with_mail-contact)

## :joystick: Features
### Benchmarking
- Multi-modal evaluation of visual-spatial reasoning in large vision-language models (LVLMs).
- Includes an LVLM API for integrating models as agents in interactive puzzle-solving tasks.
- Highly customizable with automated tools for testing and evaluation.

### Simulation
- A web app with a graphical user interface (GUI) designed for human baseline participants.
- Fully operational out of the box, with no installation or dependency requirements.
- Flexible deployment: run locally or host online on a server setup.

### Puzzle Problem Datasets
- Generate custom datasets of interactive Sliding Geom Puzzles.
- Each puzzle configuration features an animated minimal move sequence (computed using A*) to illustrate its complexity.
- Pre-generated test datasets of puzzle configurations are available for immediate use.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## :video_game: Environments

### Sliding Geom Puzzle (SGP)
This is a 3D implementation of the generalized sliding tile puzzle (GSLP), where agents have to move geoms from an initial to a goal configuration. It allows agents to move geoms in the cardinal directions (von Neumann neighborhood) by text prompts, referencing their color and shape.

<img src="Resources/README/SGP_panorama.gif" alt="Sliding Geom Puzzle" width="900"/>

### Sliding Tile Puzzle (STP)
This is a 3D implementation of the classic sliding tile puzzle (STP) commonly known as 14-15-Puzzle or n-Puzzle. Agents have to move tiles from an initial to a goal configuration. It allows agents to move tiles in the cardinal directions (von Neumann neighborhood) by text prompts, referencing their tile number.

<img src="Resources/README/STP_panorama.gif" alt="Sliding Geom Puzzle" width="900"/>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## :test_tube: Results
These are preliminary results of the most recent evaluation (Dez. '24) on the SGP problem. For more details, look at our publication [Link here].

<img src="Resources/README/results.png" alt="Sliding Geom Puzzle" width="900"/>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## :mount_fuji: Overview

The repository is organized into four main directories:

1. **Source**: Includes all source code for:
    1. [Configuration](/Source/Configuration): Generating puzzle configuration datasets.
    2. [Experiment](/Source/Experiment): Running experiments.
    3. [Evaluation](/Source/Evaluation): Evaluating experiments.
    4. [Utility](/Source/Utility): Indepdent utility scripts for the repository.
    5. [iVISPAR](/Source/iVISPAR): The Unity project for the web app in iVISPAR.
2. **Data**: Contains all data used or generated by the source code, including
     1. [Configuration datasets](/Data/Configs/),
     2. [Experiment data](/Data/Experiments/),
     3. [Task instructions](Data/Instructions/),
     4. [API keys](/Data/API-keys/),
     5. [Params](/Data/Params/),
     6. [Experiment results](/Data/Resulsts/).
3. **iVISPAR**: Holds the compiled web app.
4. **Resources**: Contains metadata files for the repository.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## :package: Setup

iVISPAR has minimal dependencies and can be set up and run in just a few simple steps.

### Clone

Clone the repository 

```
# Clone the repository
git clone https://github.com/SharkyBamboozle/iVISPAR.git
cd iVISPAR
```

### Conda

iVISPAR uses Python 3. You can find the list of Python dependencies in [Resources/environment.yml](Resources/environment.yml). We recommend downloading Anaconda and making a conda environment with

iVISPAR runs on Python 3. You can find the list of required Python dependencies in  [Resources/environment.yml](Resources/environment.yml). We recommend using Anaconda to create a conda environment

```
# Create new conda env
conda env create -f Resources/environment.yml
conda activate conda_env_iVISPAR
```

### Python
You can find an example of how to run the code in [Source/main.py](Source/main.py). It will open the iVISPAR web app on your browser and copy the client ID into the Python console.

```
# Run main script
cd Source
python main.py
```

### Unity

The project comes with the compiled [iVISPAR](iVISPAR) web app, which should work out of the box on any common OS with a browser installed. The web app is written in C# with Unity and its code source code is available under [Source/iVISPAR](Source/iVISPAR). It is unnecessary to code C# or compile the Unity project to run experiments with iVISPAR.    

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## :rocket: Quick Start

 We have prepared comprehensive **Getting Started Guides**  with step-by-step instructions to help you get started quickly.

1. [How to run experiments](Resources/HowTo/how_to_run_experiments.md)
2. [How to generate configurations](Resources/HowTo/how_to_generate_configurations.md)
3. [How to evaluate results](Resources/HowTo/how_to_evaluate_results.md)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## :bookmark: Citation

You can find our publication on iVISPAR on [arXiv](https://arxiv.org/abs/xxxx.xxxxx). If you use iVISPAR in your work, we kindly ask you to cite our paper:

*Mayer J., Nezami F., Ballout M., Serwan J., Bruni E. (2024). iVISPAR: An Interactive Visual-Spatial Reasoning Benchmark for LVLMs. arXiv preprint arXiv:xxxx.xxxxx.*


### BibTeX
```bibtex
@inproceedings{ivispar24,
  title ={{iVISPAR: An Interactive Visual-Spatial Reasoning Benchmark for LVLMs}},
  author={Julius Mayer and Farbod Nezami and Mohamad Ballout and Serwan Jassim and Elia Bruni},
  journal={arXiv preprint arXiv:xxxx.xxxxx},
  year = {2024},
  url  = {https://arxiv.org/abs/xxxx.xxxxx}
}
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## :mailbox_with_mail: Contact

Julius Mayer - research@jmayer.ai

<p align="right">(<a href="#readme-top">back to top</a>)</p>
