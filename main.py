import tkinter as tk
from tkinter import ttk
from views.main_window import MainWindow
from controllers.main_controller import MainController
import os

def main():
    # Créer le contrôleur
    controller = MainController()
    
    # Créer la fenêtre principale
    window = MainWindow(controller)
    
    # Définir l'icône de l'application avec chemin absolu
    try:
        # Obtenir le chemin absolu du répertoire du script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_dir, 'image', 'icon.png')
        icon = tk.PhotoImage(file=icon_path)
        window.iconphoto(True, icon)
    except Exception as e:
        print(f"Erreur lors du chargement de l'icône: {e}")
    
    # Lier la fenêtre au contrôleur
    controller.set_main_window(window)
    
    # Démarrer l'application
    window.mainloop()

if __name__ == "__main__":
    main() 