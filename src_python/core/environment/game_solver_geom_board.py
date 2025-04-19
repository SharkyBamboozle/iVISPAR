import numpy as np

from src_python.core.environment.tmp.a_star_solver import AStarSolver


FLIP_TRANSITION_PATHS = {
    1: {2: ['up', 'up'], 3: ['left', 'down', 'left'], 4: ['left', 'left'], 5: ['down'], 6: ['left', 'down'], 7: ['down', 'left'], 8: ['left'], 9: ['up'], 10: ['right', 'up'], 11: ['up', 'right'], 12: ['right']},
    2: {1: ['up', 'up'], 3: ['left', 'left'], 4: ['left', 'up', 'left'], 5: ['up'], 6: ['left'], 7: ['up', 'left'], 8: ['left', 'up'], 9: ['down'], 10: ['right'], 11: ['down', 'right'], 12: ['right', 'down']},
    3: {1: ['left', 'down', 'left'], 2: ['left', 'left'], 4: ['up', 'up'], 5: ['up', 'right'], 6: ['right'], 7: ['up'], 8: ['right', 'up'], 9: ['down', 'left'], 10: ['left'], 11: ['down'], 12: ['left', 'down']},
    4: {1: ['left', 'left'], 2: ['left', 'up', 'left'], 3: ['up', 'up'], 5: ['down', 'right'], 6: ['right', 'down'], 7: ['down'], 8: ['right'], 9: ['up', 'left'], 10: ['left', 'up'], 11: ['up'], 12: ['left']},
    5: {1: ['up'], 2: ['down'], 3: ['left', 'down'], 4: ['left', 'up'], 6: ['down', 'left'], 7: ['left'], 8: ['up', 'left'], 9: ['right'], 10: ['down', 'right'], 11: ['left', 'left'], 12: ['up', 'right']},
    6: {1: ['up', 'right'], 2: ['right'], 3: ['left'], 4: ['up', 'left'], 5: ['right', 'up'], 7: ['left', 'up'], 8: ['up'], 9: ['right', 'down'], 10: ['down'], 11: ['left', 'down'], 12: ['up', 'up']},
    7: {1: ['right', 'up'], 2: ['right', 'down'], 3: ['down'], 4: ['up'], 5: ['right'], 6: ['down', 'right'], 8: ['up', 'right'], 9: ['left', 'left'], 10: ['down', 'left'], 11: ['left'], 12: ['up', 'left']},
    8: {1: ['right'], 2: ['down', 'right'], 3: ['down', 'left'], 4: ['left'], 5: ['right', 'down'], 6: ['down'], 7: ['left', 'down'], 9: ['right', 'up'], 10: ['up', 'up'], 11: ['left', 'up'], 12: ['up']},
    9: {1: ['down'], 2: ['up'], 3: ['right', 'up'], 4: ['right', 'down'], 5: ['left'], 6: ['up', 'left'], 7: ['left', 'left'], 8: ['down', 'left'], 10: ['up', 'right'], 11: ['right'], 12: ['down', 'right']},
    10: {1: ['down', 'left'], 2: ['left'], 3: ['right'], 4: ['down', 'right'], 5: ['left', 'up'], 6: ['up'], 7: ['right', 'up'], 8: ['up', 'up'], 9: ['left', 'down'], 11: ['right', 'down'], 12: ['down']},
    11: {1: ['left', 'down'], 2: ['left', 'up'], 3: ['up'], 4: ['down'], 5: ['left', 'left'], 6: ['up', 'right'], 7: ['right'], 8: ['down', 'right'], 9: ['left'], 10: ['up', 'left'], 12: ['down', 'left']},
    12: {1: ['left'], 2: ['up', 'left'], 3: ['up', 'right'], 4: ['right'], 5: ['left', 'down'], 6: ['up', 'up'], 7: ['right', 'down'], 8: ['down'], 9: ['left', 'up'], 10: ['up'], 11: ['right', 'up']},
}


class GameSolverGeomBoard:

    def __init__(self, game_system, action_set):
        self.game_system = game_system
        self.enabled_actions = [k for k, v in action_set.items() if v]

    def hash_state(self, state):
        return tuple(map(tuple, state))

    def heuristic(self, s, g):
        return np.sum(np.abs(s[:, 0] - g[:, 0]))

    def get_successors(self, current, goal):
        successors = []

        # MOVE actions
        if "move" in self.enabled_actions:
            for i in range(current.shape[0]):
                if current[i, 1] >= 0:  # only movable if on board
                    for direction in ["up", "down", "left", "right"]:
                        new_state = self.game_system.actions["move"](
                            board_state=current.copy(),
                            object_index=i,
                            direction=direction
                        )
                        if self.game_system.is_valid_state(new_state):
                            successors.append((f"move {i} {direction}", new_state))

        # ADD actions
        if "add" in self.enabled_actions:
            for i in range(current.shape[0]):
                if current[i, 1] == -1 and goal[i, 1] >= 0:
                    new_state = current.copy()
                    new_state[i, 0] = goal[i, 0]  # position from goal
                    new_state[i, 1] = goal[i, 1]  # orientation from goal
                    if self.game_system.is_valid_state(new_state):
                        successors.append((f"add {i}", new_state))

        return successors

    def apply_all_removes(self, state, goal):
        actions = []
        for i in range(state.shape[0]):
            if state[i, 1] >= 0 and goal[i, 1] == -1:
                state[i, 1] = -1
                actions.append(f"remove {i}")
        return state, actions

    def flip_orientations(self, state, goal):
        actions = []
        for i in range(state.shape[0]):
            current_ori = state[i, 2]  # assuming orientations are in column 1
            goal_ori = goal[i, 2]
            if state[i, 2] != -1 and current_ori != goal_ori:
                flip_actions = FLIP_TRANSITION_PATHS.get(current_ori, {}).get(goal_ori)
                if flip_actions:
                    actions.extend([f"flip {i} {direction}" for direction in flip_actions])
                    state[i, 2] = goal_ori  # directly update to goal orientation
                else:
                    raise ValueError(f"No flip path from {current_ori} to {goal_ori}")
        return state, actions

    def solve(self, start_state, goal_state):
        state = start_state.copy()
        full_actions = []

        if "addrmv" in self.enabled_actions:
            state, actions = self.apply_all_removes(state, goal_state)
            full_actions.extend(actions)

        if "move" in self.enabled_actions or "addrmv" in self.enabled_actions:
            a_star_solver = AStarSolver(
                heuristic=self.heuristic,
                get_successors=self.get_successors,
                hash_state=self.hash_state
            )
            state, actions = a_star_solver.solve(state, goal_state)
            full_actions.extend(actions)

        if "flip" in self.enabled_actions:
            state, actions = self.flip_orientations(state, goal_state)
            full_actions.extend(actions)

        return full_actions
