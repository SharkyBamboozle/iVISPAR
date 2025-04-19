import heapq
import numpy as np

class AStarSolver:
    def __init__(self, heuristic, get_successors, hash_state):
        self.heuristic = heuristic
        self.get_successors = get_successors
        self.hash_state = hash_state

    def solve(self, start_state, goal_state):
        open_set = []
        heapq.heappush(open_set, (0, start_state, []))
        g_score = {self.hash_state(start_state): 0}
        visited = set()

        while open_set:
            _, current, path = heapq.heappop(open_set)
            current_hash = self.hash_state(current)

            if current_hash in visited:
                continue
            visited.add(current_hash)

            if np.array_equal(current[:, :2], goal_state[:, :2]):
                return current, path

            # Provide both current and goal states here
            for action_name, new_state in self.get_successors(current, goal_state):
                new_hash = self.hash_state(new_state)
                tentative_g = g_score[current_hash] + 1
                if new_hash not in g_score or tentative_g < g_score[new_hash]:
                    g_score[new_hash] = tentative_g
                    f_score = tentative_g + self.heuristic(new_state, goal_state)
                    heapq.heappush(open_set, (f_score, new_state, path + [action_name]))

        return start_state, []
