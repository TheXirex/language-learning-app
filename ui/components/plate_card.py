"""
Flashcard Plate Card Content & Shell Components for Study Sessions.
"""

from typing import Callable, Optional
import flet as ft

from ui.theme import (
    get_level_color,
    POS_BADGE_COLOR,
    GUIDEWORD_BADGE_COLOR,
    PLATE_WIDTH,
    PLATE_HEIGHT,
    PLATE_PADDING,
    PLATE_BORDER_RADIUS,
    PLATE_BORDER_COLOR,
    PLATE_BG_COLOR,
    PLATE_BOX_SHADOW,
)
from ui.utils import open_url


def build_plate_card_content(
    word_data: dict,
    is_flipped: bool,
    study_mode: str = "word_to_def",
) -> ft.Control:
    """
    Build the inner content of a learning plate (Quizlet flashcard),
    rendering either the front or back based on is_flipped and study_mode.
    """
    word_str = word_data.get("word", "")
    definitions = word_data.get("definitions", [])
    raw_url = word_data.get("url")
    target_url = raw_url if raw_url else f"https://dictionary.cambridge.org/dictionary/english/{word_str.lower().replace(' ', '-')}"

    primary_def = definitions[0] if definitions else {}
    level = primary_def.get("level")
    pos = primary_def.get("pos")
    guideword = primary_def.get("guideword")
    def_text = primary_def.get("definition", "No definition available.")
    examples = primary_def.get("examples", [])

    badges = []
    if level:
        badges.append(
            ft.Container(
                content=ft.Text(level, color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                bgcolor=get_level_color(level),
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                border_radius=6,
            )
        )
    if pos:
        badges.append(
            ft.Container(
                content=ft.Text(pos, color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                bgcolor=POS_BADGE_COLOR,
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                border_radius=6,
            )
        )
    if guideword:
        badges.append(
            ft.Container(
                content=ft.Text(guideword, color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                bgcolor=GUIDEWORD_BADGE_COLOR,
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                border_radius=6,
            )
        )

    link_button = ft.IconButton(
        icon=ft.Icons.OPEN_IN_NEW,
        icon_color=ft.Colors.INDIGO_400,
        icon_size=18,
        tooltip="Open Cambridge Dictionary",
        on_click=lambda e, link=target_url: open_url(link),
    )

    if study_mode == "word_to_def":
        show_front = not is_flipped
    else:
        # def_to_word mode
        show_front = is_flipped

    if show_front:
        # FRONT SIDE: Shows purely the target word prominently without level badges, tags, or link button
        return ft.Column(
            [
                ft.Container(),
                ft.Container(
                    content=ft.Text(
                        word_str,
                        size=38,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.INDIGO_900,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                ),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.TOUCH_APP_ROUNDED, size=15, color=ft.Colors.INDIGO_400),
                        ft.Text(
                            "Click plate to reveal definition",
                            size=12,
                            color=ft.Colors.INDIGO_500,
                            weight=ft.FontWeight.W_500,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                ),
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
    else:
        # BACK SIDE: Shows the definition and examples
        examples_col = ft.Column(spacing=4)
        for ex in examples:
            examples_col.controls.append(
                ft.Row(
                    [
                        ft.Text("•", color=ft.Colors.INDIGO_500, size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(ex, italic=True, color=ft.Colors.GREY_800, size=13, expand=True),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                )
            )

        secondary_defs_count = len(definitions) - 1
        secondary_info = None
        if secondary_defs_count > 0:
            secondary_info = ft.Text(
                f"+ {secondary_defs_count} more definition{'s' if secondary_defs_count > 1 else ''} in dictionary",
                size=11,
                color=ft.Colors.BLUE_GREY_600,
                italic=True,
            )

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Row(
                            [
                                ft.Text(word_str, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900),
                                ft.Row(badges, spacing=4),
                            ],
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        link_button,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=1, color=ft.Colors.INDIGO_100),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                def_text,
                                size=15,
                                weight=ft.FontWeight.W_600,
                                color=ft.Colors.BLACK_87,
                            ),
                            examples_col if examples_col.controls else ft.Container(),
                            secondary_info if secondary_info else ft.Container(),
                        ],
                        spacing=8,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    expand=True,
                ),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.TOUCH_APP_ROUNDED, size=15, color=ft.Colors.INDIGO_400),
                        ft.Text("Click plate to flip back to word", size=12, color=ft.Colors.INDIGO_500, weight=ft.FontWeight.W_500),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                ),
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )


def build_plate_card_shell(
    word_data: dict,
    flipped: bool,
    study_mode: str = "word_to_def",
    plate_idx: int = 0,
    on_click: Optional[Callable] = None,
    on_hover: Optional[Callable] = None,
) -> ft.Container:
    """Build the styled card container shell for AnimatedSwitcher."""
    inner_content = build_plate_card_content(word_data, flipped, study_mode)
    return ft.Container(
        key=f"plate_{plate_idx}_{flipped}_{study_mode}",
        content=inner_content,
        width=PLATE_WIDTH,
        height=PLATE_HEIGHT,
        padding=PLATE_PADDING,
        border=ft.Border.all(1.5, PLATE_BORDER_COLOR),
        border_radius=PLATE_BORDER_RADIUS,
        bgcolor=PLATE_BG_COLOR,
        shadow=PLATE_BOX_SHADOW,
        animate_offset=ft.Animation(140, ft.AnimationCurve.EASE_OUT),
        offset=ft.Offset(0, 0),
        alignment=ft.Alignment(0, 0),
        on_click=on_click,
        on_hover=on_hover,
    )
