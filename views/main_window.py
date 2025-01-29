import tkinter as tk
from tkinter import ttk
from .login_view import LoginView
from .dashboard_view import DashboardView

class MainWindow(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        
        self.controller = controller
        self.setup_window()
        self.setup_styles()
        
        # Frame principal qui contiendra toutes les vues
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill='both', expand=True)
        
        # Commencer par la vue de connexion
        self.show_login()
    
    def setup_window(self):
        self.title("Gestion de Bibliothèque")
        self.geometry("1024x768")
        self.minsize(800, 600)
        
        # Centrer la fenêtre
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1024) // 2
        y = (screen_height - 768) // 2
        self.geometry(f"+{x}+{y}")
    
    def setup_styles(self):
        style = ttk.Style()
        style.configure('Main.TFrame', background='white')
        style.configure('Header.TFrame', background='#f0f0f0')
        style.configure('Content.TFrame', background='white')
        
        # Style pour les boutons
        style.configure('Action.TButton', padding=10)
        style.configure('Menu.TButton', padding=5)
    
    def show_login(self):
        # Nettoyer le frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Afficher la vue de connexion
        login_view = LoginView(self.main_frame, self.controller)
        login_view.pack(fill='both', expand=True) 
    
    def show_dashboard(self):
        # Nettoyer le frame principal
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Afficher le tableau de bord
        dashboard_view = DashboardView(self.main_frame, self.controller)
        dashboard_view.pack(fill='both', expand=True) 