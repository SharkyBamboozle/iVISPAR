<div id="readme-top"></div>


![Build](https://img.shields.io/github/actions/workflow/status/username/repository/build.yml?branch=main)


# iVISPAR

The interactive-Visiual-Spatial-Reasoning (iVISPAR) benchmark tests the visiual-spatial-reasoning of humans and artificial agents. It features a fully customizable version of the popular sliding tile puzzle with a 3D simulator and a natural language API that allows large vision language models (LVLMs) to interact with the scene.


<img src="Resources/sliding_geom_puzzle_viz.gif" alt="Sliding Geom Puzzle" width="500"/>


## Table of Contents
1. [Features](#joystick-features)
2. [Overview](#mount_fuji-overview)
3. [Quick Start](#rocket-quick-start)
4. [Setup](#package-setup)
5. [Citation](#bookmark-citation)
6. [Contact](#mailbox_with_mail-contact)



## :joystick: Features

### Benchmarking
- Multi-modal evaluation of visual-spatial reasoning in LVLMs
- use LVLMs as agents in interactive puzzle solving task
- highly parameterizable, with automated testing and evaluation
### Puzzle problem datasets
- generate your own dataset of interactive Sliding Geom Puzzles
- each individual puzzle configuration comes with an animated minimal move sequence computed by A*, to show this puzzle instance’s complexity
- additionally, pre-generated test dataset of puzzle configurations are provided
### Simulation
- WebApp with GUI for LVLMs and human baseline participants
- works out of the box, easy setup, no installation or dependencies necessary
- can run locally or online on a server setup
    

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## :mount_fuji: Overview

There are four directories:

1. **Data**: contains all data used by the source code, from the configuration datasets in configs, the experiment data, LLM task instructions and API-keys, to the results
2. **iVISPAR**: contains the compiled WebApp. 
3. **Resources**: holds some meta files for the repository
4. **Source**: contains all source code for generating a dataset of puzzle configurations in COnfiguration, running the experiment in /experimetn and evaluating the experiments in Evalaution, as well as the Unity project for the WebApp in iVISPAR.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## :rocket: Quick Start

You can find an example of how to run the code in source/main.py. It will open the iVISPAR web app on your browser and copy the client ID into the Python console. We've prepared a comprehensive **Getting Started Guide** with instructions to help you get started with the iVISPAR benchmark.

1. [How to run experiments](Resources/how_to_run_experiments.md)
2. [How to generate configurations (optional)](Resources/how_to_generate_configurations.md)
3. [How to evaluate the results](Resources/how_to_evaluate_results.md)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## :package: Setup

### Clone

You can clone our repository with 

```
$ git clone https://github.com/askforalfred/alfred.git alfred
$ export ALFRED_ROOT=$(pwd)/alfred
```

### Conda

The experiment uses Python 3. You can find the list of Python dependencies in /Resources/environment.yaml. We recommend to download Anaconda and make a conda environment with

```
$ conda env create -f resources/environment.yml
```

### Unity

The WebApp is written in C# with Unity and it’s code source code is available under /source/iVISPAR. The project comes with the compiled WebApp, which should work out of the box on any common OS with a browser installed. It is unnecessary to code C# or compile the Unity project to run experiments with iVISPAR. To extend the iVISPAR simulation, the C# is included as a Unity project in source/iVISPAR.    

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## :bookmark: Citation

We've published our latest paper on iVISPAR, which you can find on [ArXiv](https://arxiv.org/). If you use iVISPAR in your research, please cite our paper:

*Mayer J., Nezami F., Ballout M., Serwan J., Bruni E. (2024). iVISPAR: An Interactive Visual-Spatial Reasoning Benchmark for LVLMs. arXiv preprint arXiv:xxxx.xxxxx.*

```
@inproceedings{iVisapar24,
  title ={{iVISPAR: An Interactive Visual-Spatial Reasoning Benchmark for LVLMs}},
  author={Julius Mayer and Farbod Nezami and Mohamad Ballout and Serwan Jassim and Elia Bruni},
  booktitle = {ICML 2025 Benchmarking,
  year = {2024},
  url  = {https://arxiv.org/abs/xxxx.xxxxx}
}
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## :mailbox_with_mail: Contact

Julius Mayer - research@jmayer.ai

<p align="right">(<a href="#readme-top">back to top</a>)</p>
