"""
Main entry point to launch the experiment using the geom board puzzle setup.
Minimal interface: adjust the experiment parameters signature to change the config set.
"""

import asyncio

from core.experiment.experiment_runner import ExperimentRunner
import core.experiment.experiment_runner_geom_board # Required for ExperimentRunner's factory pattern


async def main(experiment_params_signature: str) -> None:
    runner = ExperimentRunner(experiment_params_signature)

    print(f"Start running experiments") #TODO replace with logging
    experiment_id = await runner.run_episodes()

    # TODO: replace with logging.info(f"Experiment {experiment_id} finished.")
    print(f"Finished running experiments for experiment ID: {experiment_id}")

    # TODO: Add quick summary and plotting of experiments

if __name__ == "__main__":
    experiment_params_signature = "params_geom_board_experiment_example"
    asyncio.run(main(experiment_params_signature=experiment_params_signature))
