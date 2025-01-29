import tkinter as tk
from tkinter import ttk, messagebox

class DemandeEmpruntView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        # Tableau des demandes
        columns = ('ID', 'Utilisateur', 'Document', 'Type', 'Date demande', 'Actions')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=15)
        
        # Configuration des colonnes
        for col in columns:
            self.tree.heading(col, text=col)
            if col in ('ID', 'Type'):
                self.tree.column(col, width=70)
            elif col == 'Actions':
                self.tree.column(col, width=150)
            else:
                self.tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Placement
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.charger_demandes()
    
    def charger_demandes(self):
        # Nettoyer la liste
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Charger les demandes
        demandes = self.controller.get_demandes_emprunt()
        for demande in demandes:
            demande_id, user_id, doc_id, date_demande, username, titre, type_doc = demande
            
            item = self.tree.insert('', 'end', values=(
                demande_id, username, titre, type_doc, date_demande, ''
            ))
            
            # Ajouter les boutons d'action
            frame = ttk.Frame(self.tree)
            ttk.Button(frame, text="✓", width=3,
                      command=lambda d=demande_id: self.valider_demande(d)).pack(side='left', padx=2)
            ttk.Button(frame, text="✗", width=3,
                      command=lambda d=demande_id: self.refuser_demande(d)).pack(side='left', padx=2)
            
            self.tree.set(item, 'Actions', '')
            self.tree.window_create(self.tree.bbox(item, 'Actions')[0], window=frame)
    
    def valider_demande(self, demande_id):
        if messagebox.askyesno("Confirmation", "Valider cette demande d'emprunt ?"):
            success, message = self.controller.traiter_demande_emprunt(demande_id, 'validee')
            if success:
                messagebox.showinfo("Succès", message)
                self.charger_demandes()
            else:
                messagebox.showerror("Erreur", message)
    
    def refuser_demande(self, demande_id):
        commentaire = tk.simpledialog.askstring("Motif", "Motif du refus :")
        if commentaire is not None:
            success, message = self.controller.traiter_demande_emprunt(
                demande_id, 'refusee', commentaire)
            if success:
                messagebox.showinfo("Succès", message)
                self.charger_demandes()
            else:
                messagebox.showerror("Erreur", message) 