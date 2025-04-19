import gym
from gym import spaces
import numpy as np

class GeomBoardEnv(gym.Env):
    def __init__(self, board_width, board_height, action_set, num_geoms):
        super().__init__()
        self.game = GameSystemGeomBoard(board_width, board_height, action_set)
        self.board_size = board_width * board_height
        self.num_geoms = num_geoms
        self.action_types = ["move", "flip", "remove", "add"]
        self.directions = ["up", "down", "left", "right"]

        self.action_space = spaces.Tuple((
            spaces.Discrete(len(self.action_types)),
            spaces.Discrete(num_geoms),
            spaces.Discrete(len(self.directions))
        ))

        self.observation_space = spaces.Box(
            low=0,
            high=max(self.board_size, 12),
            shape=(num_geoms, 3),
            dtype=np.int16
        )

        self._state = None
        self._goal_state = None

    def reset(self, *, seed=None, options=None):
        self._state = self._sample_initial_state()
        self._goal_state = self._sample_goal_state(self._state)
        return self._state.copy(), {}

    def step(self, action):
        action_type_id, object_index, direction_id = action
        action_type = self.action_types[action_type_id]
        direction = self.directions[direction_id]

        if not hasattr(self.game.actions, action_type):
            raise ValueError(f"Invalid action type: {action_type}")

        action_fn = getattr(self.game.actions, action_type)
        new_state = action_fn(self._state.copy(), object_index, direction)

        self._state = new_state
        done = self.game.is_goal(new_state, self._goal_state)
        reward = 1.0 if done else 0.0

        return new_state.copy(), reward, done, False, {}

    def render(self, mode="human"):
        print(self._state)

    def _sample_initial_state(self):
        # Replace with your real sampler
        positions = np.random.choice(self.board_size, self.num_geoms, replace=False)
        stacks = np.zeros(self.num_geoms, dtype=np.int8)
        orientations = np.random.randint(1, 13, self.num_geoms)
        return np.stack((positions, stacks, orientations), axis=1)

    def _sample_goal_state(self, start_state):
        return start_state.copy()  # Replace with your real goal logic
