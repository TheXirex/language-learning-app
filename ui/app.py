import asyncio
import os
import random
import sys
import threading
import time
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
                bgcolor=ft.Colors.BLUE_700,
                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                border_radius=6,
            )
        )
    if guideword:
        badges.append(
            ft.Container(
                content=ft.Text(guideword, color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                bgcolor=ft.Colors.TEAL_700,
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
        # FRONT SIDE: Shows the target word prominently
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Row(badges, spacing=6),
                        link_button,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                word_str,
                                size=36,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.INDIGO_900,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    f"Guideword: {guideword}" if guideword else f"Part of Speech: {pos or 'word'}",
                                    size=13,
                                    color=ft.Colors.INDIGO_600,
                                    italic=True,
                                ),
                                visible=bool(guideword or pos),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                    ),
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                ),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.TOUCH_APP_ROUNDED, size=15, color=ft.Colors.INDIGO_400),
                        ft.Text("Click plate or press Space to reveal definition", size=12, color=ft.Colors.INDIGO_500, weight=ft.FontWeight.W_500),
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
                        ft.Icon(ft.Icons.FLIP_TO_FRONT_ROUNDED, size=15, color=ft.Colors.INDIGO_400),
                        ft.Text("Click plate or press Space to flip back to word", size=12, color=ft.Colors.INDIGO_500, weight=ft.FontWeight.W_500),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                ),
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

def main(page: ft.Page):
    page.title = "Language Learning App"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 16

    # Repositories
    repo = WordRepository()

    # State variables
    current_search_result = {}
    cached_saved_words: list[dict] = []

    # Learning (Plates) State
    all_levels_list = ["A1", "A2", "B1", "B2", "C1", "C2"]
    selected_levels: set[str] = set()       # Empty means all levels
    selected_pos: set[str] = set()          # Empty means all POS
    selected_count_limit: int | None = 10   # None means All
    study_mode: str = "word_to_def"         # "word_to_def" or "def_to_word"

    # Learning Session Active State
    learning_session_words: list[dict] = []
    current_plate_idx: int = 0
    is_flipped: bool = False
    is_flipping: bool = False
    is_learning_active: bool = False
    is_learning_completed: bool = False

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

    # UI Elements - Learning (Plates) Tab Container
    learning_tab_content = ft.Container(expand=True, padding=10)

    # Tabs definition
    search_tab = ft.Tab(label="Search & Add", icon=ft.Icons.SEARCH)
    dictionary_tab = ft.Tab(label="Dictionary", icon=ft.Icons.MENU_BOOK)
    learning_tab = ft.Tab(label="Learning (Plates)", icon=ft.Icons.STYLE)

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

                # Update saved list and refresh learning view if on config
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

    # -------------------------------------------------------------
    # LEARNING (PLATES) LOGIC & VIEWS
    # -------------------------------------------------------------
    def get_available_pos_tags() -> list[str]:
        """Extract all unique POS tags present in cached dictionary words."""
        tags = set()
        for w in cached_saved_words:
            for d in w.get("definitions", []):
                p = (d.get("pos") or "").strip().lower()
                if p:
                    tags.add(p)
        sorted_tags = sorted(list(tags))
        return sorted_tags if sorted_tags else ["noun", "verb", "adjective", "adverb"]

    def get_filtered_learning_words() -> list[dict]:
        """Filter cached_saved_words by selected CEFR levels and POS tags."""
        matched = []

        for w in cached_saved_words:
            defs = w.get("definitions", [])
            if not defs:
                continue

            # 1. Level filter: word matches if ANY definition matches selected levels
            if selected_levels:
                has_level = any(
                    (d.get("level") or "").strip().upper() in selected_levels
                    for d in defs
                )
                if not has_level:
                    continue

            # 2. POS filter: word matches if ANY definition matches selected POS
            if selected_pos:
                has_pos = any(
                    (d.get("pos") or "").strip().lower() in selected_pos
                    for d in defs
                )
                if not has_pos:
                    continue

            matched.append(w)

        return matched

    is_flipping = False

    def build_plate_card_shell(word_data: dict, flipped: bool) -> ft.Container:
        """Build the styled card container shell for AnimatedSwitcher."""
        inner_content = build_plate_card_content(word_data, flipped, study_mode)
        return ft.Container(
            key=f"plate_{current_plate_idx}_{flipped}_{study_mode}",
            content=inner_content,
            width=580,
            height=350,
            padding=24,
            border=ft.Border.all(1.5, ft.Colors.INDIGO_100),
            border_radius=18,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=16,
                color=ft.Colors.with_opacity(0.10, ft.Colors.INDIGO_900),
                offset=ft.Offset(0, 6),
            ),
            animate_offset=ft.Animation(140, ft.AnimationCurve.EASE_OUT),
            offset=ft.Offset(0, 0),
            alignment=ft.Alignment(0, 0),
            on_click=lambda e: trigger_plate_flip(),
            on_hover=on_plate_hover,
        )

    async def flip_worker():
        nonlocal is_flipped, is_flipping
        try:
            is_flipped = not is_flipped
            current_word = learning_session_words[current_plate_idx]
            plate_card_switcher.content = build_plate_card_shell(current_word, is_flipped)
            plate_card_switcher.update()
            await asyncio.sleep(0.28)
        except Exception:
            pass
        finally:
            is_flipping = False

    def trigger_plate_flip():
        """Smooth horizontal card flip turnover via AnimatedSwitcher."""
        nonlocal is_flipping
        if is_flipping or not learning_session_words:
            return
        is_flipping = True
        page.run_task(flip_worker)

    def prev_plate():
        """Navigate to previous plate card."""
        nonlocal current_plate_idx, is_flipped
        if current_plate_idx > 0:
            current_plate_idx -= 1
            is_flipped = False
            render_learning_view()

    def next_plate():
        """Navigate to next plate card or complete session if at end."""
        nonlocal current_plate_idx, is_flipped, is_learning_completed
        if current_plate_idx < len(learning_session_words) - 1:
            current_plate_idx += 1
            is_flipped = False
            render_learning_view()
        else:
            # Reached end of cards -> show Session Complete
            is_learning_completed = True
            render_learning_view()

    def shuffle_current_deck():
        """Shuffle remaining cards in session."""
        nonlocal learning_session_words, current_plate_idx, is_flipped
        if len(learning_session_words) > 1:
            random.shuffle(learning_session_words)
            current_plate_idx = 0
            is_flipped = False
            show_snack("Deck shuffled! Starting from plate 1.", ft.Colors.INDIGO_700)
            render_learning_view()

    def start_learning_session():
        """Initialize and launch flashcard learning session."""
        nonlocal learning_session_words, current_plate_idx, is_flipped, is_learning_active, is_learning_completed
        matching = get_filtered_learning_words()
        if not matching:
            show_snack("No words match your selected filters. Please adjust filters.", ft.Colors.RED_700)
            return

        words_pool = list(matching)
        random.shuffle(words_pool)

        if selected_count_limit is not None and selected_count_limit > 0:
            learning_session_words = words_pool[:selected_count_limit]
        else:
            learning_session_words = words_pool

        current_plate_idx = 0
        is_flipped = False
        is_learning_active = True
        is_learning_completed = False
        render_learning_view()

    def exit_learning_to_config():
        """Exit active study session and return to configuration view."""
        nonlocal is_learning_active, is_learning_completed
        is_learning_active = False
        is_learning_completed = False
        render_learning_view()

    def on_plate_hover(e):
        """Micro-elevation animation on mouse hover."""
        if not is_flipping:
            if e.data == "true":
                e.control.offset = ft.Offset(0, -0.015)
            else:
                e.control.offset = ft.Offset(0, 0)
            e.control.update()

    # AnimatedSwitcher container definition for study view
    plate_card_switcher = ft.AnimatedSwitcher(
        content=None,
        transition=ft.AnimatedSwitcherTransition.SCALE,
        duration=260,
        reverse_duration=260,
        switch_in_curve=ft.AnimationCurve.EASE_OUT_CUBIC,
        switch_out_curve=ft.AnimationCurve.EASE_IN_CUBIC,
    )

    def build_learning_config_view() -> ft.Control:
        """Build the pre-session configuration screen with pure in-place reactive updates (no scroll jump)."""
        nonlocal selected_count_limit, study_mode
        total_dict_count = len(cached_saved_words)

        if total_dict_count == 0:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.MENU_BOOK_ROUNDED, size=54, color=ft.Colors.INDIGO_300),
                        ft.Text("Your Dictionary is Empty", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900),
                        ft.Text(
                            "Search and save words in the 'Search & Add' tab to start learning with flashcard plates!",
                            size=14,
                            color=ft.Colors.GREY_700,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Button(
                            "Go to Search & Add",
                            icon=ft.Icons.SEARCH,
                            bgcolor=ft.Colors.INDIGO_700,
                            color=ft.Colors.WHITE,
                            on_click=lambda e: switch_to_search_tab(),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=14,
                ),
                alignment=ft.Alignment(0, 0),
                expand=True,
                padding=30,
            )

        # ------------------------------------------------------------------
        # 1. Study Direction Selector (Top-level with in-place toggle)
        # ------------------------------------------------------------------
        mode_w2d_icon = ft.Icon(
            ft.Icons.ABC_ROUNDED if study_mode == "word_to_def" else ft.Icons.RADIO_BUTTON_UNCHECKED,
            size=18,
            color=ft.Colors.WHITE if study_mode == "word_to_def" else ft.Colors.BLUE_GREY_700,
        )
        mode_w2d_text = ft.Text(
            "Word → Definition",
            color=ft.Colors.WHITE if study_mode == "word_to_def" else ft.Colors.BLUE_GREY_900,
            size=13,
            weight=ft.FontWeight.BOLD,
        )
        mode_w2d_btn = ft.Container(
            content=ft.Row([mode_w2d_icon, mode_w2d_text], spacing=6),
            bgcolor=ft.Colors.INDIGO_700 if study_mode == "word_to_def" else ft.Colors.GREY_100,
            border=ft.Border.all(1.5, ft.Colors.INDIGO_700 if study_mode == "word_to_def" else ft.Colors.GREY_300),
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
            on_click=lambda e: set_study_mode("word_to_def"),
        )

        mode_d2w_icon = ft.Icon(
            ft.Icons.PSYCHOLOGY_ALT_ROUNDED if study_mode == "def_to_word" else ft.Icons.RADIO_BUTTON_UNCHECKED,
            size=18,
            color=ft.Colors.WHITE if study_mode == "def_to_word" else ft.Colors.BLUE_GREY_700,
        )
        mode_d2w_text = ft.Text(
            "Definition → Word",
            color=ft.Colors.WHITE if study_mode == "def_to_word" else ft.Colors.BLUE_GREY_900,
            size=13,
            weight=ft.FontWeight.BOLD,
        )
        mode_d2w_btn = ft.Container(
            content=ft.Row([mode_d2w_icon, mode_d2w_text], spacing=6),
            bgcolor=ft.Colors.INDIGO_700 if study_mode == "def_to_word" else ft.Colors.GREY_100,
            border=ft.Border.all(1.5, ft.Colors.INDIGO_700 if study_mode == "def_to_word" else ft.Colors.GREY_300),
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
            on_click=lambda e: set_study_mode("def_to_word"),
        )

        def set_study_mode(mode: str):
            nonlocal study_mode
            study_mode = mode
            is_w2d = mode == "word_to_def"

            mode_w2d_btn.bgcolor = ft.Colors.INDIGO_700 if is_w2d else ft.Colors.GREY_100
            mode_w2d_btn.border = ft.Border.all(1.5, ft.Colors.INDIGO_700 if is_w2d else ft.Colors.GREY_300)
            mode_w2d_icon.name = ft.Icons.ABC_ROUNDED if is_w2d else ft.Icons.RADIO_BUTTON_UNCHECKED
            mode_w2d_icon.color = ft.Colors.WHITE if is_w2d else ft.Colors.BLUE_GREY_700
            mode_w2d_text.color = ft.Colors.WHITE if is_w2d else ft.Colors.BLUE_GREY_900

            mode_d2w_btn.bgcolor = ft.Colors.INDIGO_700 if not is_w2d else ft.Colors.GREY_100
            mode_d2w_btn.border = ft.Border.all(1.5, ft.Colors.INDIGO_700 if not is_w2d else ft.Colors.GREY_300)
            mode_d2w_icon.name = ft.Icons.PSYCHOLOGY_ALT_ROUNDED if not is_w2d else ft.Icons.RADIO_BUTTON_UNCHECKED
            mode_d2w_icon.color = ft.Colors.WHITE if not is_w2d else ft.Colors.BLUE_GREY_700
            mode_d2w_text.color = ft.Colors.WHITE if not is_w2d else ft.Colors.BLUE_GREY_900

            page.update()

        # ------------------------------------------------------------------
        # 2. Compact CEFR Level Small Selectors
        # ------------------------------------------------------------------
        level_chip_map: dict[str, ft.Container] = {}
        level_chips_row = ft.Row(wrap=True, spacing=8)

        for lvl in all_levels_list:
            is_sel = lvl in selected_levels
            badge_color = get_level_color(lvl)

            def make_level_click(target_lvl=lvl):
                def on_click(e):
                    if target_lvl in selected_levels:
                        selected_levels.remove(target_lvl)
                    else:
                        selected_levels.add(target_lvl)
                    update_config_view_state()
                return on_click

            chip_container = ft.Container(
                content=ft.Text(
                    lvl,
                    color=ft.Colors.WHITE if is_sel else ft.Colors.BLUE_GREY_800,
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                bgcolor=badge_color if is_sel else ft.Colors.WHITE,
                border=ft.Border.all(1.5 if is_sel else 1.0, badge_color if is_sel else ft.Colors.GREY_300),
                border_radius=6,
                width=38,
                height=28,
                alignment=ft.Alignment(0, 0),
                tooltip=f"Level {lvl}" + (" (Selected)" if is_sel else ""),
                on_click=make_level_click(),
            )
            level_chip_map[lvl] = chip_container
            level_chips_row.controls.append(chip_container)

        def select_all_levels(e):
            selected_levels.clear()
            selected_levels.update(all_levels_list)
            update_config_view_state()

        def clear_levels(e):
            selected_levels.clear()
            update_config_view_state()

        # ------------------------------------------------------------------
        # 3. Part of Speech Filter Chips
        # ------------------------------------------------------------------
        available_pos = get_available_pos_tags()
        pos_chip_map: dict[str, ft.Container] = {}
        pos_chips_row = ft.Row(wrap=True, spacing=8)

        for pos_tag in available_pos:
            is_sel = pos_tag in selected_pos

            def make_pos_click(target_pos=pos_tag):
                def on_click(e):
                    if target_pos in selected_pos:
                        selected_pos.remove(target_pos)
                    else:
                        selected_pos.add(target_pos)
                    update_config_view_state()
                return on_click

            p_container = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.CHECK, size=14, color=ft.Colors.WHITE, visible=is_sel),
                        ft.Text(pos_tag, color=ft.Colors.WHITE if is_sel else ft.Colors.BLUE_GREY_900, size=12, weight=ft.FontWeight.W_600),
                    ],
                    spacing=4,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                bgcolor=ft.Colors.BLUE_700 if is_sel else ft.Colors.GREY_100,
                border=ft.Border.all(1.5, ft.Colors.BLUE_700 if is_sel else ft.Colors.GREY_300),
                border_radius=8,
                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                on_click=make_pos_click(),
            )
            pos_chip_map[pos_tag] = p_container
            pos_chips_row.controls.append(p_container)

        def select_all_pos(e):
            selected_pos.clear()
            selected_pos.update(available_pos)
            update_config_view_state()

        def clear_pos(e):
            selected_pos.clear()
            update_config_view_state()

        # ------------------------------------------------------------------
        # 4. Adaptive Word Count Presets Row
        # ------------------------------------------------------------------
        count_chips_row = ft.Row(wrap=True, spacing=6)

        # ------------------------------------------------------------------
        # 5. Live Summary Banner & Start Button Containers
        # ------------------------------------------------------------------
        summary_banner_container = ft.Container()

        start_btn_icon = ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color=ft.Colors.WHITE, size=22)
        start_btn_label = ft.Text(
            "Start Learning Session",
            size=15,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
        )
        start_button = ft.Button(
            content=ft.Row(
                [start_btn_icon, start_btn_label],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            bgcolor=ft.Colors.INDIGO_700,
            disabled=False,
            on_click=lambda e: start_learning_session(),
            height=46,
        )

        def build_summary_banner(matched_list: list[dict], matching_cnt: int, eff_cnt: int) -> ft.Control:
            if matching_cnt > 0:
                preview_chips = []
                for w in matched_list[:8]:
                    preview_chips.append(
                        ft.Container(
                            content=ft.Text(w.get("word", ""), size=11, color=ft.Colors.INDIGO_900, weight=ft.FontWeight.W_500),
                            bgcolor=ft.Colors.INDIGO_50,
                            border=ft.Border.all(1, ft.Colors.INDIGO_200),
                            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                            border_radius=12,
                        )
                    )
                if matching_cnt > 8:
                    preview_chips.append(
                        ft.Text(f"+ {matching_cnt - 8} more", size=11, color=ft.Colors.INDIGO_600, italic=True)
                    )

                return ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color=ft.Colors.GREEN_700, size=22),
                                    ft.Column(
                                        [
                                            ft.Text(
                                                f"Selected {matching_cnt} of {total_dict_count} words from your dictionary",
                                                weight=ft.FontWeight.BOLD,
                                                size=14,
                                                color=ft.Colors.GREEN_900,
                                            ),
                                            ft.Text(
                                                f"Session will practice {eff_cnt} words (Shuffled)",
                                                size=12,
                                                color=ft.Colors.GREEN_800,
                                            ),
                                        ],
                                        spacing=2,
                                        expand=True,
                                    ),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=10,
                            ),
                            ft.Divider(height=1, color=ft.Colors.GREEN_200),
                            ft.Row(
                                [
                                    ft.Text("Included words preview:", size=11, color=ft.Colors.GREY_700, weight=ft.FontWeight.BOLD),
                                    ft.Row(preview_chips, wrap=True, spacing=4, expand=True),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=14,
                    bgcolor=ft.Colors.GREEN_50,
                    border=ft.Border.all(1.5, ft.Colors.GREEN_300),
                    border_radius=10,
                )
            else:
                return ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, color=ft.Colors.AMBER_900, size=22),
                            ft.Column(
                                [
                                    ft.Text(
                                        f"0 of {total_dict_count} words match the selected filters",
                                        weight=ft.FontWeight.BOLD,
                                        size=14,
                                        color=ft.Colors.AMBER_900,
                                    ),
                                    ft.Text(
                                        "Try clearing level or POS filters to include more words from your dictionary.",
                                        size=12,
                                        color=ft.Colors.AMBER_800,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=14,
                    bgcolor=ft.Colors.AMBER_50,
                    border=ft.Border.all(1.5, ft.Colors.AMBER_300),
                    border_radius=10,
                )

        def update_config_view_state():
            """In-place update of all interactive elements: preserves exact scroll position!"""
            nonlocal selected_count_limit
            matching_words = get_filtered_learning_words()
            matching_count = len(matching_words)

            # 1. Update CEFR Level small selectors
            for lvl, c in level_chip_map.items():
                is_sel = lvl in selected_levels
                badge_color = get_level_color(lvl)
                c.bgcolor = badge_color if is_sel else ft.Colors.WHITE
                c.border = ft.Border.all(1.5 if is_sel else 1.0, badge_color if is_sel else ft.Colors.GREY_300)
                txt = c.content
                txt.color = ft.Colors.WHITE if is_sel else ft.Colors.BLUE_GREY_800
                c.tooltip = f"Level {lvl}" + (" (Selected)" if is_sel else "")

            # 2. Update POS chips
            for pos_tag, c in pos_chip_map.items():
                is_sel = pos_tag in selected_pos
                c.bgcolor = ft.Colors.BLUE_700 if is_sel else ft.Colors.GREY_100
                c.border = ft.Border.all(1.5, ft.Colors.BLUE_700 if is_sel else ft.Colors.GREY_300)
                icon_ctrl = c.content.controls[0]
                text_ctrl = c.content.controls[1]
                icon_ctrl.visible = is_sel
                text_ctrl.color = ft.Colors.WHITE if is_sel else ft.Colors.BLUE_GREY_900

            # 3. Update Adaptive Word Count Presets
            standard_steps = [5, 10, 15, 20, 30, 50, 100]
            adaptive_steps = [step for step in standard_steps if step < matching_count]
            count_options = [(step, str(step)) for step in adaptive_steps]
            if matching_count > 0:
                count_options.append((None, f"All ({matching_count})"))
            else:
                count_options.append((None, "0"))

            valid_values = [opt[0] for opt in count_options]
            if selected_count_limit not in valid_values:
                selected_count_limit = None

            effective_count = min(matching_count, selected_count_limit) if (selected_count_limit is not None and selected_count_limit > 0) else matching_count

            count_chips_row.controls.clear()
            for opt_val, opt_label in count_options:
                is_sel = selected_count_limit == opt_val

                def make_count_click(target_opt=opt_val):
                    def on_click(e):
                        nonlocal selected_count_limit
                        selected_count_limit = target_opt
                        update_config_view_state()
                    return on_click

                count_chips_row.controls.append(
                    ft.Container(
                        content=ft.Text(
                            opt_label,
                            color=ft.Colors.WHITE if is_sel else ft.Colors.BLUE_GREY_900,
                            size=12,
                            weight=ft.FontWeight.BOLD,
                        ),
                        bgcolor=ft.Colors.INDIGO_700 if is_sel else ft.Colors.GREY_100,
                        border=ft.Border.all(1.5, ft.Colors.INDIGO_700 if is_sel else ft.Colors.GREY_300),
                        border_radius=8,
                        padding=ft.Padding.symmetric(horizontal=14, vertical=6),
                        on_click=make_count_click(),
                    )
                )

            # 4. Update Summary Banner
            summary_banner_container.content = build_summary_banner(matching_words, matching_count, effective_count)

            # 5. Update Start Button
            start_button.disabled = matching_count == 0
            start_button.bgcolor = ft.Colors.INDIGO_700 if matching_count > 0 else ft.Colors.GREY_400
            start_btn_label.value = f"Start Learning Session ({effective_count} words)" if matching_count > 0 else "Select Words to Start"

            page.update()

        # Initial render of reactive child elements
        update_config_view_state()

        # Assemble Configuration Card
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.STYLE, color=ft.Colors.INDIGO_700, size=24),
                                    ft.Column(
                                        [
                                            ft.Text("Flashcard Plates Learning Setup", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900),
                                            ft.Text("Filter by CEFR levels or parts of speech, then start active recall practice with Quizlet turning plates.", size=12, color=ft.Colors.GREY_700),
                                        ],
                                        spacing=2,
                                    ),
                                ],
                                spacing=12,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Divider(height=1, color=ft.Colors.INDIGO_100),

                            # TOP: Study Direction Selector
                            ft.Row(
                                [
                                    ft.Text("Study Direction:", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                                    ft.Row([mode_w2d_btn, mode_d2w_btn], spacing=10),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Divider(height=1, color=ft.Colors.INDIGO_100),

                            # 1. CEFR Levels section
                            ft.Row(
                                [
                                    ft.Text("1. CEFR Level Filter:", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                                    ft.Row(
                                        [
                                            ft.TextButton("All Levels", on_click=select_all_levels, style=ft.ButtonStyle(padding=0)),
                                            ft.Text("•", color=ft.Colors.GREY_400),
                                            ft.TextButton("Clear", on_click=clear_levels, style=ft.ButtonStyle(padding=0)),
                                        ],
                                        spacing=6,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            level_chips_row,

                            # 2. Parts of Speech section
                            ft.Row(
                                [
                                    ft.Text("2. Part of Speech (POS) Filter:", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                                    ft.Row(
                                        [
                                            ft.TextButton("All POS", on_click=select_all_pos, style=ft.ButtonStyle(padding=0)),
                                            ft.Text("•", color=ft.Colors.GREY_400),
                                            ft.TextButton("Clear", on_click=clear_pos, style=ft.ButtonStyle(padding=0)),
                                        ],
                                        spacing=6,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            pos_chips_row,

                            # 3. Words per session (Adaptive)
                            ft.Row(
                                [
                                    ft.Text("3. Words per session:", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                                    count_chips_row,
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),

                            # Dynamic matching feedback banner
                            summary_banner_container,

                            # Start button
                            start_button,
                        ],
                        spacing=14,
                    ),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.Border.all(1, ft.Colors.INDIGO_100),
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=8,
                        color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                        offset=ft.Offset(0, 3),
                    ),
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10,
        )

    def build_learning_study_view() -> ft.Control:
        """Build the active study screen with the interactive plate and outer left/right arrows."""
        total_cards = len(learning_session_words)
        current_word = learning_session_words[current_plate_idx]
        progress_val = (current_plate_idx + 1) / max(1, total_cards)

        # Update plate card switcher content
        plate_card_switcher.content = build_plate_card_shell(current_word, is_flipped)

        # Outer Left Navigation Arrow (<)
        is_first = current_plate_idx == 0
        left_arrow_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                icon_size=24,
                icon_color=ft.Colors.INDIGO_900 if not is_first else ft.Colors.GREY_400,
                disabled=is_first,
                tooltip="Previous Plate (← Left Arrow)",
                on_click=lambda e: prev_plate(),
            ),
            bgcolor=ft.Colors.WHITE if not is_first else ft.Colors.GREY_100,
            border=ft.Border.all(1.5, ft.Colors.INDIGO_200 if not is_first else ft.Colors.GREY_200),
            border_radius=30,
            width=50,
            height=50,
            alignment=ft.Alignment(0, 0),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=6,
                color=ft.Colors.with_opacity(0.10, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ) if not is_first else None,
        )

        # Outer Right Navigation Arrow (>)
        is_last = current_plate_idx == total_cards - 1
        right_arrow_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.CHECK_ROUNDED if is_last else ft.Icons.ARROW_FORWARD_IOS_ROUNDED,
                icon_size=24,
                icon_color=ft.Colors.WHITE if is_last else ft.Colors.INDIGO_900,
                tooltip="Finish Session" if is_last else "Next Plate (→ Right Arrow)",
                on_click=lambda e: next_plate(),
            ),
            bgcolor=ft.Colors.GREEN_700 if is_last else ft.Colors.WHITE,
            border=ft.Border.all(1.5, ft.Colors.GREEN_700 if is_last else ft.Colors.INDIGO_200),
            border_radius=30,
            width=50,
            height=50,
            alignment=ft.Alignment(0, 0),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=6,
                color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

        # Header controls
        progress_bar = ft.ProgressBar(
            value=progress_val,
            color=ft.Colors.INDIGO_600,
            bgcolor=ft.Colors.INDIGO_100,
            height=8,
            border_radius=4,
            expand=True,
        )

        counter_badge = ft.Container(
            content=ft.Text(
                f"Plate {current_plate_idx + 1} / {total_cards}",
                weight=ft.FontWeight.BOLD,
                size=13,
                color=ft.Colors.INDIGO_900,
            ),
            bgcolor=ft.Colors.INDIGO_50,
            border=ft.Border.all(1, ft.Colors.INDIGO_200),
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
            border_radius=12,
        )

        return ft.Column(
            [
                # Top session toolbar
                ft.Row(
                    [
                        counter_badge,
                        progress_bar,
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.SHUFFLE,
                                    icon_color=ft.Colors.INDIGO_700,
                                    tooltip="Shuffle Deck",
                                    on_click=lambda e: shuffle_current_deck(),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.REFRESH,
                                    icon_color=ft.Colors.INDIGO_700,
                                    tooltip="Restart from Beginning",
                                    on_click=lambda e: restart_learning_session(),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.TUNE,
                                    icon_color=ft.Colors.INDIGO_700,
                                    tooltip="Configure Filters / Settings",
                                    on_click=lambda e: exit_learning_to_config(),
                                ),
                            ],
                            spacing=2,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),

                # Central Plate + Left/Right Outer Arrows Row
                ft.Container(
                    content=ft.Row(
                        [
                            left_arrow_btn,
                            plate_card_switcher,
                            right_arrow_btn,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=18,
                    ),
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                ),

                # Bottom control & shortcut helper bar
                ft.Row(
                    [
                        ft.Button(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.FLIP_ROUNDED, size=18, color=ft.Colors.WHITE),
                                    ft.Text("Flip Plate (Space)", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                ],
                                spacing=6,
                            ),
                            bgcolor=ft.Colors.INDIGO_700,
                            on_click=lambda e: trigger_plate_flip(),
                            height=40,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        ft.Text("💡 Shortcuts: [←] Previous Plate   |   [Space] Flip Card   |   [→] Next Plate", size=11, color=ft.Colors.GREY_600, italic=True),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            expand=True,
            spacing=10,
        )

    def build_learning_complete_view() -> ft.Control:
        """Build the congratulatory summary view when all cards in session have been practiced."""
        total_cards = len(learning_session_words)

        practiced_chips = []
        for w in learning_session_words:
            defs = w.get("definitions", [])
            lvl = defs[0].get("level") if defs else None
            practiced_chips.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Text(lvl, size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                bgcolor=get_level_color(lvl),
                                padding=ft.Padding.symmetric(horizontal=6, vertical=1),
                                border_radius=4,
                            ) if lvl else ft.Container(),
                            ft.Text(w.get("word", ""), size=12, color=ft.Colors.INDIGO_900, weight=ft.FontWeight.W_600),
                        ],
                        spacing=4,
                    ),
                    bgcolor=ft.Colors.INDIGO_50,
                    border=ft.Border.all(1, ft.Colors.INDIGO_200),
                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                    border_radius=8,
                )
            )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.EMOJI_EVENTS_ROUNDED, size=64, color=ft.Colors.AMBER_600),
                    ft.Text("🎉 Session Completed!", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900),
                    ft.Text(
                        f"You practiced {total_cards} word{'s' if total_cards > 1 else ''} in this study session.",
                        size=14,
                        color=ft.Colors.GREY_700,
                    ),
                    ft.Divider(height=1, color=ft.Colors.INDIGO_100),
                    ft.Text("Practiced Words:", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                    ft.Row(practiced_chips, wrap=True, spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=1, color=ft.Colors.INDIGO_100),
                    ft.Row(
                        [
                            ft.Button(
                                "Practice Again",
                                icon=ft.Icons.REFRESH,
                                bgcolor=ft.Colors.INDIGO_700,
                                color=ft.Colors.WHITE,
                                on_click=lambda e: restart_learning_session(),
                            ),
                            ft.Button(
                                "Shuffle & Repeat",
                                icon=ft.Icons.SHUFFLE,
                                bgcolor=ft.Colors.GREEN_700,
                                color=ft.Colors.WHITE,
                                on_click=lambda e: shuffle_and_restart(),
                            ),
                            ft.OutlinedButton(
                                "New Session Setup",
                                icon=ft.Icons.TUNE,
                                on_click=lambda e: exit_learning_to_config(),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=12,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=14,
            ),
            padding=30,
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(1, ft.Colors.INDIGO_100),
            border_radius=16,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=12,
                color=ft.Colors.with_opacity(0.08, ft.Colors.INDIGO_900),
                offset=ft.Offset(0, 4),
            ),
            alignment=ft.Alignment(0, 0),
            expand=True,
        )

    def restart_learning_session():
        """Restart session from card 1."""
        nonlocal current_plate_idx, is_flipped, is_learning_completed
        current_plate_idx = 0
        is_flipped = False
        is_learning_completed = False
        render_learning_view()

    def shuffle_and_restart():
        """Shuffle cards and restart session."""
        nonlocal learning_session_words, current_plate_idx, is_flipped, is_learning_completed
        random.shuffle(learning_session_words)
        current_plate_idx = 0
        is_flipped = False
        is_learning_completed = False
        render_learning_view()

    def render_learning_view():
        """Render the appropriate view inside learning_tab_content."""
        learning_tab_content.content = None
        if not is_learning_active:
            learning_tab_content.content = build_learning_config_view()
        elif is_learning_completed:
            learning_tab_content.content = build_learning_complete_view()
        else:
            learning_tab_content.content = build_learning_study_view()
        page.update()

    def switch_to_search_tab():
        """Helper to navigate to Search & Add tab."""
        tabs.selected_index = 0
        page.update()

    def on_tab_change(e):
        """Handle top-level tab switching."""
        load_saved_words()
        if tabs.selected_index == 2 and not is_learning_active:
            render_learning_view()

    def handle_keyboard_event(e: ft.KeyboardEvent):
        """Global keyboard shortcut listener for plates study session."""
        # Only active when in Learning Tab (index 2) during active study
        if tabs.selected_index == 2 and is_learning_active and not is_learning_completed:
            if e.key in ("ArrowLeft", "Arrow Left", "Left"):
                prev_plate()
            elif e.key in ("ArrowRight", "Arrow Right", "Right"):
                next_plate()
            elif e.key in (" ", "Space"):
                trigger_plate_flip()

    page.on_keyboard_event = handle_keyboard_event

    def load_saved_words():
        nonlocal cached_saved_words
        try:
            cached_saved_words = repo.list_words()
            apply_dictionary_filter()
            if not is_learning_active:
                render_learning_view()
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
                        search_tab_content,
                        saved_tab_content,
                        learning_tab_content,
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
