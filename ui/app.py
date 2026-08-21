import os
import sys
import warnings
import webbrowser
from pathlib import Path

# Suppress upstream deprecation warnings (e.g. from cryptography/pymongo)
warnings.filterwarnings("ignore")

# Add src to Python path so we can import modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

import flet as ft
from modules.scrapper import run_spider
from modules.db.repository import WordRepository

def get_level_color(level: str | None) -> str:
    """Return a consistent badge color based on CEFR level."""
    if not level:
        return ft.Colors.BLUE_GREY_600
    lvl = str(level).strip().upper()
    if lvl in ("A1", "A2"):
        return ft.Colors.GREEN_700
    elif lvl in ("B1", "B2"):
        return ft.Colors.AMBER_800
    elif lvl in ("C1", "C2"):
        return ft.Colors.DEEP_PURPLE_600
    return ft.Colors.BLUE_GREY_600

def open_url(url: str):
    """Open given URL in default web browser."""
    if url:
        try:
            webbrowser.open(url)
        except Exception:
            pass

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

def build_definition_block(
    def_data: dict,
    is_primary: bool = False
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
                bgcolor=ft.Colors.BLUE_700,
                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                border_radius=5,
            )
        )

    # 3. Guideword badge
    if def_data.get("guideword"):
        badges.append(
            ft.Container(
                content=ft.Text(def_data["guideword"], color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.BOLD),
                bgcolor=ft.Colors.TEAL_700,
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
    on_delete=None,
    page: ft.Page | None = None,
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
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=4,
            color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )

def main(page: ft.Page):
    page.title = "Language Learning App"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 16

    # Repositories
    repo = WordRepository()

    # State variables
    current_search_result = {}
    cached_saved_words = []

    # Tag Guide / FAQ component at top of page
    faq_component = build_tag_faq()

    # UI Elements - Search Tab
    search_input = ft.TextField(
        hint_text="Enter a word to learn (e.g. abandon, car, run)...",
        expand=True,
        on_submit=lambda e: perform_search(),
    )
    search_button = ft.Button("Search", on_click=lambda e: perform_search())
    search_loading = ft.ProgressRing(visible=False, width=20, height=20)

    search_result_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    save_button = ft.Button(
        "Save to Dictionary",
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.GREEN_700,
        visible=False,
        on_click=lambda e: save_word(),
    )

    # UI Elements - Dictionary Tab
    dictionary_filter = ft.TextField(
        hint_text="Search in dictionary...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True,
        on_change=lambda e: apply_dictionary_filter(),
    )

    saved_list = ft.ListView(expand=True, spacing=10)

    # Tabs definition
    search_tab = ft.Tab(label="Search & Add", icon=ft.Icons.SEARCH)
    dictionary_tab = ft.Tab(label="Dictionary", icon=ft.Icons.MENU_BOOK)

    def show_snack(msg: str, color: str):
        snack = ft.SnackBar(ft.Text(msg), bgcolor=color, open=True)
        page.overlay.append(snack)
        page.update()

    def perform_search():
        nonlocal current_search_result
        word = search_input.value.strip() if search_input.value else ""
        if not word:
            return

        search_button.disabled = True
        search_loading.visible = True
        search_result_column.controls.clear()
        save_button.visible = False
        page.update()

        try:
            current_search_result = run_spider(word)

            if current_search_result and current_search_result.get("definitions"):
                card = build_word_card(
                    current_search_result,
                    page=page,
                )
                search_result_column.controls.append(card)
                save_button.visible = True
            else:
                search_result_column.controls.append(
                    ft.Text("No definitions found for this word.", color=ft.Colors.RED_600, size=15)
                )

        except Exception as e:
            search_result_column.controls.append(
                ft.Text(f"Error scraping word: {e}", color=ft.Colors.RED_600)
            )

        search_button.disabled = False
        search_loading.visible = False
        page.update()

    def save_word():
        nonlocal current_search_result
        if current_search_result:
            try:
                repo.save_word(current_search_result)
                show_snack(f"Word '{current_search_result.get('word', '')}' saved successfully!", ft.Colors.GREEN_700)

                # Clear search
                search_input.value = ""
                search_result_column.controls.clear()
                save_button.visible = False
                current_search_result = {}

                # Update saved list
                load_saved_words()
            except Exception as e:
                show_snack(f"Error saving word: {e}", ft.Colors.RED_700)
        page.update()

    def delete_word(word: str):
        try:
            repo.delete_word(word)
            show_snack(f"Word '{word}' deleted successfully!", ft.Colors.GREEN_700)
            load_saved_words()
        except Exception as e:
            show_snack(f"Error deleting word: {e}", ft.Colors.RED_700)
            page.update()

    def update_tab_counter(total_count: int):
        dictionary_tab.label = f"Dictionary ({total_count})" if total_count > 0 else "Dictionary"

    def render_saved_words(words_to_render: list[dict], is_filtering: bool = False):
        saved_list.controls.clear()
        total_count = len(cached_saved_words)

        update_tab_counter(total_count)

        if not words_to_render:
            empty_msg = "No matching words found." if is_filtering else "No words in dictionary yet."
            saved_list.controls.append(
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
                    on_delete=delete_word,
                    page=page,
                )
                saved_list.controls.append(card)

    def apply_dictionary_filter():
        filter_text = dictionary_filter.value.strip().lower() if dictionary_filter.value else ""
        if not filter_text:
            render_saved_words(cached_saved_words, is_filtering=False)
        else:
            filtered = [
                w for w in cached_saved_words
                if filter_text in w.get("word", "").lower()
                or any(
                    filter_text in (d.get("definition", "").lower() + " " + (d.get("guideword") or "").lower())
                    for d in w.get("definitions", [])
                )
            ]
            render_saved_words(filtered, is_filtering=True)
        page.update()

    def load_saved_words():
        nonlocal cached_saved_words
        try:
            cached_saved_words = repo.list_words()
            apply_dictionary_filter()
        except Exception as e:
            saved_list.controls.clear()
            saved_list.controls.append(
                ft.Text(f"Error loading dictionary: {e}", color=ft.Colors.RED_700)
            )
            page.update()

    # Layout - Search Tab
    search_tab_content = ft.Container(
        content=ft.Column(
            [
                ft.Row([search_input, search_button, search_loading], alignment=ft.MainAxisAlignment.START),
                search_result_column,
                save_button,
            ],
            expand=True,
            spacing=12,
        ),
        padding=10,
    )

    # Layout - Dictionary Tab (clean full-width search with inline counter)
    saved_tab_content = ft.Container(
        content=ft.Column(
            [
                ft.Row([dictionary_filter]),
                saved_list,
            ],
            expand=True,
            spacing=10,
        ),
        padding=10,
    )

    tabs = ft.Tabs(
        length=2,
        expand=True,
        selected_index=0,
        content=ft.Column(
            [
                ft.TabBar(
                    tabs=[
                        search_tab,
                        dictionary_tab,
                    ],
                    on_click=lambda e: load_saved_words(),
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        search_tab_content,
                        saved_tab_content,
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

    # Initial load
    load_saved_words()

if __name__ == "__main__":
    ft.run(main)
