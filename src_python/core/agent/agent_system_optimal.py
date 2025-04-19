class AIAgent(Agent):
    def __init__(self, episode_logger, move_sequence):
        self.episode_logger = episode_logger
        self.move_sequence = move_sequence
        #self.move_sequence.pop(-1)
        self.delay = 0

    def act(self, observation, i):
        if not self.move_sequence:
            logging.warning("AIAgent path empty")
            return "path empty"
        else:
            action = self.move_sequence.pop(0)
            self.episode_logger.info(f"action {action}")
            return action