"""
Word and Definition Card Components.
"""

from typing import Callable, Optional
import flet as ft

from ui.theme import (
    get_level_color,
    POS_BADGE_COLOR,
    GUIDEWORD_BADGE_COLOR,
    CARD_BOX_SHADOW,
)
from ui.utils import open_url


def build_definition_block(
    def_data: dict,
    is_primary: bool = False,
) -> ft.Container:
    """Build a styled block for a single word definition / sense with level on the first place."""
    badges = []

    # 1. CEFR Level badge (first in tags)
    if def_data.get("level"):
        badges.append(
            ft.Container(
                content=ft.Text(def_data["level"], color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.BOLD),
                bgcolor=get_level_color(def_data["level"]),
                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                border_radius=5,
            )
        )

    # 2. Part of Speech badge
    if def_data.get("pos"):
        badges.append(
            ft.Container(
                content=ft.Text(def_data["pos"], color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.BOLD),
                bgcolor=POS_BADGE_COLOR,
                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                border_radius=5,
            )
        )

    # 3. Guideword badge
    if def_data.get("guideword"):
        badges.append(
            ft.Container(
                content=ft.Text(def_data["guideword"], color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.BOLD),
                bgcolor=GUIDEWORD_BADGE_COLOR,
                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                border_radius=5,
            )
        )

    # Examples list
    examples_col = ft.Column(spacing=3)
    for ex in def_data.get("examples", []):
        examples_col.controls.append(
            ft.Row(
                [
                    ft.Text("•", color=ft.Colors.GREY_500, size=14),
                    ft.Text(ex, italic=True, color=ft.Colors.GREY_800, size=13, expand=True),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(badges, wrap=True, spacing=6) if badges else ft.Container(),
                ft.Text(def_data.get("definition", ""), weight=ft.FontWeight.W_600, size=14, color=ft.Colors.BLACK_87),
                examples_col if examples_col.controls else ft.Container(),
            ],
            spacing=8,
        ),
        padding=12,
        border=ft.Border.all(1, ft.Colors.INDIGO_100 if is_primary else ft.Colors.GREY_200),
        border_radius=8,
        bgcolor=ft.Colors.INDIGO_50 if is_primary else ft.Colors.GREY_50,
        margin=ft.Margin.only(bottom=6),
    )


def build_word_card(
    word_data: dict,
    on_delete: Optional[Callable[[str], None]] = None,
    page: Optional[ft.Page] = None,
) -> ft.Container:
    """
    Build a comprehensive word card where the primary (first) definition is defined
    immediately and any additional definitions can be toggled/viewed on click.
    """
    word_str = word_data.get("word", "")
    definitions = word_data.get("definitions", [])
    raw_url = word_data.get("url")
    target_url = raw_url if raw_url else f"https://dictionary.cambridge.org/dictionary/english/{word_str.lower().replace(' ', '-')}"

    # Word title and count of descriptions tag placed lower than the word
    word_title_controls = [
        ft.Text(word_str, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
    ]

    if definitions:
        count_text = f"{len(definitions)} description{'s' if len(definitions) > 1 else ''}"
        word_title_controls.append(
            ft.Container(
                content=ft.Text(count_text, size=11, color=ft.Colors.BLUE_GREY_700, weight=ft.FontWeight.W_500),
                bgcolor=ft.Colors.BLUE_GREY_50,
                padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                border_radius=10,
                border=ft.Border.all(1, ft.Colors.BLUE_GREY_200),
            )
        )

    word_info_col = ft.Column(word_title_controls, spacing=4)

    # Action buttons (Cambridge link and delete)
    action_buttons = [
        ft.IconButton(
            icon=ft.Icons.OPEN_IN_NEW,
            icon_color=ft.Colors.BLUE_GREY_500,
            icon_size=18,
            tooltip="Open in Cambridge Dictionary",
            url=target_url,
            on_click=lambda e, link=target_url: open_url(link),
        )
    ]

    if on_delete:
        action_buttons.append(
            ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_color=ft.Colors.RED_400,
                icon_size=20,
                tooltip="Delete Word",
                on_click=lambda e, w=word_str: on_delete(w),
            )
        )

    header_row = ft.Row(
        [
            word_info_col,
            ft.Row(action_buttons, spacing=0),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    card_content = [header_row]

    if not definitions:
        card_content.append(ft.Text("No definitions found for this word.", italic=True, color=ft.Colors.GREY_600))
    else:
        # Primary (first) definition - always defined and shown immediately
        primary_block = build_definition_block(
            definitions[0],
            is_primary=True,
        )
        card_content.append(primary_block)

        # Other options (if any)
        other_defs = definitions[1:]
        if other_defs:
            other_options_col = ft.Column(
                controls=[
                    build_definition_block(d, is_primary=False)
                    for d in other_defs
                ],
                visible=False,
                spacing=6,
            )

            def toggle_options(e):
                other_options_col.visible = not other_options_col.visible
                if other_options_col.visible:
                    toggle_btn.content = f"Hide other options ({len(other_defs)})"
                    toggle_btn.icon = ft.Icons.KEYBOARD_ARROW_UP
                else:
                    toggle_btn.content = f"See other options ({len(other_defs)} more)"
                    toggle_btn.icon = ft.Icons.KEYBOARD_ARROW_DOWN
                if page:
                    page.update()

            toggle_btn = ft.TextButton(
                content=f"See other options ({len(other_defs)} more)",
                icon=ft.Icons.KEYBOARD_ARROW_DOWN,
                style=ft.ButtonStyle(color=ft.Colors.BLUE_700),
                on_click=toggle_options,
            )

            card_content.append(
                ft.Row([toggle_btn], alignment=ft.MainAxisAlignment.START)
            )
            card_content.append(other_options_col)

    return ft.Container(
        content=ft.Column(card_content, spacing=10),
        padding=16,
        border=ft.Border.all(1, ft.Colors.GREY_300),
        border_radius=10,
        bgcolor=ft.Colors.WHITE,
        margin=ft.Margin.only(bottom=12),
        shadow=CARD_BOX_SHADOW,
    )
