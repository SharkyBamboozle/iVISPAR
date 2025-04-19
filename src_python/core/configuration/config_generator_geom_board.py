from itertools import product
from collections import defaultdict

from tqdm import tqdm
import random
import numpy as np
import hashlib
from collections import Counter

from .config_model_new import ConfigModel
from .config_generator import ConfigGenerator
from .param_model_geom_board import GeomBoardGameParamsModel

from src_python.core.environment.tmp.find_shortest_move_sequence import calculate_manhattan_heuristic
from src_python.core.environment.game_solver_geom_board import GameSolverGeomBoard
from src_python.core.environment.game_system_geom_board import GameSystemGeomBoard


@ConfigGenerator.register_subclass("geom_board")
class ConfigGeneratorGeomBoard(ConfigGenerator):
    """Configuration generator for the 'geom_board' puzzle game."""

    game_params_model = GeomBoardGameParamsModel

    @staticmethod
    def state_to_md5(start_state: str, goal_state: str) -> str:
        """Create an MD5 hash from the states."""
        state_str = ','.join(map(str, start_state + goal_state))
        return hashlib.md5(state_str.encode()).hexdigest()

    @staticmethod
    def sample_board_states(board_width: int, board_height: int, num_geoms: int) -> np.ndarray:
        """Generates a board checkpoint_state where multiple geoms may stack at the same position."""

        # Sample positions with replacement (allows stacking)
        positions = np.random.choice(board_width * board_height, num_geoms, replace=True).astype(np.int8)

        # Count how many objects land on each position to compute stack levels
        stack_levels = np.array([np.sum(positions[:i] == pos) for i, pos in enumerate(positions)], dtype=np.int8)

        # Assign random orientations (1–12)
        orientations = np.random.randint(1, 13, size=num_geoms, dtype=np.int8)

        # Final shape: (num_geoms, 3)
        return np.stack((positions, stack_levels, orientations), axis=1)

    def generate_goal_state(self, start_state, path_length,
                            game_system: GameSystemGeomBoard, game_solver: GameSolverGeomBoard):
        # -> tuple[StateType, StateType, list[str]]

        while True:
            # Sample actions
            valid_actions = [action for action, enabled in self.game_params.action_set.items() if enabled]
            actions = [random.choice(valid_actions) for _ in range(path_length)]

            print("")
            # First loop: apply flip and move
            goal_state = start_state.copy()
            for action in actions:
                if action in {"flip", "move"}:
                    goal_state = game_system.apply_action_randomly(goal_state, action)


            # Second loop: apply remove actions with random choice
            for action in actions:
                if action == "addrmv":
                    if np.random.rand() < 0.5:
                        goal_state = game_system.apply_action_randomly(goal_state, "remove")
                    else:
                        start_state = game_system.apply_action_randomly(start_state, "remove")


            print("Start")
            print(start_state)
            print("Goal")
            print(goal_state)
            print("")

            optimal_actions = game_solver.solve(start_state, goal_state)

            print("")
            print(actions)
            print(optimal_actions)



            # self.config_logger.info(c1 - c2)  # Actions in actions1 but not in actions2
            # self.config_logger.info(c2 - c1)  # Actions in actions1 but not in actions2

            if len(optimal_actions) == len(actions):
                break
            elif len(optimal_actions) < len(actions):
                print("optimal actions too short")
                # self.config_logger.info(c1 - c2)  # Actions in actions1 but not in actions2
            elif len(optimal_actions) > len(actions):
                # self.config_logger.info(c2 - c1)  # Actions in actions1 but not in actions2
                raise ValueError(f"This should not be possible, then there is a bug here")

        return start_state, goal_state, actions

    def generate_dataset(self) -> None:
        #self.config_logger.info("start generating episode configuration dataset")

        combinations = product(
            range(*self.game_params.board_width_range.as_tuple),
            range(*self.game_params.board_height_range.as_tuple),
            range(*self.game_params.num_geoms_range.as_tuple),
            range(*self.game_params.shortest_solution_path_range.as_tuple),
        )

        # Convert combinations generator to a list once
        combinations_list = list(combinations)

        # Compute total combinations safely
        total_combinations = (
                len(combinations_list) *
                len(range(*self.game_params.path_interference_factor_range.as_tuple)) *
                self.game_params.instances_per_configuration
        )

        for board_width, board_height, num_geoms, shortest_path_length in tqdm(
                combinations_list , total=total_combinations, desc="Generating Samples"):

            #self.config_logger.info(
            #    f"Starting new configuration batch: Board({board_width}x{board_height}), "
            #    f"Geoms={num_geoms}, ShortestPath={shortest_path}"
            #)

            seen_state_combinations = set()

            # Initialize bins to track instances per path_interference factor
            path_interference_counts = defaultdict(int)

            # Instantiate GameDynamics
            game_system = GameSystemGeomBoard(board_width, board_height, self.game_params.action_set)
            game_solver = GameSolverGeomBoard(game_system, self.game_params.action_set)

            # Ensure all expected bins exist with a count of 0
            for interference_factor in range(*self.game_params.path_interference_factor_range.as_tuple):
                path_interference_counts[interference_factor] = 0

            # Loop until all bins are filled
            while not all(count >= self.game_params.instances_per_configuration for count in
                          path_interference_counts.values()):


                # -------------------------------#
                #         Compute States         #
                # -------------------------------#

                #Sample a start board checkpoint_state
                start_state = self.sample_board_states(board_width, board_height, num_geoms)

                # Generate a goal checkpoint_state from sampled actions
                start_state, goal_state, actions = self.generate_goal_state(start_state,
                                                                    shortest_path_length, game_system, game_solver)

                # Compress the checkpoint_state combination using zlib
                compressed_state_combination = self.state_to_md5(start_state, goal_state)
                if compressed_state_combination in seen_state_combinations: continue
                seen_state_combinations.add(compressed_state_combination)

                # -------------------------------#
                #       Assemble ConfigModel     #
                # -------------------------------#
                # Prepare geometry samples
                geoms = [(shape, color) for shape in self.game_params.shape_set
                         for color in self.game_params.color_set]
                geoms_sample = random.sample(geoms, num_geoms)

                config = ConfigModel(
                    config_instance_id="ICML_b_4_g_2_c1_2_c2_0_i_3",
                    experiment_type="SlidingGeomPuzzle",
                    complexity_c1=2,
                    complexity_c2=0,
                    grid_size=4
                )
                config.add(goal_state, key="goal_state")
                config.add(start_state, key="start_state")
                config.add(geoms_sample, key="geom_sample")
                config.add(self.game_params.action_set.items(), key="action_set")
                config.add(actions, key="optimal_path")

                config.save_to_json(self.dataset_dir)