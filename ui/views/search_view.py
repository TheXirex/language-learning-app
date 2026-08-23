"""
Search & Add Tab View.
"""

from typing import Callable, Optional
import flet as ft

from modules.scrapper import run_spider
from modules.db.repository import WordRepository
from ui.components.word_card import build_word_card


class SearchView:
    """View for searching Cambridge Dictionary and adding words to database."""

    def __init__(
        self,
        page: ft.Page,
        repo: WordRepository,
        on_word_saved: Optional[Callable[[], None]] = None,
        show_snack: Optional[Callable[[str, str], None]] = None,
    ):
        self.page = page
        self.repo = repo
        self.on_word_saved = on_word_saved
        self.show_snack = show_snack or (lambda msg, col: None)

        self.current_search_result: dict = {}

        # UI Controls
        self.search_input = ft.TextField(
            hint_text="Enter a word to learn (e.g. abandon, car, run)...",
            expand=True,
            on_submit=lambda e: self.perform_search(),
        )
        self.search_button = ft.Button("Search", on_click=lambda e: self.perform_search())
        self.search_loading = ft.ProgressRing(visible=False, width=20, height=20)

        self.search_result_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.save_button = ft.Button(
            "Save to Dictionary",
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREEN_700,
            visible=False,
            on_click=lambda e: self.save_word(),
        )

        # Root control container
        self.control = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            self.search_input,
                            self.search_button,
                            self.search_loading,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    self.search_result_column,
                    ft.Row(
                        [self.save_button],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                expand=True,
                spacing=12,
            ),
            padding=10,
            expand=True,
        )

    def perform_search(self):
        """Execute word scraping via Cambridge spider."""
        word = self.search_input.value.strip() if self.search_input.value else ""
        if not word:
            return

        self.search_button.disabled = True
        self.search_loading.visible = True
        self.search_result_column.controls.clear()
        self.save_button.visible = False
        self.page.update()

        try:
            self.current_search_result = run_spider(word)

            if self.current_search_result and self.current_search_result.get("definitions"):
                card = build_word_card(
                    self.current_search_result,
                    page=self.page,
                )
                self.search_result_column.controls.append(card)
                self.save_button.visible = True
            else:
                self.search_result_column.controls.append(
                    ft.Text("No definitions found for this word.", color=ft.Colors.RED_600, size=15)
                )
        except Exception as e:
            self.search_result_column.controls.append(
                ft.Text(f"Error scraping word: {e}", color=ft.Colors.RED_600)
            )

        self.search_button.disabled = False
        self.search_loading.visible = False
        self.page.update()

    def save_word(self):
        """Save the extracted word data to repository."""
        if self.current_search_result:
            try:
                self.repo.save_word(self.current_search_result)
                self.show_snack(
                    f"Word '{self.current_search_result.get('word', '')}' saved successfully!",
                    ft.Colors.GREEN_700,
                )

                # Clear search
                self.search_input.value = ""
                self.search_result_column.controls.clear()
                self.save_button.visible = False
                self.current_search_result = {}

                # Notify listener
                if self.on_word_saved:
                    self.on_word_saved()
            except Exception as e:
                self.show_snack(f"Error saving word: {e}", ft.Colors.RED_700)
        self.page.update()
