import re
from typing import Tuple, List, Dict

from src_python.core.utility.json_file_handler import JsonFileHandler


class ActionModel:
    def __init__(self, raw_prompt: str, split_at: str = "action: move "):
        """
        Create an ActionModel object from a raw model output prompt.

        Args:
            raw_prompt (str): The model's raw output string.
            split_at (str): Marker string where the action part starts in the prompt.
        """
        self.raw_prompt = raw_prompt
        self.split_at = split_at
        self.cleaning_rules = self._load_regex_rules("action_cleaning_regex")
        self.cleaned_action_str, self.thoughts = self._parse_and_clean(raw_prompt)

    @property
    def action_data(self) -> str:
        return self.cleaned_action_str

    def _load_regex_rules(self, file_signature: str) -> List[Tuple[str, str, int]]:
        """
        Load regex cleaning rules from a JSON file.

        Each rule in JSON must have:
        - pattern (str)
        - replacement (str)
        - flags (str or int)
        """
        flag_map = {
            "MULTILINE": re.MULTILINE,
            "IGNORECASE": re.IGNORECASE,
            0: 0
        }
        raw_rules = JsonFileHandler.load_json(file_signature=file_signature, source_dir="settings")
        return [(r["pattern"], r["replacement"], flag_map.get(r["flags"], 0)) for r in raw_rules]

    def _parse_and_clean(self, response: str) -> Tuple[str, str]:
        """
        Extract and clean the action and thoughts from a raw prompt string.
        """
        cleaned_response = response.replace("\n", " ").replace("*", "").replace("#", "").strip().lower()
        split_index = cleaned_response.rfind(self.split_at.lower())

        if split_index != -1:
            thoughts = cleaned_response[:split_index].strip()
            action = "move " + cleaned_response[split_index + len(self.split_at):].strip()
        else:
            thoughts = response
            action = "No valid action found."

        cleaned_action = self._shape_mapping(self._clean_action_string(action))
        return cleaned_action, thoughts

    def _clean_action_string(self, action: str) -> str:
        """
        Apply regex cleaning rules to the action string.
        """
        for pattern, repl, flags in self.cleaning_rules:
            action = re.sub(pattern, repl, action, flags=flags)
        return action.strip()

    def _shape_mapping(self, response: str) -> str:
        """
        Replace 2D shape terms with corresponding 3D body names.
        """
        shape_map = {
            "circle": "sphere",
            "square": "cube",
            "triangle": "pyramid",
            "hexagon": "cylinder"
        }
        for shape_2d, body_3d in shape_map.items():
            response = response.replace(shape_2d, body_3d)
        return response

    def to_dict(self) -> Dict[str, List[str] or str]:
        """
        Return parsed action and thoughts as a dictionary.
        """
        actions = [a.strip() for a in self.cleaned_action_str.split(',') if a.strip()]
        return {
            "actions": actions,
            "thoughts": self.thoughts.strip()
        }
