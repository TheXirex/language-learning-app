"""
Flashcards Tab View.
"""

from __future__ import annotations

import asyncio
import random
from typing import Callable, List, Optional, Set
import flet as ft

from ui.components.plate_card import build_plate_card_shell
from ui.theme import get_level_color


class LearningView:
    """View managing the interactive flashcard learning sessions."""

    def __init__(
        self,
        page: ft.Page,
        get_saved_words: Callable[[], List[dict]],
        on_navigate_to_search: Optional[Callable[[], None]] = None,
        show_snack: Optional[Callable[[str, str], None]] = None,
    ):
        self.page = page
        self.get_saved_words = get_saved_words
        self.on_navigate_to_search = on_navigate_to_search
        self.show_snack = show_snack or (lambda msg, col: None)

        # Learning Configuration State
        self.selected_levels: Set[str] = set()       # Empty or populated with selected levels
        self.selected_pos: Set[str] = set()          # Empty or populated with selected POS
        self.study_mode: str = "word_to_def"         # "word_to_def" or "def_to_word"
        self._initialized_filters: bool = False

        # Learning Session Active State
        self.learning_session_words: List[dict] = []
        self.current_plate_idx: int = 0
        self.is_flipped: bool = False
        self.is_flipping: bool = False
        self.is_learning_active: bool = False
        self.is_learning_completed: bool = False

        # AnimatedSwitcher plate component
        self.plate_card_switcher = ft.AnimatedSwitcher(
            content=None,
            transition=ft.AnimatedSwitcherTransition.SCALE,
            duration=260,
            reverse_duration=260,
            switch_in_curve=ft.AnimationCurve.EASE_OUT_CUBIC,
            switch_out_curve=ft.AnimationCurve.EASE_IN_CUBIC,
        )

        # Root container
        self.control = ft.Container(expand=True, padding=10)

    def get_available_level_tags(self) -> List[str]:
        """Extract all unique CEFR level tags present in cached dictionary words from DB."""
        levels = set()
        for w in self.get_saved_words():
            for d in w.get("definitions", []):
                lvl = (d.get("level") or "").strip().upper()
                if lvl:
                    levels.add(lvl)
        cefr_order = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}
        return sorted(list(levels), key=lambda x: (cefr_order.get(x, 99), x))

    def get_available_pos_tags(self) -> List[str]:
        """Extract all unique POS tags present in cached dictionary words from DB."""
        tags = set()
        for w in self.get_saved_words():
            for d in w.get("definitions", []):
                p = (d.get("pos") or "").strip().lower()
                if p:
                    tags.add(p)
        return sorted(list(tags))

    def get_filtered_learning_words(self) -> List[dict]:
        """Filter words according to selected levels and POS categories."""
        saved_words = self.get_saved_words()
        if not saved_words:
            return []

        available_levels = set(self.get_available_level_tags())
        available_pos = set(self.get_available_pos_tags())

        # If user explicitly unselected all levels or all POS
        if available_levels and self.selected_levels is not None and len(self.selected_levels) == 0:
            return []
        if available_pos and self.selected_pos is not None and len(self.selected_pos) == 0:
            return []

        # Only apply level filtering if a strict subset of levels is selected
        filter_by_level = bool(available_levels and self.selected_levels is not None and self.selected_levels != available_levels)

        # Only apply POS filtering if a strict subset of POS is selected
        filter_by_pos = bool(available_pos and self.selected_pos is not None and self.selected_pos != available_pos)

        if not filter_by_level and not filter_by_pos:
            return list(saved_words)

        matched = []
        for w in saved_words:
            defs = w.get("definitions", [])
            if not defs:
                continue

            if filter_by_level:
                has_level = any(
                    (d.get("level") or "").strip().upper() in self.selected_levels
                    for d in defs
                )
                if not has_level:
                    continue

            if filter_by_pos:
                has_pos = any(
                    (d.get("pos") or "").strip().lower() in self.selected_pos
                    for d in defs
                )
                if not has_pos:
                    continue

            matched.append(w)

        return matched

    # -----------------------------------------------------------------------
    # Flip & Animation Workers
    # -----------------------------------------------------------------------
    def on_plate_hover(self, e):
        """Micro-elevation animation on mouse hover."""
        if not self.is_flipping:
            if e.data == "true":
                e.control.offset = ft.Offset(0, -0.015)
            else:
                e.control.offset = ft.Offset(0, 0)
            e.control.update()

    def build_current_plate_shell(self, flipped: bool) -> ft.Container:
        """Create shell container for the current study plate."""
        current_word = self.learning_session_words[self.current_plate_idx]
        return build_plate_card_shell(
            word_data=current_word,
            flipped=flipped,
            study_mode=self.study_mode,
            plate_idx=self.current_plate_idx,
            on_click=lambda e: self.trigger_plate_flip(),
            on_hover=self.on_plate_hover,
        )

    async def flip_worker(self):
        """Perform smooth AnimatedSwitcher card turnover."""
        try:
            self.is_flipped = not self.is_flipped
            self.plate_card_switcher.content = self.build_current_plate_shell(self.is_flipped)
            self.plate_card_switcher.update()
            await asyncio.sleep(0.28)
        except Exception:
            pass
        finally:
            self.is_flipping = False

    def trigger_plate_flip(self):
        """Smooth card flip turnover via AnimatedSwitcher."""
        if self.is_flipping or not self.learning_session_words:
            return
        self.is_flipping = True
        self.page.run_task(self.flip_worker)

    # -----------------------------------------------------------------------
    # Session Navigation
    # -----------------------------------------------------------------------
    def prev_plate(self):
        """Navigate to previous plate card."""
        if self.current_plate_idx > 0:
            self.current_plate_idx -= 1
            self.is_flipped = False
            self.render_learning_view()

    def next_plate(self):
        """Navigate to next plate card or complete session if at end."""
        if self.current_plate_idx < len(self.learning_session_words) - 1:
            self.current_plate_idx += 1
            self.is_flipped = False
            self.render_learning_view()
        else:
            self.is_learning_completed = True
            self.render_learning_view()

    def shuffle_current_deck(self):
        """Shuffle remaining cards in session."""
        if len(self.learning_session_words) > 1:
            random.shuffle(self.learning_session_words)
            self.current_plate_idx = 0
            self.is_flipped = False
            self.show_snack("Deck shuffled! Starting from card 1.", ft.Colors.INDIGO_700)
            self.render_learning_view()

    def start_learning_session(self):
        """Initialize and launch flashcard learning session."""
        matching = self.get_filtered_learning_words()
        if not matching:
            self.show_snack("No words match your selected filters. Please adjust filters.", ft.Colors.RED_700)
            return

        words_pool = list(matching)
        random.shuffle(words_pool)
        self.learning_session_words = words_pool

        self.current_plate_idx = 0
        self.is_flipped = False
        self.is_learning_active = True
        self.is_learning_completed = False
        self.render_learning_view()

    def restart_learning_session(self):
        """Restart session from card 1."""
        self.current_plate_idx = 0
        self.is_flipped = False
        self.is_learning_completed = False
        self.render_learning_view()

    def shuffle_and_restart(self):
        """Shuffle cards and restart session."""
        random.shuffle(self.learning_session_words)
        self.current_plate_idx = 0
        self.is_flipped = False
        self.is_learning_completed = False
        self.render_learning_view()

    def exit_learning_to_config(self):
        """Exit active study session and return to configuration view."""
        self.is_learning_active = False
        self.is_learning_completed = False
        self.render_learning_view()

    # -----------------------------------------------------------------------
    # View Builders (Config, Study, Complete)
    # -----------------------------------------------------------------------
    def build_learning_config_view(self) -> ft.Control:
        """Build the pre-session configuration screen with pure in-place reactive updates."""
        total_dict_count = len(self.get_saved_words())

        if total_dict_count == 0:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.MENU_BOOK_ROUNDED, size=54, color=ft.Colors.INDIGO_300),
                        ft.Text("Your Dictionary is Empty", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900),
                        ft.Text(
                            "Search and save words in the 'Search & Add' tab to start learning with flashcards!",
                            size=14,
                            color=ft.Colors.GREY_700,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Button(
                            "Go to Search & Add",
                            icon=ft.Icons.SEARCH,
                            bgcolor=ft.Colors.INDIGO_700,
                            color=ft.Colors.WHITE,
                            on_click=lambda e: self.on_navigate_to_search() if self.on_navigate_to_search else None,
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

        # 1. Study Direction Selector
        mode_w2d_text = ft.Text(
            "Word → Definition",
            color=ft.Colors.WHITE if self.study_mode == "word_to_def" else ft.Colors.BLUE_GREY_900,
            size=13,
            weight=ft.FontWeight.BOLD,
        )
        mode_w2d_btn = ft.Container(
            content=mode_w2d_text,
            bgcolor=ft.Colors.INDIGO_700 if self.study_mode == "word_to_def" else ft.Colors.WHITE,
            border=ft.Border.all(1.5 if self.study_mode == "word_to_def" else 1.0, ft.Colors.INDIGO_700 if self.study_mode == "word_to_def" else ft.Colors.GREY_300),
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
            on_click=lambda e: set_study_mode("word_to_def"),
        )

        mode_d2w_text = ft.Text(
            "Definition → Word",
            color=ft.Colors.WHITE if self.study_mode == "def_to_word" else ft.Colors.BLUE_GREY_900,
            size=13,
            weight=ft.FontWeight.BOLD,
        )
        mode_d2w_btn = ft.Container(
            content=mode_d2w_text,
            bgcolor=ft.Colors.INDIGO_700 if self.study_mode == "def_to_word" else ft.Colors.WHITE,
            border=ft.Border.all(1.5 if self.study_mode == "def_to_word" else 1.0, ft.Colors.INDIGO_700 if self.study_mode == "def_to_word" else ft.Colors.GREY_300),
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
            on_click=lambda e: set_study_mode("def_to_word"),
        )

        def set_study_mode(mode: str):
            self.study_mode = mode
            is_w2d = mode == "word_to_def"

            mode_w2d_btn.bgcolor = ft.Colors.INDIGO_700 if is_w2d else ft.Colors.WHITE
            mode_w2d_btn.border = ft.Border.all(1.5 if is_w2d else 1.0, ft.Colors.INDIGO_700 if is_w2d else ft.Colors.GREY_300)
            mode_w2d_text.color = ft.Colors.WHITE if is_w2d else ft.Colors.BLUE_GREY_900

            mode_d2w_btn.bgcolor = ft.Colors.INDIGO_700 if not is_w2d else ft.Colors.WHITE
            mode_d2w_btn.border = ft.Border.all(1.5 if not is_w2d else 1.0, ft.Colors.INDIGO_700 if not is_w2d else ft.Colors.GREY_300)
            mode_d2w_text.color = ft.Colors.WHITE if not is_w2d else ft.Colors.BLUE_GREY_900

            self.page.update()

        # 2. CEFR Level Selectors (Dynamically fetched from DB words)
        available_levels = self.get_available_level_tags()
        available_pos = self.get_available_pos_tags()

        avail_lvl_set = set(available_levels)
        avail_pos_set = set(available_pos)

        if not self._initialized_filters:
            self.selected_levels = set(avail_lvl_set)
            self.selected_pos = set(avail_pos_set)
            self._initialized_filters = True
        else:
            # If user had all levels selected previously (or levels was empty), select all currently available
            if not hasattr(self, "_prev_avail_levels") or self.selected_levels == self._prev_avail_levels or not self.selected_levels:
                self.selected_levels = set(avail_lvl_set)
            else:
                self.selected_levels = self.selected_levels.intersection(avail_lvl_set)

            if not hasattr(self, "_prev_avail_pos") or self.selected_pos == self._prev_avail_pos or not self.selected_pos:
                self.selected_pos = set(avail_pos_set)
            else:
                self.selected_pos = self.selected_pos.intersection(avail_pos_set)

        self._prev_avail_levels = set(avail_lvl_set)
        self._prev_avail_pos = set(avail_pos_set)

        level_chip_map: dict[str, ft.Container] = {}
        level_chips_row = ft.Row(wrap=True, spacing=8)

        # "All" chip for CEFR levels
        def make_all_levels_click():
            def on_click(e):
                if self.selected_levels == set(available_levels):
                    self.selected_levels.clear()
                else:
                    self.selected_levels = set(available_levels)
                update_config_view_state()
            return on_click

        is_all_levels_sel = bool(available_levels and self.selected_levels == set(available_levels))
        all_levels_chip = ft.Container(
            content=ft.Text(
                "All",
                color=ft.Colors.WHITE if is_all_levels_sel else ft.Colors.BLUE_GREY_800,
                size=11,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            bgcolor=ft.Colors.INDIGO_700 if is_all_levels_sel else ft.Colors.WHITE,
            border=ft.Border.all(1.5 if is_all_levels_sel else 1.0, ft.Colors.INDIGO_700 if is_all_levels_sel else ft.Colors.GREY_300),
            border_radius=6,
            height=28,
            padding=ft.Padding.symmetric(horizontal=10, vertical=0),
            alignment=ft.Alignment(0, 0),
            tooltip="All Levels" + (" (Selected)" if is_all_levels_sel else ""),
            on_click=make_all_levels_click(),
        )
        level_chips_row.controls.append(all_levels_chip)

        for lvl in available_levels:
            is_sel = lvl in self.selected_levels
            badge_color = get_level_color(lvl)

            def make_level_click(target_lvl=lvl):
                def on_click(e):
                    if target_lvl in self.selected_levels:
                        self.selected_levels.remove(target_lvl)
                    else:
                        self.selected_levels.add(target_lvl)
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


        # 3. Part of Speech Filter Chips (Dynamically fetched from DB words)
        pos_chip_map: dict[str, ft.Container] = {}
        pos_chips_row = ft.Row(wrap=True, spacing=8)

        # "All" chip for POS
        def make_all_pos_click():
            def on_click(e):
                if self.selected_pos == set(available_pos):
                    self.selected_pos.clear()
                else:
                    self.selected_pos = set(available_pos)
                update_config_view_state()
            return on_click

        is_all_pos_sel = bool(available_pos and self.selected_pos == set(available_pos))
        all_pos_chip = ft.Container(
            content=ft.Text(
                "All",
                color=ft.Colors.WHITE if is_all_pos_sel else ft.Colors.BLUE_GREY_800,
                size=11,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            bgcolor=ft.Colors.INDIGO_700 if is_all_pos_sel else ft.Colors.WHITE,
            border=ft.Border.all(1.5 if is_all_pos_sel else 1.0, ft.Colors.INDIGO_700 if is_all_pos_sel else ft.Colors.GREY_300),
            border_radius=6,
            height=28,
            padding=ft.Padding.symmetric(horizontal=10, vertical=0),
            alignment=ft.Alignment(0, 0),
            tooltip="All Parts of Speech" + (" (Selected)" if is_all_pos_sel else ""),
            on_click=make_all_pos_click(),
        )
        pos_chips_row.controls.append(all_pos_chip)

        for pos_tag in available_pos:
            is_sel = pos_tag in self.selected_pos

            def make_pos_click(target_pos=pos_tag):
                def on_click(e):
                    if target_pos in self.selected_pos:
                        self.selected_pos.remove(target_pos)
                    else:
                        self.selected_pos.add(target_pos)
                    update_config_view_state()
                return on_click

            pos_color = ft.Colors.INDIGO_700
            p_container = ft.Container(
                content=ft.Text(
                    pos_tag,
                    color=ft.Colors.WHITE if is_sel else ft.Colors.BLUE_GREY_800,
                    size=11,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                bgcolor=pos_color if is_sel else ft.Colors.WHITE,
                border=ft.Border.all(1.5 if is_sel else 1.0, pos_color if is_sel else ft.Colors.GREY_300),
                border_radius=6,
                height=28,
                padding=ft.Padding.symmetric(horizontal=10, vertical=0),
                alignment=ft.Alignment(0, 0),
                tooltip=f"POS: {pos_tag}" + (" (Selected)" if is_sel else ""),
                on_click=make_pos_click(),
            )
            pos_chip_map[pos_tag] = p_container
            pos_chips_row.controls.append(p_container)


        # Start Button
        start_btn_icon = ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color=ft.Colors.WHITE, size=22)
        start_btn_label = ft.Text(
            "Start Flashcards",
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
            on_click=lambda e: self.start_learning_session(),
            height=46,
        )

        def update_config_view_state():
            """In-place update of interactive configuration elements."""
            matching_words = self.get_filtered_learning_words()
            matching_count = len(matching_words)

            # 1. Update CEFR Level selectors + "All" chip
            is_all_levels_active = bool(available_levels and self.selected_levels == set(available_levels))
            all_levels_chip.bgcolor = ft.Colors.INDIGO_700 if is_all_levels_active else ft.Colors.WHITE
            all_levels_chip.border = ft.Border.all(1.5 if is_all_levels_active else 1.0, ft.Colors.INDIGO_700 if is_all_levels_active else ft.Colors.GREY_300)
            all_levels_chip.content.color = ft.Colors.WHITE if is_all_levels_active else ft.Colors.BLUE_GREY_800
            all_levels_chip.tooltip = "All Levels" + (" (Selected)" if is_all_levels_active else "")

            for lvl, c in level_chip_map.items():
                is_sel = lvl in self.selected_levels
                badge_color = get_level_color(lvl)
                c.bgcolor = badge_color if is_sel else ft.Colors.WHITE
                c.border = ft.Border.all(1.5 if is_sel else 1.0, badge_color if is_sel else ft.Colors.GREY_300)
                txt = c.content
                txt.color = ft.Colors.WHITE if is_sel else ft.Colors.BLUE_GREY_800
                c.tooltip = f"Level {lvl}" + (" (Selected)" if is_sel else "")

            # 2. Update POS chips + "All" chip
            is_all_pos_active = bool(available_pos and self.selected_pos == set(available_pos))
            all_pos_chip.bgcolor = ft.Colors.INDIGO_700 if is_all_pos_active else ft.Colors.WHITE
            all_pos_chip.border = ft.Border.all(1.5 if is_all_pos_active else 1.0, ft.Colors.INDIGO_700 if is_all_pos_active else ft.Colors.GREY_300)
            all_pos_chip.content.color = ft.Colors.WHITE if is_all_pos_active else ft.Colors.BLUE_GREY_800
            all_pos_chip.tooltip = "All Parts of Speech" + (" (Selected)" if is_all_pos_active else "")

            for pos_tag, c in pos_chip_map.items():
                is_sel = pos_tag in self.selected_pos
                pos_color = ft.Colors.INDIGO_700
                c.bgcolor = pos_color if is_sel else ft.Colors.WHITE
                c.border = ft.Border.all(1.5 if is_sel else 1.0, pos_color if is_sel else ft.Colors.GREY_300)
                txt = c.content
                txt.color = ft.Colors.WHITE if is_sel else ft.Colors.BLUE_GREY_800
                c.tooltip = f"POS: {pos_tag}" + (" (Selected)" if is_sel else "")

            # 3. Update Start Button
            start_button.disabled = matching_count == 0
            start_button.bgcolor = ft.Colors.INDIGO_700 if matching_count > 0 else ft.Colors.GREY_400
            words_suffix = f"{matching_count} word{'s' if matching_count != 1 else ''}"
            start_btn_label.value = f"Start Flashcards ({words_suffix})" if matching_count > 0 else "Select Words to Start"

            self.page.update()

        # Initial state setup
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
                                            ft.Text("Flashcards Setup", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_900),
                                            ft.Text("Filter by CEFR levels or parts of speech, then start active recall practice with flashcards.", size=12, color=ft.Colors.GREY_700),
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
                                    level_chips_row,
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Divider(height=1, color=ft.Colors.INDIGO_100),

                            # 2. Parts of Speech section
                            ft.Row(
                                [
                                    ft.Text("2. Part of Speech (POS) Filter:", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                                    pos_chips_row,
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),

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

    def build_learning_study_view(self) -> ft.Control:
        """Build the active study screen with the interactive plate and outer navigation arrows."""
        total_cards = len(self.learning_session_words)
        progress_val = (self.current_plate_idx + 1) / max(1, total_cards)

        # Update plate card switcher content
        self.plate_card_switcher.content = self.build_current_plate_shell(self.is_flipped)

        # Outer Left Navigation Arrow (<)
        is_first = self.current_plate_idx == 0
        left_arrow_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED,
                icon_size=24,
                icon_color=ft.Colors.INDIGO_900 if not is_first else ft.Colors.GREY_400,
                disabled=is_first,
                tooltip="Previous Card (← Left Arrow)",
                on_click=lambda e: self.prev_plate(),
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
        is_last = self.current_plate_idx == total_cards - 1
        right_arrow_btn = ft.Container(
            content=ft.IconButton(
                icon=ft.Icons.CHECK_ROUNDED if is_last else ft.Icons.ARROW_FORWARD_IOS_ROUNDED,
                icon_size=24,
                icon_color=ft.Colors.WHITE if is_last else ft.Colors.INDIGO_900,
                tooltip="Finish Session" if is_last else "Next Card (→ Right Arrow)",
                on_click=lambda e: self.next_plate(),
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
                f"Card {self.current_plate_idx + 1} / {total_cards}",
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
                                    on_click=lambda e: self.shuffle_current_deck(),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE_ROUNDED,
                                    icon_color=ft.Colors.INDIGO_700,
                                    tooltip="Quit",
                                    on_click=lambda e: self.exit_learning_to_config(),
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
                            self.plate_card_switcher,
                            right_arrow_btn,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=18,
                    ),
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                ),
            ],
            expand=True,
            spacing=10,
        )

    def build_learning_complete_view(self) -> ft.Control:
        """Build the congratulatory summary view when all cards in session have been practiced."""
        total_cards = len(self.learning_session_words)

        practiced_chips = []
        for w in self.learning_session_words:
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
                                on_click=lambda e: self.restart_learning_session(),
                            ),
                            ft.Button(
                                "Shuffle & Repeat",
                                icon=ft.Icons.SHUFFLE,
                                bgcolor=ft.Colors.GREEN_700,
                                color=ft.Colors.WHITE,
                                on_click=lambda e: self.shuffle_and_restart(),
                            ),
                            ft.OutlinedButton(
                                "Quit",
                                icon=ft.Icons.CLOSE_ROUNDED,
                                on_click=lambda e: self.exit_learning_to_config(),
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

    def render_learning_view(self):
        """Render the appropriate view inside self.control."""
        self.control.content = None
        if not self.is_learning_active:
            self.control.content = self.build_learning_config_view()
        elif self.is_learning_completed:
            self.control.content = self.build_learning_complete_view()
        else:
            self.control.content = self.build_learning_study_view()
        self.page.update()

    def handle_keyboard_event(self, e: ft.KeyboardEvent):
        """Global keyboard shortcut listener for plates study session."""
        if self.is_learning_active and not self.is_learning_completed:
            if e.key in ("ArrowLeft", "Arrow Left", "Left"):
                self.prev_plate()
            elif e.key in ("ArrowRight", "Arrow Right", "Right"):
                self.next_plate()
            elif e.key in (" ", "Space"):
                self.trigger_plate_flip()
