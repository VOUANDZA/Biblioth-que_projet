from tkinter import ttk
import json
import os

class ThemeManager:
    def __init__(self):
        self.current_theme = 'light'
        self.themes = {
            'light': {
                'bg': '#ffffff',
                'fg': '#000000',
                'button_bg': '#f0f0f0',
                'selected_bg': '#0078d7',
                'selected_fg': '#ffffff',
                'tree_bg': '#ffffff',
                'tree_selected': '#e5f3ff'
            },
            'dark': {
                'bg': '#2d2d2d',
                'fg': '#ffffff',
                'button_bg': '#3d3d3d',
                'selected_bg': '#0078d7',
                'selected_fg': '#ffffff',
                'tree_bg': '#2d2d2d',
                'tree_selected': '#404040'
            }
        }

    def apply_theme(self, root, theme_name='light'):
        self.current_theme = theme_name
        theme = self.themes[theme_name]
        
        style = ttk.Style()
        style.theme_use('clam')  # Base theme
        
        # Configuration générale
        style.configure('.',
            background=theme['bg'],
            foreground=theme['fg'],
            fieldbackground=theme['bg']
        )
        
        # Boutons
        style.configure('TButton',
            background=theme['button_bg'],
            padding=5
        )
        
        # Treeview
        style.configure('Treeview',
            background=theme['tree_bg'],
            fieldbackground=theme['tree_bg'],
            foreground=theme['fg']
        )
        
        style.map('Treeview',
            background=[('selected', theme['tree_selected'])],
            foreground=[('selected', theme['selected_fg'])]
        )

    def toggle_theme(self, root):
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme(root, new_theme) 