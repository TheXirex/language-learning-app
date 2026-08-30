"""
Main Application Entry Point for Language Learning App.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

# Suppress upstream deprecation warnings (e.g. from cryptography/pymongo)
warnings.filterwarnings("ignore")

# Add src and project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import flet as ft
from modules.db.repository import WordRepository

from ui.components import build_tag_faq
from ui.views import SearchView, DictionaryView, LearningView


def main(page: ft.Page):
    """Main application orchestrator and layout initializer."""
    page.title = "Language Learning App"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 16

    # Repository
    repo = WordRepository()

    # Global Notification
    def show_snack(msg: str, color: str):
        snack = ft.SnackBar(ft.Text(msg), bgcolor=color, open=True)
        page.overlay.append(snack)
        page.update()

    # Tag Guide / FAQ component at top of page
    faq_component = build_tag_faq()

    # State
    active_tab_index = 0
    dict_view: DictionaryView = None
    learning_view: LearningView = None

    def switch_to_search_tab():
        set_active_tab(0)

    def on_word_saved():
        dict_view.load_saved_words()
        if not learning_view.is_learning_active:
            learning_view.render_learning_view()

    def on_words_changed():
        if not learning_view.is_learning_active:
            learning_view.render_learning_view()

    search_view = SearchView(
        page=page,
        repo=repo,
        on_word_saved=on_word_saved,
        show_snack=show_snack,
    )

    dict_view = DictionaryView(
        page=page,
        repo=repo,
        on_words_changed=on_words_changed,
        on_count_updated=lambda count: update_dict_tab_counter(count),
        show_snack=show_snack,
    )

    learning_view = LearningView(
        page=page,
        get_saved_words=lambda: dict_view.cached_saved_words,
        on_navigate_to_search=switch_to_search_tab,
        show_snack=show_snack,
    )

    # -----------------------------------------------------------------------
    # Custom Non-Focusable Segmented Tab Navigation Bar
    # (Prevents Flutter native TabBar from stealing Arrow Keys during study)
    # -----------------------------------------------------------------------
    tab_titles = ["Search & Add", "Dictionary", "Flashcards"]
    tab_icons = [ft.Icons.SEARCH, ft.Icons.MENU_BOOK, ft.Icons.STYLE]

    dict_counter_text = ft.Text("Dictionary", size=13, weight=ft.FontWeight.W_500)
    tab_label_controls = [
        ft.Text("Search & Add", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        dict_counter_text,
        ft.Text("Flashcards", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.BLUE_GREY_800),
    ]

    tab_icon_controls = [
        ft.Icon(ft.Icons.SEARCH, size=18, color=ft.Colors.WHITE),
        ft.Icon(ft.Icons.MENU_BOOK, size=18, color=ft.Colors.BLUE_GREY_700),
        ft.Icon(ft.Icons.STYLE, size=18, color=ft.Colors.BLUE_GREY_700),
    ]

    tab_button_containers: list[ft.Container] = []

    def update_dict_tab_counter(total_count: int):
        dict_counter_text.value = f"Dictionary ({total_count})" if total_count > 0 else "Dictionary"
        page.update()

    def update_tab_bar_styles():
        for i, container in enumerate(tab_button_containers):
            is_active = i == active_tab_index
            container.bgcolor = ft.Colors.INDIGO_700 if is_active else ft.Colors.TRANSPARENT
            container.shadow = ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color=ft.Colors.with_opacity(0.12, ft.Colors.INDIGO_900),
                offset=ft.Offset(0, 2),
            ) if is_active else None

            lbl = tab_label_controls[i]
            lbl.color = ft.Colors.WHITE if is_active else ft.Colors.BLUE_GREY_800
            lbl.weight = ft.FontWeight.BOLD if is_active else ft.FontWeight.W_500

            icn = tab_icon_controls[i]
            icn.color = ft.Colors.WHITE if is_active else ft.Colors.BLUE_GREY_700

    tab_content_container = ft.Container(
        content=search_view.control,
        expand=True,
    )

    def set_active_tab(index: int):
        nonlocal active_tab_index
        active_tab_index = index
        update_tab_bar_styles()

        if index == 0:
            tab_content_container.content = search_view.control
        elif index == 1:
            dict_view.load_saved_words()
            tab_content_container.content = dict_view.control
        elif index == 2:
            dict_view.load_saved_words()
            if not learning_view.is_learning_active:
                learning_view.render_learning_view()
            tab_content_container.content = learning_view.control

        page.update()

    for idx in range(3):
        def make_tab_click(target_idx=idx):
            return lambda e: set_active_tab(target_idx)

        btn = ft.Container(
            content=ft.Row(
                [
                    tab_icon_controls[idx],
                    tab_label_controls[idx],
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            bgcolor=ft.Colors.INDIGO_700 if idx == 0 else ft.Colors.TRANSPARENT,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            alignment=ft.Alignment(0, 0),
            expand=True,
            on_click=make_tab_click(),
        )
        tab_button_containers.append(btn)

    tab_bar_strip = ft.Container(
        content=ft.Row(
            tab_button_containers,
            spacing=4,
        ),
        bgcolor=ft.Colors.INDIGO_50,
        border=ft.Border.all(1, ft.Colors.INDIGO_100),
        border_radius=10,
        padding=4,
        margin=ft.Margin.only(top=4, bottom=6),
    )

    # Keyboard navigation listener (strictly handles learning session arrow/space keys)
    def handle_keyboard_event(e: ft.KeyboardEvent):
        if active_tab_index == 2:
            learning_view.handle_keyboard_event(e)

    page.on_keyboard_event = handle_keyboard_event

    page.add(
        ft.Column(
            [
                faq_component,
                tab_bar_strip,
                tab_content_container,
            ],
            expand=True,
            spacing=4,
        )
    )

    # Initial dictionary load and learning view render
    dict_view.load_saved_words()
    learning_view.render_learning_view()


if __name__ == "__main__":
    ft.run(main)
