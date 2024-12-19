<div id="readme-top"></div>



![Task_multimodal](https://img.shields.io/badge/Task-multimodal-gray?style=flat&labelColor=red)
![Task_visual_reasoning](https://img.shields.io/badge/Task-visual_reasoning-gray?style=flat&labelColor=red)
![Task_visual_spatial_reasoning](https://img.shields.io/badge/Task-visual_spatial_reasoning-gray?style=flat&labelColor=red)<br>

![Model_Claude](https://img.shields.io/badge/Model-Claude-gray?logo=claude&style=flat&labelColor=blue)
![Model_Claude](https://img.shields.io/badge/Model-GPT4-gray?logo=openai&style=flat&labelColor=blue)
![Model_Claude](https://img.shields.io/badge/Model-Gemini-gray?logo=googlegemini&style=flat&labelColor=blue)<br>

![Environment_sliding_tile_puzzle](https://img.shields.io/badge/Environment-sliding_tile_puzzle-gray?style=flat&labelColor=darkgreen)
![Environment_sliding_geom_puzzle](https://img.shields.io/badge/Environment-sliding_geom_puzzle-gray?style=flat&labelColor=darkgreen)<br>



# :jigsaw: iVISPAR
Large Vision-Language Models (LVLMs) are known to face challenges with spatial reasoning and visual alignment. iVISPAR (Interactive Visual-Spatial Reasoning benchmark) addresses these limitations by providing an interactive environment designed to evaluate the capabilities of LVLMs as agents in this context.

The benchmark focuses on a specific scenario — a variation of the generalized Sliding Tile Puzzle, a classic problem that requires logical planning, spatial awareness, and multi-step problem-solving. iVISPAR features a fully customizable Sliding Tile Puzzle simulator that uses 3D geometric shapes (geoms) and a natural language API, enabling LVLMs to interact directly with the scene by prompting actions.

The benchmark supports evaluation through both visual modality and text-based representations of geoms and their coordinates. This dual approach allows for a comprehensive assessment of visual-spatial scene understanding and spatial planning capabilities. To gauge model performance, agents are compared against a human baseline, random agents, and the A* algorithm, providing insight into the problem's complexity ceiling and the alignment of the model's spatial reasoning with human logic.

<div align="center">
  <img src="Resources/README/sliding_geom_puzzle_viz.gif" alt="Sliding Geom Puzzle" width="700"/>
  <p><em>Figure 1: Visualization of GPT-4's interaction with the Sliding Geom Puzzle (SGP).</em></p>
</div>

This is our submission to the [Berkley LLM Agents Hackathon 2024](https://rdi.berkeley.edu/llm-agents-hackathon/), please find our submission [video on YouTube](https://www.youtube.com/watch?v=6s1ova1tgwo).

## Table of Contents
1. [Features](#joystick-features)
2. [Environments](#video_game-puzzle-environments)
3. [Results](#test_tube-results)
4. [Overview](#mount_fuji-overview)
5. [Setup](#package-setup)
6. [Quick Start](#rocket-quick-start)
7. [Citation](#bookmark-citation)
8. [Contact](#mailbox_with_mail-contact)

## :joystick: Features
### Benchmarking
- **Multi-modal evaluation:** Assess visual-spatial reasoning in LVLMs using both visual and text-based representations.
- **LVLM agent integration:** Includes an LVLM API to seamlessly integrate models as agents for interactive puzzle-solving tasks.
- **AI agent integration:** Provides benchmark comparisons with solutions from A* agents and random agents to establish performance baselines.
- **Customizable and automated:** Offers high customizability with automated tools for testing, evaluation, and comparative analysis.

### Simulation
- **Featuring two puzzle scenarios:** Includes two distinct puzzle scenarios, Sliding Geom Puzzle (SGP) and Sliding Tile Puzzle (STP), with a prompt-based API, allowing LVLM agents to interact with the environment through an action-perception loop.
- **Ready-to-use:** Fully operational right out of the box — no additional installation or dependency requirements.
- **Interactive web app:** A browser-based graphical user interface (GUI) for human participants to interact with the puzzles, enabling human baseline comparisons.
- **Flexible deployment:** Run the simulation locally or host it on a server for online access and remote experimentation.
- **Future addition:** Incorporation of additional spatial reasoning puzzles to enable more comprehensive evaluation of visual-spatial reasoning capabilities.
   
### Datasets
- **Custom puzzle generation:** Generate interactive Sliding Tile Puzzle or Sliding Geom Puzzle datasets tailored to specific experimental needs.
- **Move sequence visualization:** Each puzzle configuration includes an animated minimal move sequence (computed using A*) to illustrate puzzle complexity.
- **Pre-generated datasets:** Access a library of pre-generated test datasets for quick experimentation and evaluation.
- **Future addition:** Incorporation of human performance data to define the problem's complexity ceiling and analyze the alignment of model-based spatial reasoning with human logic.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## :video_game: Puzzle Environments

### Sliding Geom Puzzle (SGP)
This is a 3D implementation of the generalized sliding tile puzzle (GSTP), where agents are tasked with moving geoms from a randomly sampled initial to a randomly sampled goal state. Agents can move tiles in the four cardinal directions (following the von Neumann neighborhood) using text prompts that reference their color and shape. Configuration options include board size, number of geoms, shapes and colors of geoms, camera angles, visibility of board labels, representation types (vision or text), complexity (minimal move sequence length), and more.

<div align="center">
  <img src="Resources/README/SGP_panorama.gif" alt="Sliding Geom Puzzle" width="900"/>
  <p><em>Figure 2: Visualization of Sliding Geom Puzzle (SGP) configuration examples of varying sizes solved by A*.</em></p>
</div>


### Sliding Tile Puzzle (STP)
This is a 3D implementation of the classic Sliding Tile Puzzle (STP), commonly known as the 15-Puzzle or n-Puzzle. Agents are tasked with moving tiles from a randomly sampled initial configuration to a goal state where the numbered tiles are arranged in order. Agents can move tiles in the four cardinal directions (following the von Neumann neighborhood) using text prompts that reference the tile number. STP is a well-known NP-hard problem. Configuration options include board size, number of tiles, camera angles, visibility of board labels, representation types (vision or text), complexity (minimal move sequence length), and more.

<div align="center">
  <img src="Resources/README/STP_panorama.gif" alt="Sliding Geom Puzzle" width="900"/>
  <p><em>Figure 3: Visualization of Sliding Tile Puzzle (STP) configuration examples of varying sizes solved by A*.</em></p>
</div>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## :test_tube: Results
Preliminary results from the latest evaluation (Dec. '24) on the SGP problem for the Berkeley LLM Agents Hackathon are shown below. For more details, see [Citation](#bookmark-citation).

<div align="center">
  <img src="Resources/README/results.png" alt="Sliding Geom Puzzle" width="900"/>
  <p><em>Figure 4: Preliminary results from the most recent evaluation (Dec. '24) on the SGP problem for the Berkeley LLM Agents Hackathon.</em></p>
</div>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## :mount_fuji: Overview

The repository is organized into four main directories:

### **(1) Source**: 
Contains all the source code required to generate datasets, run experiments, and evaluate results.
    
1. **[Configuration](/Source/Configuration):** Scripts for generating puzzle configuration datasets.
2. **[Experiment](/Source/Experiment):** Code for running experiments based on the generated configurations.
3. **[Evaluation](/Source/Evaluation):** Tools for analyzing and evaluating experimental results.
4. **[Utility](/Source/Utility):** Independent utility scripts that add functions for the project.
5. **[iVISPAR](/Source/iVISPAR):** The Unity project files for the iVISPAR web application.
    
### **(2) Data**:
Contains all data used or generated by the source code, including
 1. **[Configs](/Data/Configs/):** Contains puzzle configuration files used as input for experiments.
 2. **[Experiments](/Data/Experiments/):** Raw data generated while running experiments, such as logs and execution traces.
 3. **[Instructions](Data/Instructions/):** Instructions or prompts used to guide AI agents or human participants.
 4. **[API keys](/Data/API-keys/):** Contains the file to set your API keys (note: ensure this directory is properly secured and excluded from any public commits).
 5. **[Params](/Data/Params/):** Parameter files used to configure and customize experiments and agent behavior.
 6. **[Results](/Data/Results/):** Final output of the experiments, including performance metrics, logs, and summaries.

### **(3) iVISPAR**: 
This directory contains the compiled version of the iVISPAR web app, ready to be launched in your browser. It requires no additional compilation or modification. However, it must connect to the experiment via Python to receive configuration files.

### **(4) Resources**: 
Contains metadata files and supporting resources for the project. This may include environment files, dependency lists, and documentation files.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## :package: Setup

iVISPAR has minimal dependencies and can be easily set up and run in just a few simple steps.

### Clone

Clone the repository.

```bash
git clone https://github.com/SharkyBamboozle/iVISPAR.git
cd iVISPAR
```

### Conda

iVISPAR runs on Python 3. You can find the list of required Python dependencies in [Resources/environment.yml](Resources/environment.yml). We recommend using [Anaconda](https://www.anaconda.com/) to create a new conda environment.

```bash
conda env create -f Resources/environment.yml
conda activate conda_env_iVISPAR
```

### Python

You can find an example of how to run the code in [Source/main.py](Source/main.py). First, the script generates a minimal dataset of configuration files. Next, iVISPAR is launched in your web browser and prompts you to copy the client ID from the web app into the Python console. Once connected, an AI agent, acting as a stand-in for your LVLMs API connection, executes the optimal path. Finally, the results are evaluated and plotted automatically. For more details, see [Quick Start](#rocket-quick-start).

```bash
cd Source
python main.py
```

### Unity

The project includes the compiled [iVISPAR](iVISPAR) web app, which works out of the box on any common operating system with a web browser installed. The web app is built with C# using Unity, and its source code is available in [Source/iVISPAR](Source/iVISPAR). No knowledge of C# or compilation of the Unity project is required to run experiments with iVISPAR. We also provide a fully online working version for human experiments.


[http://ivispar.microcosm.ai/](https://ivispar.microcosm.ai/?human=true)


<div align="center">
  <img src="Resources/README/webapp.png" alt="webapp image" width="500"/>
  <p><em>Figure 5: Web app with UI for human experiments.</em></p>
</div>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## :rocket: Quick Start

 We have prepared comprehensive **Getting Started Guides**  with step-by-step instructions to help you get started quickly.

1. [How to run experiments](Resources/HowTo/how_to_run_experiments.md)
2. [How to generate configurations](Resources/HowTo/how_to_generate_configurations.md)
3. [How to evaluate results](Resources/HowTo/how_to_evaluate_results.md)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## :bookmark: Citation

Please find our publication on iVISPAR on [arXiv](https://arxiv.org/abs/xxxx.xxxxx). If you use iVISPAR in your work, we kindly ask you to cite our paper:

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
