from typing import Dict, Any
from pydantic import Field

from .param_model import BaseGameParamsModel, RangeModel


class GeomBoardGameParamsModel(BaseGameParamsModel):
    """Validates game_params for Geom Board game."""

    board_width_range: RangeModel
    board_height_range: RangeModel
    num_geoms_range: RangeModel
    shortest_solution_path_range: RangeModel
    path_interference_factor_range: RangeModel

    instances_per_configuration: int = Field(..., ge=1)

    action_set: Dict[str, bool]
    shape_set: Dict[str, bool]
    color_set: Dict[str, bool]
