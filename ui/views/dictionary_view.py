"""
Dictionary (Saved Words) Tab View.
"""

from typing import Callable, List, Optional
import flet as ft

from modules.db.repository import WordRepository
from ui.components.word_card import build_word_card


class DictionaryView:
    """View for browsing, filtering, and managing saved dictionary words."""

    def __init__(
        self,
        page: ft.Page,
        repo: WordRepository,
        on_words_changed: Optional[Callable[[], None]] = None,
        on_count_updated: Optional[Callable[[int], None]] = None,
        show_snack: Optional[Callable[[str, str], None]] = None,
    ):
        self.page = page
        self.repo = repo
        self.on_words_changed = on_words_changed
        self.on_count_updated = on_count_updated
        self.show_snack = show_snack or (lambda msg, col: None)

        self.cached_saved_words: List[dict] = []

        # UI Controls
        self.dictionary_filter = ft.TextField(
            hint_text="Search in dictionary...",
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
            on_change=lambda e: self.apply_dictionary_filter(),
        )
        self.saved_list = ft.ListView(expand=True, spacing=10)

        # Root control container
        self.control = ft.Container(
            content=ft.Column(
                [
                    ft.Row([self.dictionary_filter]),
                    self.saved_list,
                ],
                expand=True,
                spacing=10,
            ),
            padding=10,
            expand=True,
        )

    def load_saved_words(self):
        """Fetch all saved words from repository and update filter/list."""
        try:
            self.cached_saved_words = self.repo.list_words()
            self.apply_dictionary_filter()
        except Exception as e:
            self.saved_list.controls.clear()
            self.saved_list.controls.append(
                ft.Text(f"Error loading dictionary: {e}", color=ft.Colors.RED_700)
            )
            self.page.update()

    def apply_dictionary_filter(self):
        """Filter saved words based on input text and render results."""
        filter_text = (self.dictionary_filter.value or "").strip().lower()
        if not filter_text:
            self.render_saved_words(self.cached_saved_words, is_filtering=False)
        else:
            filtered = [
                w for w in self.cached_saved_words
                if filter_text in w.get("word", "").lower()
                or any(
                    filter_text in (d.get("definition", "").lower() + " " + (d.get("guideword") or "").lower())
                    for d in w.get("definitions", [])
                )
            ]
            self.render_saved_words(filtered, is_filtering=True)
        self.page.update()

    def render_saved_words(self, words_to_render: List[dict], is_filtering: bool = False):
        """Render given word list cards into saved_list."""
        self.saved_list.controls.clear()
        total_count = len(self.cached_saved_words)

        if self.on_count_updated:
            self.on_count_updated(total_count)

        if not words_to_render:
            empty_msg = "No matching words found." if is_filtering else "No words in dictionary yet."
            self.saved_list.controls.append(
                ft.Container(
                    content=ft.Text(empty_msg, color=ft.Colors.GREY_600, size=14, italic=True),
                    padding=24,
                    alignment=ft.Alignment(0, 0),
                )
            )
        else:
            for w in words_to_render:
                card = build_word_card(
                    w,
                    on_delete=self.delete_word,
                    page=self.page,
                )
                self.saved_list.controls.append(card)

    def delete_word(self, word: str):
        """Delete word from database and refresh list."""
        try:
            self.repo.delete_word(word)
            self.show_snack(f"Word '{word}' deleted successfully!", ft.Colors.GREEN_700)
            self.load_saved_words()
            if self.on_words_changed:
                self.on_words_changed()
        except Exception as e:
            self.show_snack(f"Error deleting word: {e}", ft.Colors.RED_700)
            self.page.update()
