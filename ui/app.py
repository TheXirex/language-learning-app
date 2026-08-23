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

    # Tab Definitions
    search_tab = ft.Tab(label="Search & Add", icon=ft.Icons.SEARCH)
    dictionary_tab = ft.Tab(label="Dictionary", icon=ft.Icons.MENU_BOOK)
    learning_tab = ft.Tab(label="Learning (Plates)", icon=ft.Icons.STYLE)

    def update_dict_tab_counter(total_count: int):
        dictionary_tab.label = f"Dictionary ({total_count})" if total_count > 0 else "Dictionary"
        page.update()

    def switch_to_search_tab():
        tabs.selected_index = 0
        page.update()

    # Initialize Views
    dict_view: DictionaryView = None
    learning_view: LearningView = None

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
        on_count_updated=update_dict_tab_counter,
        show_snack=show_snack,
    )

    learning_view = LearningView(
        page=page,
        get_saved_words=lambda: dict_view.cached_saved_words,
        on_navigate_to_search=switch_to_search_tab,
        show_snack=show_snack,
    )

    def on_tab_change(e):
        """Handle tab changes across views."""
        dict_view.load_saved_words()
        if tabs.selected_index == 2 and not learning_view.is_learning_active:
            learning_view.render_learning_view()

    def handle_keyboard_event(e: ft.KeyboardEvent):
        """Delegate keyboard events to active views."""
        if tabs.selected_index == 2:
            learning_view.handle_keyboard_event(e)

    page.on_keyboard_event = handle_keyboard_event

    # Top-level Tabs Assembly
    tabs = ft.Tabs(
        length=3,
        expand=True,
        selected_index=0,
        content=ft.Column(
            [
                ft.TabBar(
                    tabs=[
                        search_tab,
                        dictionary_tab,
                        learning_tab,
                    ],
                    on_click=on_tab_change,
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        search_view.control,
                        dict_view.control,
                        learning_view.control,
                    ],
                ),
            ],
            expand=True,
        ),
    )

    page.add(
        ft.Column(
            [
                faq_component,
                tabs,
            ],
            expand=True,
            spacing=2,
        )
    )

    # Initial dictionary load and learning view render
    dict_view.load_saved_words()
    learning_view.render_learning_view()


if __name__ == "__main__":
    ft.run(main)
