import re
from collections import deque
from typing import Tuple, List, Dict, Union

from src_python.core.utility.json_file_handler import JsonFileHandler


class ActionModel:
    def __init__(self, raw_prompt: str, split_at: str = "action:", num_actions: int = None, game_params = None):
        """
        Create an ActionModel object from a raw model output prompt.

        Args:
            raw_prompt (str): The model's raw output string.
            split_at (str): Marker string where the action part starts in the prompt.
            num_actions (int, optional): Expected number of actions to validate against.
        """
        self.raw_prompt = raw_prompt
        self.split_at = split_at
        self.cleaning_rules = self._load_regex_rules("action_cleaning_regex")

        # Parse and clean
        self.cleaned_action_str, self.thoughts = self._parse_and_clean(raw_prompt)
        self.action_queue = self._initialize_action_queue(self.cleaned_action_str)
        self.action_mistakes = {"missing_action": [], "extra_action": []}

        # Validate number of actions if requested
        if num_actions is not None:
            self._check_action_count(expected_count=num_actions)

    @property
    def action_data(self) -> str:
        return self.cleaned_action_str

    def _load_regex_rules(self, file_signature: str) -> List[Tuple[str, str, int]]:
        flag_map = {
            "MULTILINE": re.MULTILINE,
            "IGNORECASE": re.IGNORECASE,
            0: 0
        }
        raw_rules = JsonFileHandler.load_json(file_signature=file_signature, source_dir="settings")
        return [(r["pattern"], r["replacement"], flag_map.get(r["flags"], 0)) for r in raw_rules]

    def _parse_and_clean(self, response: str) -> Tuple[str, str]:
        cleaned_response = response.replace("\n", " ").replace("*", "").replace("#", "").strip().lower()
        split_index = cleaned_response.rfind(self.split_at.lower())

        if split_index != -1:
            thoughts = cleaned_response[:split_index].strip()
            action = cleaned_response[split_index + len(self.split_at):].strip()
        else:
            thoughts = response
            action = "No valid action found."

        cleaned_action = self._shape_mapping(self._clean_action_string(action))
        return cleaned_action, thoughts

    def _clean_action_string(self, action: str) -> str:
        for pattern, repl, flags in self.cleaning_rules:
            action = re.sub(pattern, repl, action, flags=flags)
        return action.strip()

    def _shape_mapping(self, response: str) -> str:
        shape_map = {
            "circle": "sphere",
            "square": "cube",
            "triangle": "pyramid",
            "hexagon": "cylinder"
        }
        for shape_2d, body_3d in shape_map.items():
            response = response.replace(shape_2d, body_3d)
        return response

    def _initialize_action_queue(self, action_string: str) -> deque:
        actions = [a.strip() for a in action_string.split(',') if a.strip()]
        return deque(actions)

    def _check_action_count(self, expected_count: int) -> None:
        """
        Compare the number of parsed actions to the expected count.
        Records missing or extra actions in action_mistakes.
        """
        actual_count = len(self.action_queue)
        if actual_count < expected_count:
            missing = expected_count - actual_count
            self.action_mistakes["missing_action"].extend(["missing"] * missing)
        elif actual_count > expected_count:
            extra = actual_count - expected_count
            self.action_mistakes["extra_action"].extend(["extra"] * extra)

    def pop_action(self) -> Union[str, None]:
        """
        Pops the next action from the queue.

        Returns:
            str: Next action if available, otherwise None.
        """
        if self.action_queue:
            return self.action_queue.popleft()
        return None

    @property
    def has_actions_remaining(self) -> bool:
        """
        Checks if there are still actions in the queue.

        Returns:
            bool: True if actions remain, False otherwise.
        """
        return bool(self.action_queue)

    @property
    def is_empty(self) -> bool:
        """
        Checks if there are still actions in the queue.

        Returns:
            bool: True if actions remain, False otherwise.
        """
        return not bool(self.action_queue)

    def to_dict(self) -> Dict[str, Union[List[str], str, Dict]]:
        """
        Return parsed action and thoughts as a dictionary.
        """
        return {
            "actions": list(self.action_queue),
            "thoughts": self.thoughts.strip(),
            "action_mistakes": self.action_mistakes
        }
