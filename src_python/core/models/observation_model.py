class ObservationModel:
    def __init__(self, simulation_data: dict, goal_image: str, game_params = None):
        messages = simulation_data.get("messages", [{}])
        payload = simulation_data.get("payload", [""])

        self.board_data = messages[0] if len(messages) > 0 else {}
        self.screenshot = payload[0] if len(payload) > 0 else None
        self.goal_image = goal_image

        self.board_dataa = self.board_data["board_data"]
        self._is_done = self.board_data.get("done", False)
        self._step_num = self.board_data["step_num"]
        self._action =  self.board_data.get("action", "NoneAction")
        self._validity =  self.board_data.get("validity", "NoneValidity")

        self.prompt = "Prompt"
        self.chain_of_thoughts = "CoT"

    @property
    def is_done(self) -> bool:
        return self._is_done

    @property
    def action(self) -> str:
        return self._action

    @property
    def validity(self) -> str:
        return self._validity

    @property
    def step_num(self) -> int:
        return self._step_num

    @staticmethod
    def decode_image_str(image):
        pass