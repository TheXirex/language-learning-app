"""
Tag Guide & FAQ Expandable Component.
"""

import flet as ft


def build_tag_faq() -> ft.Container:
    """Build a compact, expandable Tag Guide / FAQ component for the top of the page."""
    return ft.Container(
        content=ft.ExpansionTile(
            leading=ft.Icon(ft.Icons.HELP_OUTLINE, color=ft.Colors.INDIGO_700, size=18),
            title=ft.Text("Tag Guide & FAQ", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900),
            subtitle=ft.Text("CEFR levels (A1-C2), Parts of Speech, and Guidewords", size=11, color=ft.Colors.GREY_700),
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("CEFR Language Levels:", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                            ft.Row(
                                [
                                    ft.Container(content=ft.Text("A1", color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.GREEN_700, padding=ft.Padding.symmetric(horizontal=6, vertical=2), border_radius=4),
                                    ft.Text("Beginner", size=11, color=ft.Colors.GREY_800),
                                    ft.Container(content=ft.Text("A2", color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.GREEN_700, padding=ft.Padding.symmetric(horizontal=6, vertical=2), border_radius=4),
                                    ft.Text("Elementary", size=11, color=ft.Colors.GREY_800),
                                    ft.Container(content=ft.Text("B1", color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.AMBER_800, padding=ft.Padding.symmetric(horizontal=6, vertical=2), border_radius=4),
                                    ft.Text("Intermediate", size=11, color=ft.Colors.GREY_800),
                                    ft.Container(content=ft.Text("B2", color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.AMBER_800, padding=ft.Padding.symmetric(horizontal=6, vertical=2), border_radius=4),
                                    ft.Text("Upper-Intermediate", size=11, color=ft.Colors.GREY_800),
                                    ft.Container(content=ft.Text("C1", color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.DEEP_PURPLE_600, padding=ft.Padding.symmetric(horizontal=6, vertical=2), border_radius=4),
                                    ft.Text("Advanced", size=11, color=ft.Colors.GREY_800),
                                    ft.Container(content=ft.Text("C2", color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.DEEP_PURPLE_600, padding=ft.Padding.symmetric(horizontal=6, vertical=2), border_radius=4),
                                    ft.Text("Proficiency", size=11, color=ft.Colors.GREY_800),
                                ],
                                wrap=True,
                                spacing=8,
                            ),
                            ft.Divider(height=1, color=ft.Colors.INDIGO_100),
                            ft.Text("Other Description Tags:", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                            ft.Row(
                                [
                                    ft.Container(content=ft.Text("noun / verb / adj", color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.BLUE_700, padding=ft.Padding.symmetric(horizontal=6, vertical=2), border_radius=4),
                                    ft.Text("Part of Speech (POS) — grammatical category of the word", size=11, color=ft.Colors.GREY_800),
                                ],
                                wrap=True,
                                spacing=6,
                            ),
                            ft.Row(
                                [
                                    ft.Container(content=ft.Text("guideword", color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.TEAL_700, padding=ft.Padding.symmetric(horizontal=6, vertical=2), border_radius=4),
                                    ft.Text("Guideword — Cambridge clue distinguishing specific meanings", size=11, color=ft.Colors.GREY_800),
                                ],
                                wrap=True,
                                spacing=6,
                            ),
                        ],
                        spacing=6,
                    ),
                    padding=ft.Padding.only(left=12, right=12, bottom=8),
                )
            ],
            dense=True,
            tile_padding=ft.Padding.symmetric(horizontal=10, vertical=0),
        ),
        border=ft.Border.all(1, ft.Colors.INDIGO_100),
        border_radius=8,
        bgcolor=ft.Colors.INDIGO_50,
        margin=ft.Margin.only(bottom=0),
    )
