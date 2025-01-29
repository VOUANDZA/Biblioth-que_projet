import tkinter as tk
from tkinter import ttk
from datetime import datetime

class SearchView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        # Frame pour les critères de recherche
        search_frame = ttk.LabelFrame(self, text="Critères de recherche", padding="10")
        search_frame.pack(fill='x', padx=5, pady=5)
        
        # Titre
        ttk.Label(search_frame, text="Titre:").grid(row=0, column=0, padx=5, pady=5)
        self.titre_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.titre_var).grid(row=0, column=1, padx=5, pady=5)
        
        # Type de document
        ttk.Label(search_frame, text="Type:").grid(row=1, column=0, padx=5, pady=5)
        self.type_var = tk.StringVar()
        types = ['', 'livre', 'magazine', 'journal', 'multimedia']
        ttk.Combobox(search_frame, textvariable=self.type_var, values=types).grid(row=1, column=1, padx=5, pady=5)
        
        # Auteur
        ttk.Label(search_frame, text="Auteur:").grid(row=2, column=0, padx=5, pady=5)
        self.auteur_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.auteur_var).grid(row=2, column=1, padx=5, pady=5)
        
        # Éditeur
        ttk.Label(search_frame, text="Éditeur:").grid(row=3, column=0, padx=5, pady=5)
        self.editeur_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.editeur_var).grid(row=3, column=1, padx=5, pady=5)
        
        # Bouton de recherche
        ttk.Button(search_frame, text="Rechercher", command=self.rechercher).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Tableau des résultats
        self.setup_results_table()
    
    def setup_results_table(self):
        # Frame pour les résultats
        results_frame = ttk.LabelFrame(self, text="Résultats", padding="10")
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configuration du tableau
        columns = ('ID', 'Type', 'Titre', 'Status', 'Détails')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        # Configuration des colonnes
        column_widths = {
            'ID': 60,
            'Type': 120,
            'Titre': 300,
            'Status': 100,
            'Détails': 360
        }
        
        for col in columns:
            self.tree.heading(col, text=col.upper(), anchor='w')
            self.tree.column(col, width=column_widths[col], anchor='w')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Placement
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def rechercher(self):
        # Nettoyer les résultats précédents
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Préparer les critères
        criteria = {
            'titre': self.titre_var.get(),
            'type': self.type_var.get(),
            'auteur': self.auteur_var.get(),
            'editeur': self.editeur_var.get()
        }
        
        # Effectuer la recherche
        results = self.controller.search_documents(criteria)
        
        # Afficher les résultats
        for doc in results:
            self.tree.insert('', 'end', values=(
                doc.id,
                doc.__class__.__name__,
                doc.titre,
                doc.status,
                str(doc.get_details())
            )) 