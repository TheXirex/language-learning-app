import os
import sys
import warnings
from pathlib import Path

# Suppress upstream deprecation warnings (e.g. from cryptography/pymongo)
warnings.filterwarnings("ignore")

# Add src to Python path so we can import modules
sys.path.append(str(Path(__file__).parent.parent / "src"))

import flet as ft
from modules.scrapper import run_spider
from modules.db.repository import WordRepository

def main(page: ft.Page):
    page.title = "Language Learning App"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    # Repositories
    repo = WordRepository()
    
    # State variables
    current_search_result = {}
    
    # UI Elements
    search_input = ft.TextField(hint_text="Enter a word to learn...", expand=True, on_submit=lambda e: perform_search())
    search_button = ft.Button("Search", on_click=lambda e: perform_search())
    search_loading = ft.ProgressRing(visible=False)
    
    search_result_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    save_button = ft.Button("Save", color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN, visible=False, on_click=lambda e: save_word())
    
    saved_list = ft.ListView(expand=True, spacing=10)
    
    def show_snack(msg: str, color: str):
        snack = ft.SnackBar(ft.Text(msg), bgcolor=color, open=True)
        page.overlay.append(snack)
        page.update()
    
    def build_definition_block(def_data: dict) -> ft.Container:
        badges = []
        if def_data.get("pos"):
            badges.append(ft.Container(content=ft.Text(def_data["pos"], color=ft.Colors.WHITE, size=12), bgcolor=ft.Colors.BLUE, padding=5, border_radius=5))
        if def_data.get("guideword"):
            badges.append(ft.Container(content=ft.Text(def_data["guideword"], color=ft.Colors.WHITE, size=12), bgcolor=ft.Colors.GREEN, padding=5, border_radius=5))
        if def_data.get("level"):
            badges.append(ft.Container(content=ft.Text(def_data["level"], color=ft.Colors.WHITE, size=12), bgcolor=ft.Colors.RED, padding=5, border_radius=5))
            
        examples_col = ft.Column(spacing=2)
        for ex in def_data.get("examples", []):
            examples_col.controls.append(ft.Text(f"• {ex}", italic=True, color=ft.Colors.GREY_700))
            
        return ft.Container(
            content=ft.Column([
                ft.Row(badges, wrap=True),
                ft.Text(def_data.get("definition", ""), weight=ft.FontWeight.BOLD),
                examples_col
            ], spacing=10),
            padding=15,
            border=ft.Border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            margin=ft.Margin.only(bottom=10)
        )

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
                search_result_column.controls.append(
                    ft.Text(current_search_result["word"], size=24, weight=ft.FontWeight.BOLD)
                )
                for d in current_search_result["definitions"]:
                    search_result_column.controls.append(build_definition_block(d))
                save_button.visible = True
            else:
                search_result_column.controls.append(ft.Text("No definitions found.", color=ft.Colors.RED))
                
        except Exception as e:
            search_result_column.controls.append(ft.Text(f"Error scraping: {e}", color=ft.Colors.RED))
            
        search_button.disabled = False
        search_loading.visible = False
        page.update()

    def save_word():
        nonlocal current_search_result
        if current_search_result:
            try:
                repo.save_word(current_search_result)
                show_snack("Word saved successfully!", ft.Colors.GREEN)
                
                # Clear search
                search_input.value = ""
                search_result_column.controls.clear()
                save_button.visible = False
                current_search_result = {}
                
                # Update saved list
                load_saved_words()
            except Exception as e:
                show_snack(f"Error saving word: {e}", ft.Colors.RED)
        page.update()

    def delete_word(word: str):
        try:
            repo.delete_word(word)
            show_snack("Word deleted successfully!", ft.Colors.GREEN)
            load_saved_words()
        except Exception as e:
            show_snack(f"Error deleting word: {e}", ft.Colors.RED)
            page.update()

    def load_saved_words():
        saved_list.controls.clear()
        try:
            words = repo.list_words()
            if not words:
                saved_list.controls.append(ft.Text("No saved words yet.", color=ft.Colors.GREY))
            else:
                for w in words:
                    definitions_col = ft.Column()
                    for d in w.get("definitions", []):
                        definitions_col.controls.append(build_definition_block(d))
                        
                    delete_btn = ft.IconButton(
                        icon=ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        on_click=lambda e, word_str=w["word"]: delete_word(word_str),
                        tooltip="Delete Word"
                    )
                    
                    tile = ft.ExpansionTile(
                        title=ft.Text(w["word"], weight=ft.FontWeight.BOLD),
                        trailing=delete_btn,
                        controls=[
                            ft.Container(content=definitions_col, padding=ft.Padding.only(left=15, right=15, bottom=15))
                        ]
                    )
                    saved_list.controls.append(tile)
        except Exception as e:
            saved_list.controls.append(ft.Text(f"Error loading words: {e}", color=ft.Colors.RED))
        
        page.update()

    # Layout
    search_tab_content = ft.Container(
        content=ft.Column([
            ft.Row([search_input, search_button, search_loading]),
            search_result_column,
            save_button
        ], expand=True),
        padding=10
    )
    
    saved_tab_content = ft.Container(
        content=saved_list,
        padding=10
    )

    tabs = ft.Tabs(
        length=2,
        expand=True,
        selected_index=0,
        content=ft.Column([
            ft.TabBar(
                tabs=[
                    ft.Tab(label="Search", icon=ft.Icons.SEARCH),
                    ft.Tab(label="Saved Words", icon=ft.Icons.BOOKMARKS),
                ],
                on_click=lambda e: load_saved_words()
            ),
            ft.TabBarView(
                expand=True,
                controls=[
                    search_tab_content,
                    saved_tab_content,
                ]
            )
        ], expand=True)
    )
    
    page.add(tabs)
    
    # Initial load
    load_saved_words()

if __name__ == "__main__":
    ft.run(main)
