import tkinter as tk
from tkinter import ttk, messagebox
from models.document import Livre, Magazine, Journal, OuvrageMultimedia
from datetime import datetime

class DocumentView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        # Style
        style = ttk.Style()
        style.configure('Document.TFrame', background='white')
        self.configure(style='Document.TFrame', padding="20")
        
        # Frame pour les filtres et la recherche
        self.setup_search_frame()
        
        # Frame pour la liste des documents
        self.setup_document_list()
        
        # Frame pour les actions (ajouter/modifier/supprimer)
        if self.controller.current_user.is_admin():
            self.setup_action_frame()
    
    def setup_search_frame(self):
        search_frame = ttk.LabelFrame(self, text="Recherche", padding="10")
        search_frame.pack(fill='x', padx=5, pady=5)
        
        # Type de document
        ttk.Label(search_frame, text="Type:").pack(side='left', padx=5)
        self.type_var = tk.StringVar(value="tous")
        type_combo = ttk.Combobox(search_frame, textvariable=self.type_var,
                                 values=["tous", "livre", "magazine", "journal", "multimedia"])
        type_combo.pack(side='left', padx=5)
        
        # Recherche par titre
        ttk.Label(search_frame, text="Titre:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side='left', padx=5)
        
        # Bouton rechercher
        ttk.Button(search_frame, text="Rechercher",
                  command=self.rechercher).pack(side='left', padx=5)
    
    def setup_document_list(self):
        list_frame = ttk.Frame(self)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Création du tableau
        columns = ('ID', 'Type', 'Titre', 'Status', 'Détails')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Configuration des colonnes
        for col in columns:
            self.tree.heading(col, text=col)
            if col in ('Type', 'Status'):
                self.tree.column(col, width=100)
            elif col == 'ID':
                self.tree.column(col, width=50)
            elif col == 'Détails':
                self.tree.column(col, width=300)
            else:
                self.tree.column(col, width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Placement
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Ajouter un menu contextuel (clic droit) modifié
        self.context_menu = tk.Menu(self, tearoff=0)
        if self.controller.current_user.is_admin():
            self.context_menu.add_command(label="Supprimer", command=self.supprimer_document)
            self.context_menu.add_separator()
        self.context_menu.add_command(label="Demander l'emprunt", command=self.demander_emprunt)
        
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # Charger les documents
        self.charger_documents()
    
    def setup_action_frame(self):
        action_frame = ttk.Frame(self)
        action_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(action_frame, text="Ajouter",
                  command=self.ajouter_document).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Supprimer",
                  command=self.supprimer_document).pack(side='left', padx=5)
    
    def charger_documents(self):
        # Nettoyer la liste
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Charger les documents
        documents = self.controller.get_all_documents()
        for doc in documents:
            # Filtrer par type si nécessaire
            if self.type_var.get() != "tous" and doc.__class__.__name__.lower() != self.type_var.get():
                continue
            
            # Filtrer par titre si recherche
            if self.search_var.get() and self.search_var.get().lower() not in doc.titre.lower():
                continue
            
            self.tree.insert('', 'end', values=(
                doc.id,
                doc.__class__.__name__,
                doc.titre,
                doc.status,
                str(doc.get_details())
            ))
    
    def rechercher(self):
        self.charger_documents()
    
    def on_document_double_click(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        doc_id = item['values'][0]
        status = item['values'][3]
        
        if status == 'disponible':
            if messagebox.askyesno("Emprunter", "Voulez-vous emprunter ce document ?"):
                if self.controller.emprunter_document(doc_id):
                    messagebox.showinfo("Succès", "Document emprunté avec succès")
                    self.charger_documents()
                else:
                    messagebox.showerror("Erreur", "Impossible d'emprunter ce document")
        elif status == 'emprunté':
            if messagebox.askyesno("Retourner", "Voulez-vous retourner ce document ?"):
                if self.controller.retourner_document(doc_id):
                    messagebox.showinfo("Succès", "Document retourné avec succès")
                    self.charger_documents()
                else:
                    messagebox.showerror("Erreur", "Impossible de retourner ce document")

    def ajouter_document(self):
        # Implementation of adding a document
        pass

    def supprimer_document(self):
        # Implementation of deleting a document
        pass

    def show_context_menu(self, event):
        selection = self.tree.identify_region(event.x, event.y)
        if selection == "cell":
            item = self.tree.identify_item(event.x, event.y)
            if item:
                self.context_menu.post(event.x_root, event.y_root)

    def demander_emprunt(self):
        # Implementation of demanding an emprunt
        pass 