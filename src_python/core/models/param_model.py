from pydantic import BaseModel, Field
from typing import Dict, List, Type, Any

class ConfigModel(BaseModel):
    """Validates general configuration fields."""
    config_id: str
    description: str
    game_type: str
    game_params: Dict[str, Any]  # Leave game_params unvalidated (to be handled in child class)


class RangeModel(BaseModel):
    """Validates a numeric range stored as a list `[min, max]`."""
    range: List[int] = Field(..., min_items=2, max_items=2)

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "RangeModel":
        """Convert `{min, max}` dict to `RangeModel(range=[min, max])`."""
        return cls(range=[data["min"], data["max"]])

    @property
    def min(self) -> int:
        return self.range[0]

    @property
    def max(self) -> int:
        return self.range[1]

    @property
    def as_tuple(self) -> tuple:
        """Returns the range as a tuple `(min, max + 1)` for correct iteration."""
        return self.range[0], self.range[1] + 1


class BaseGameParamsModel(BaseModel):
    """Base class for validating game_params in ConfigGenerator subclasses."""

    @classmethod
    def from_dict(cls: Type["BaseGameParamsModel"], data: Dict[str, Any]) -> "BaseGameParamsModel":
        """
        Automatically convert `{min, max}` dictionaries into `RangeModel` instances.
        This avoids having to write `from_dict()` manually in each subclass.
        """
        model_fields = cls.model_fields.keys()  # Get field names from Pydantic model

        converted_data = {}
        for field_name in model_fields:
            if isinstance(data.get(field_name), dict) and "min" in data[field_name] and "max" in data[field_name]:
                # Convert `{min, max}` dicts into `RangeModel`
                converted_data[field_name] = RangeModel.from_dict(data[field_name])
            else:
                # Pass through non-range fields unchanged
                converted_data[field_name] = data[field_name]

        return cls(**converted_data)
