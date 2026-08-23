"""
Theme package exposing colors, badge helpers, dimensions, and shadows.
"""

from .colors import (
    LEVEL_COLORS,
    DEFAULT_LEVEL_COLOR,
    POS_BADGE_COLOR,
    GUIDEWORD_BADGE_COLOR,
    get_level_color,
)
from .dimensions import (
    PLATE_WIDTH,
    PLATE_HEIGHT,
    PLATE_BORDER_RADIUS,
    PLATE_PADDING,
    PLATE_BORDER_COLOR,
    PLATE_BG_COLOR,
    PLATE_BOX_SHADOW,
    CARD_BOX_SHADOW,
)

__all__ = [
    "LEVEL_COLORS",
    "DEFAULT_LEVEL_COLOR",
    "POS_BADGE_COLOR",
    "GUIDEWORD_BADGE_COLOR",
    "get_level_color",
    "PLATE_WIDTH",
    "PLATE_HEIGHT",
    "PLATE_BORDER_RADIUS",
    "PLATE_PADDING",
    "PLATE_BORDER_COLOR",
    "PLATE_BG_COLOR",
    "PLATE_BOX_SHADOW",
    "CARD_BOX_SHADOW",
]
