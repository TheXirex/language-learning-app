"""
Color palettes and CEFR level badge mappings.
"""

from typing import Optional
import flet as ft

# CEFR Level Color Mappings
LEVEL_COLORS = {
    "A1": ft.Colors.GREEN_700,
    "A2": ft.Colors.GREEN_700,
    "B1": ft.Colors.AMBER_800,
    "B2": ft.Colors.AMBER_800,
    "C1": ft.Colors.DEEP_PURPLE_600,
    "C2": ft.Colors.DEEP_PURPLE_600,
}

DEFAULT_LEVEL_COLOR = ft.Colors.BLUE_GREY_600

# Tag Badges
POS_BADGE_COLOR = ft.Colors.BLUE_700
GUIDEWORD_BADGE_COLOR = ft.Colors.TEAL_700


def get_level_color(level: Optional[str]) -> str:
    """Return a consistent badge color based on CEFR level."""
    if not level:
        return DEFAULT_LEVEL_COLOR
    lvl = str(level).strip().upper()
    return LEVEL_COLORS.get(lvl, DEFAULT_LEVEL_COLOR)
