"""
Layout sizing, border radii, padding, and shadow tokens.
"""

import flet as ft

# Plate Card Sizing & Appearance
PLATE_WIDTH = 580
PLATE_HEIGHT = 350
PLATE_BORDER_RADIUS = 18
PLATE_PADDING = 24
PLATE_BORDER_COLOR = ft.Colors.INDIGO_100
PLATE_BG_COLOR = ft.Colors.WHITE

# Box Shadows
PLATE_BOX_SHADOW = ft.BoxShadow(
    spread_radius=0,
    blur_radius=16,
    color=ft.Colors.with_opacity(0.10, ft.Colors.INDIGO_900),
    offset=ft.Offset(0, 6),
)

CARD_BOX_SHADOW = ft.BoxShadow(
    spread_radius=0,
    blur_radius=4,
    color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
    offset=ft.Offset(0, 2),
)
