from typing import Tuple, List, Dict, Hashable

class GameSystem:

    def is_goal(self, board_state: dict, goal_state: dict) -> bool:
        """ Simple goal check — checkpoint_state equality. """
        return board_state == goal_state

    def hashable_representation(self, board_state: dict) -> Hashable:
        """ Converts board checkpoint_state into a hashable format. """
        # Example: Convert grid to frozen set of (position, geom) tuples
        return frozenset(board_state.items())

    def deep_copy_state(self, board_state: dict) -> dict:
        """ Deep copy the board checkpoint_state to avoid mutation during action application. """
        return {k: v for k, v in board_state.items()}

    def __hash__(self):
        """ Hashing depends on current checkpoint_state — useful if this system itself is the node in A*. """
        return hash(self.hashable_representation(self.current_state))

    def __eq__(self, other):
        if not isinstance(other, GameSystemGeomBoard):
            return False
        return self.hashable_representation(self.current_state) == other.hashable_representation(other.current_state)

    @property
    def current_state(self) -> dict:
        """ (Optional) This could be wired up to track the 'current' working checkpoint_state if needed. """
        raise NotImplementedError("current_state property must be connected to your actual checkpoint_state tracking if needed.")



