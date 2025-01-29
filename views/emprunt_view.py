import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class EmpruntView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        # Création des onglets
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Onglet Mes Emprunts
        self.mes_emprunts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.mes_emprunts_frame, text='Mes Emprunts')
        self.setup_mes_emprunts()
        
        # Onglet Mes Demandes
        self.mes_demandes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.mes_demandes_frame, text='Mes Demandes')
        self.setup_mes_demandes()
        
        # Onglet Demandes (pour admin seulement)
        if self.controller.current_user.is_admin():
            self.demandes_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.demandes_frame, text='Gestion Demandes')
            self.setup_demandes()
    
    def setup_mes_emprunts(self):
        # Frame principal
        main_frame = ttk.Frame(self.mes_emprunts_frame)
        main_frame.pack(fill='both', expand=True)
        
        # Tableau des emprunts
        columns = ('ID', 'Document', 'Type', 'Date emprunt', 'Date retour prévue', 
                  'Date retour', 'Status', 'Pénalités', 'Actions')
        self.emprunts_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        # Configuration des colonnes
        for col in columns:
            self.emprunts_tree.heading(col, text=col)
            if col in ('ID', 'Type', 'Status'):
                self.emprunts_tree.column(col, width=100)
            elif col == 'Pénalités':
                self.emprunts_tree.column(col, width=80)
            else:
                self.emprunts_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.emprunts_tree.yview)
        self.emprunts_tree.configure(yscrollcommand=scrollbar.set)
        
        # Placement
        self.emprunts_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Frame pour les actions
        action_frame = ttk.Frame(self.mes_emprunts_frame)
        action_frame.pack(fill='x', pady=5)
        
        # Bouton pour retourner le document sélectionné
        ttk.Button(
            action_frame,
            text="Retourner le document",
            command=self.retourner_document
        ).pack(side='left', padx=5)
        
        self.charger_emprunts()
    
    def setup_demandes(self):
        # Frame pour les demandes en attente
        demandes_frame = ttk.Frame(self.demandes_frame)
        demandes_frame.pack(fill='both', expand=True)
        
        # Tableau des demandes
        columns = ('ID', 'Utilisateur', 'Document', 'Type', 'Date demande', 'Actions')
        self.demandes_tree = ttk.Treeview(demandes_frame, columns=columns, show='headings', height=15)
        
        # Configuration des colonnes
        for col in columns:
            self.demandes_tree.heading(col, text=col)
            if col in ('ID', 'Type'):
                self.demandes_tree.column(col, width=70)
            elif col == 'Actions':
                self.demandes_tree.column(col, width=150)
            else:
                self.demandes_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(demandes_frame, orient='vertical', command=self.demandes_tree.yview)
        self.demandes_tree.configure(yscrollcommand=scrollbar.set)
        
        # Placement
        self.demandes_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Ajouter un gestionnaire d'événements pour le double-clic
        self.demandes_tree.bind('<Double-Button-1>', self.on_demande_double_click)
        
        # Charger les demandes
        self.charger_demandes()
    
    def charger_emprunts(self):
        # Nettoyer la liste actuelle
        for item in self.emprunts_tree.get_children():
            self.emprunts_tree.delete(item)
        
        # Charger les emprunts
        emprunts = self.controller.get_user_emprunts()
        
        # Remplir le tableau
        for emprunt in emprunts:
            # Calculer les pénalités
            penalites = emprunt.calculer_penalites() if hasattr(emprunt, 'calculer_penalites') else 0
            penalites_str = f"{penalites:.2f}€" if penalites > 0 else "Pas de pénalité"
            
            # Obtenir le statut
            status = emprunt.get_status()
            
            # Formater les dates
            date_emprunt = emprunt.date_emprunt.strftime('%Y-%m-%d')
            date_retour_prevue = emprunt.date_retour_prevue.strftime('%Y-%m-%d') if emprunt.date_retour_prevue else ""
            date_retour = emprunt.date_retour.strftime('%Y-%m-%d') if emprunt.date_retour else ""
            
            # Déterminer les actions possibles
            actions = "Retourner" if not emprunt.date_retour else ""
            
            # Insérer dans le tableau
            item = self.emprunts_tree.insert('', 'end', values=(
                emprunt.document.id,
                emprunt.document.titre,
                emprunt.document.__class__.__name__,
                date_emprunt,
                date_retour_prevue,
                date_retour,
                status,
                penalites_str,
                actions
            ))
            
            # Colorer en rouge si en retard
            if status == "En retard":
                self.emprunts_tree.tag_configure('retard', foreground='red')
                self.emprunts_tree.item(item, tags=('retard',))
    
    def charger_demandes(self):
        # Nettoyer la liste
        for item in self.demandes_tree.get_children():
            self.demandes_tree.delete(item)
        
        # Charger les demandes
        demandes = self.controller.get_demandes_emprunt()
        for demande in demandes:
            demande_id, user_id, doc_id, date_demande, username, titre, type_doc = demande
            
            # Créer un frame pour les boutons
            frame = ttk.Frame(self.demandes_frame)
            ttk.Button(frame, text="Valider", width=8,
                      command=lambda d=demande_id: self.valider_demande(d)).pack(side='left', padx=2)
            ttk.Button(frame, text="Refuser", width=8,
                      command=lambda d=demande_id: self.refuser_demande(d)).pack(side='left', padx=2)
            
            # Insérer la ligne dans le tableau
            self.demandes_tree.insert('', 'end', values=(
                demande_id,
                username,
                titre,
                type_doc,
                date_demande,
                "Valider/Refuser"  # Texte pour la colonne Actions
            ))
    
    def retourner_document(self):
        selection = self.emprunts_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un document à retourner")
            return
        
        item = self.emprunts_tree.item(selection[0])
        doc_id = item['values'][0]  # Supposons que l'ID est dans la première colonne
        titre = item['values'][1]   # Supposons que le titre est dans la deuxième colonne
        
        if messagebox.askyesno("Confirmation", f"Voulez-vous retourner le document '{titre}' ?"):
            if self.controller.retourner_document(doc_id):
                messagebox.showinfo("Succès", "Document retourné avec succès")
                # Rafraîchir la liste des emprunts
                self.charger_emprunts()
                # Rafraîchir aussi la liste des demandes si elle existe
                if hasattr(self, 'charger_mes_demandes'):
                    self.charger_mes_demandes()
            else:
                messagebox.showerror("Erreur", "Impossible de retourner le document")
    
    def valider_demande(self, demande_id):
        if messagebox.askyesno("Confirmation", "Valider cette demande d'emprunt ?"):
            success, message = self.controller.traiter_demande_emprunt(demande_id, 'validee')
            if success:
                messagebox.showinfo("Succès", message)
                self.charger_demandes()
                self.charger_emprunts()
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
    
    def on_demande_double_click(self, event):
        item = self.demandes_tree.selection()[0]
        demande_id = self.demandes_tree.item(item)['values'][0]
        
        # Créer une fenêtre popup pour les actions
        popup = tk.Toplevel(self)
        popup.title("Actions")
        popup.geometry("200x100")
        
        ttk.Button(popup, text="Valider",
                  command=lambda: [self.valider_demande(demande_id), popup.destroy()]).pack(pady=5)
        ttk.Button(popup, text="Refuser",
                  command=lambda: [self.refuser_demande(demande_id), popup.destroy()]).pack(pady=5) 
    
    def setup_mes_demandes(self):
        # Frame principal
        main_frame = ttk.Frame(self.mes_demandes_frame)
        main_frame.pack(fill='both', expand=True)
        
        # Tableau des demandes
        columns = ('ID', 'Document', 'Type', 'Date demande', 'Status', 'Commentaire', 'Actions')
        self.mes_demandes_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        # Configuration des colonnes
        for col in columns:
            self.mes_demandes_tree.heading(col, text=col)
            if col in ('ID', 'Type', 'Status'):
                self.mes_demandes_tree.column(col, width=100)
            elif col == 'Actions':
                self.mes_demandes_tree.column(col, width=150)
            else:
                self.mes_demandes_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.mes_demandes_tree.yview)
        self.mes_demandes_tree.configure(yscrollcommand=scrollbar.set)
        
        # Placement
        self.mes_demandes_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Frame pour les actions
        action_frame = ttk.Frame(self.mes_demandes_frame)
        action_frame.pack(fill='x', pady=5)
        
        # Boutons d'action
        ttk.Button(
            action_frame,
            text="Annuler la demande",
            command=self.annuler_demande
        ).pack(side='left', padx=5)
        
        ttk.Button(
            action_frame,
            text="Relancer la demande",
            command=self.relancer_demande
        ).pack(side='left', padx=5)
        
        self.charger_mes_demandes()
    
    def charger_mes_demandes(self):
        # Nettoyer la liste
        for item in self.mes_demandes_tree.get_children():
            self.mes_demandes_tree.delete(item)
        
        # Charger les demandes
        demandes = self.controller.get_mes_demandes()
        for demande in demandes:
            item = self.mes_demandes_tree.insert('', 'end', values=(
                demande['id'],
                demande['titre_document'],
                demande['type_document'],
                demande['date_demande'],
                demande['status'],
                demande['commentaire'] or '',
                'Annuler' if demande['status'] == 'en_attente' else 'Relancer'
            ))
            
            # Colorer selon le statut
            if demande['status'] == 'refusee':
                self.mes_demandes_tree.tag_configure('refusee', foreground='red')
                self.mes_demandes_tree.item(item, tags=('refusee',))
            elif demande['status'] == 'validee':
                self.mes_demandes_tree.tag_configure('validee', foreground='green')
                self.mes_demandes_tree.item(item, tags=('validee',))
    
    def annuler_demande(self):
        selection = self.mes_demandes_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une demande")
            return
        
        item = self.mes_demandes_tree.item(selection[0])
        demande_id = item['values'][0]
        status = item['values'][4]
        
        if status != 'en_attente':
            messagebox.showwarning("Attention", "Seules les demandes en attente peuvent être annulées")
            return
        
        if messagebox.askyesno("Confirmation", "Voulez-vous annuler cette demande ?"):
            if self.controller.annuler_demande_emprunt(demande_id):
                messagebox.showinfo("Succès", "Demande annulée avec succès")
                self.charger_mes_demandes()
            else:
                messagebox.showerror("Erreur", "Impossible d'annuler la demande")
    
    def relancer_demande(self):
        selection = self.mes_demandes_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une demande")
            return
        
        item = self.mes_demandes_tree.item(selection[0])
        demande_id = item['values'][0]
        status = item['values'][4]
        
        if status == 'en_attente':
            messagebox.showwarning("Attention", "Cette demande est déjà en cours")
            return
        
        if messagebox.askyesno("Confirmation", "Voulez-vous relancer cette demande ?"):
            if self.controller.relancer_demande_emprunt(demande_id):
                messagebox.showinfo("Succès", "Demande relancée avec succès")
                self.charger_mes_demandes()
            else:
                messagebox.showerror("Erreur", "Impossible de relancer la demande")
    
    def modifier_document(self):
        selection = self.emprunts_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un document à modifier")
            return
        
        item = self.emprunts_tree.item(selection[0])
        doc_id = item['values'][0]
        
        # Récupérer le document
        document = self.controller.get_document(doc_id)
        if not document:
            messagebox.showerror("Erreur", "Document introuvable")
            return
        
        # Ouvrir la boîte de dialogue d'édition
        dialog = EditDocumentDialog(self, self.controller, document, self.charger_documents)
        dialog.grab_set() 