import tkinter as tk
from tkinter import ttk
from .document_management_view import AddDocumentDialog
import tkinter.messagebox as messagebox
from .emprunt_view import EmpruntView
from .user_view import UserView
from utils.tooltip import ToolTip
from .search_view import SearchView
from views.edit_document_dialog import EditDocumentDialog
from models.document import Livre, Magazine, Journal, OuvrageMultimedia

class DashboardView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        # Configuration du style
        style = ttk.Style()
        style.configure('Dashboard.TFrame', background='#f5f5f5')
        style.configure('Main.TFrame', background='#f5f5f5')
        style.configure('Content.TFrame', background='#f5f5f5')
        
        # Style pour les boutons normaux (bleu)
        style.configure('Menu.TButton', 
                       padding=5,
                       font=('Helvetica', 9))
        style.map('Menu.TButton',
                 background=[('!active', '#2196F3'), ('active', '#1976D2')],
                 foreground=[('!active', 'black'), ('active', 'black')])
        
        # Style pour le bouton déconnexion (rouge)
        style.configure('Logout.TButton', 
                       padding=5,
                       font=('Helvetica', 9, 'bold'))
        style.map('Logout.TButton',
                 background=[('!active', '#dc3545'), ('active', '#c82333')],
                 foreground=[('!active', 'black'), ('active', 'black')])
        
        # Style pour le bouton emprunter (vert)
        style.configure('Emprunt.TButton', 
                       padding=8,
                       font=('Helvetica', 10, 'bold'))
        style.map('Emprunt.TButton',
                 background=[('!active', '#28a745'), ('active', '#218838')],
                 foreground=[('!active', 'black'), ('active', 'black')])
        
        self.configure(style='Dashboard.TFrame', padding=(10, 5, 10, 10))
        
        # En-tête avec informations utilisateur et déconnexion
        self.setup_header()
        
        # Menu principal
        self.setup_menu()
        
        # Zone de contenu principal - Supprimer le padding vertical
        self.content_frame = ttk.Frame(self, style='Content.TFrame')
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=0)  # Changer pady=20 en pady=0
        
        # Afficher le catalogue par défaut
        self.show_catalogue()
    
    def setup_header(self):
        header_frame = ttk.Frame(self, style='Header.TFrame')
        header_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Info utilisateur
        user_info = ttk.Label(
            header_frame,
            text=f"Connecté en tant que : {self.controller.current_user.username}",
            font=('Helvetica', 10)
        )
        user_info.pack(side='left')
        
        # Bouton déconnexion en rouge
        ttk.Button(
            header_frame,
            text="Déconnexion",
            command=self.controller.logout,
            style='Logout.TButton'  # Utiliser le style rouge
        ).pack(side='right')
    
    def setup_menu(self):
        menu_frame = ttk.Frame(self, style='Main.TFrame')
        menu_frame.pack(fill='x', padx=20)
        
        # Boutons du menu
        catalogue_btn = ttk.Button(
            menu_frame,
            text="Catalogue",
            command=self.show_catalogue,
            style='Menu.TButton'
        )
        catalogue_btn.pack(side='left', padx=5)
        ToolTip(catalogue_btn, "Consulter la liste des documents disponibles")
        
        emprunts_btn = ttk.Button(
            menu_frame,
            text="Emprunts",
            command=self.show_emprunts,
            style='Menu.TButton'
        )
        emprunts_btn.pack(side='left', padx=5)
        ToolTip(emprunts_btn, "Gérer vos emprunts et demandes")
        
        # Boutons supplémentaires pour les administrateurs
        if self.controller.current_user.is_admin():
            ttk.Button(
                menu_frame,
                text="Gestion Documents",
                command=self.show_gestion_documents,
                style='Menu.TButton'
            ).pack(side='left', padx=5)
            
            ttk.Button(
                menu_frame,
                text="Gestion Utilisateurs",
                command=self.show_gestion_utilisateurs,
                style='Menu.TButton'
            ).pack(side='left', padx=5)
        
        # Ajouter le bouton de recherche avancée
        search_btn = ttk.Button(
            menu_frame,
            text="Recherche avancée",
            command=self.show_search,
            style='Menu.TButton'
        )
        search_btn.pack(side='left', padx=5)
        ToolTip(search_btn, "Recherche avancée dans le catalogue")
    
    def show_catalogue(self):
        # Nettoyer le contenu
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Configuration du style pour le catalogue
        style = ttk.Style()
        style.configure("Modern.Treeview", 
                       background="white",
                       foreground="black",
                       rowheight=30,
                       fieldbackground="white",
                       font=('Helvetica', 10))
        style.configure("Modern.Treeview.Heading",
                       background="#e1e1e1",
                       foreground="black",
                       relief='flat',
                       font=('Helvetica', 10, 'bold'),
                       padding=(10, 5))
        style.map("Modern.Treeview",
                 background=[("selected", "#2196F3")],
                 foreground=[("selected", "white")])
        
        # Frame principal sans padding
        main_frame = ttk.Frame(self.content_frame, style='Content.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        # Bouton d'emprunt en haut avec style spécial
        top_frame = ttk.Frame(main_frame, style='Content.TFrame')
        top_frame.pack(fill='x', padx=2, pady=(0, 10))
        
        emprunt_btn = ttk.Button(
            top_frame,
            text="​Emprunter le document sélectionné​",
            command=self.demander_emprunt,
            style='Emprunt.TButton'
        )
        emprunt_btn.pack(side='left', padx=5)
        
        # Barre d'outils moderne
        toolbar = ttk.Frame(main_frame, style='Content.TFrame')
        toolbar.pack(fill='x', padx=2, pady=(0, 5))
        
        # Tableau moderne
        columns = ('ID', 'Type', 'Titre', 'Status', 'Détails')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', 
                                height=20, style="Modern.Treeview")
        
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
        
        # Placement direct du tableau et scrollbar sans frame intermédiaire
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        # Chargement des documents avec alternance de couleurs
        documents = self.controller.get_all_documents()
        for i, doc in enumerate(documents):
            tags = ('evenrow',) if i % 2 == 0 else ('oddrow',)
            self.tree.insert('', 'end', values=(
                doc.id,
                doc.__class__.__name__,
                doc.titre,
                doc.status,
                str(doc.get_details())
            ), tags=tags)
        
        # Configuration des couleurs alternées
        self.tree.tag_configure('oddrow', background='#f8f9fa')
        self.tree.tag_configure('evenrow', background='white')
        
        # Menu contextuel moderne
        self.context_menu = tk.Menu(self, tearoff=0, font=('Helvetica', 10),
                                   background='white', foreground='black')
        if self.controller.current_user.is_admin():
            self.context_menu.add_command(label="✏️ Modifier", command=self.modifier_document)
            self.context_menu.add_command(label="🗑️ Supprimer", command=self.supprimer_document)
            self.context_menu.add_separator()
        self.context_menu.add_command(label="📚 Emprunter", command=self.demander_emprunt)
        
        self.tree.bind('<Button-3>', self.show_context_menu)
        self.tree.bind('<Double-1>', lambda e: self.demander_emprunt())
    
    def show_emprunts(self):
        # Nettoyer le contenu
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Afficher la vue des emprunts
        emprunt_view = EmpruntView(self.content_frame, self.controller)
        emprunt_view.pack(fill='both', expand=True)
    
    def show_gestion_documents(self):
        # Vérifier les droits d'administration
        if not self.controller.current_user.is_admin():
            messagebox.showerror("Erreur", "Accès non autorisé")
            return
        
        # Nettoyer le contenu
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Frame principal pour la gestion des documents
        self.gestion_frame = ttk.Frame(self.content_frame)
        self.gestion_frame.pack(fill='both', expand=True)
        
        # Frame pour les actions
        action_frame = ttk.LabelFrame(self.gestion_frame, text="Actions", padding="10")
        action_frame.pack(fill='x', padx=5, pady=5)
        
        # Boutons de gestion
        ttk.Button(
            action_frame,
            text="Ajouter un document",
            command=self.ajouter_document,
            style='Menu.TButton'
        ).pack(side='left', padx=5)
        
        ttk.Button(
            action_frame,
            text="Modifier document",
            command=self.modifier_document,
            style='Menu.TButton'
        ).pack(side='left', padx=5)
        
        ttk.Button(
            action_frame,
            text="Supprimer sélection",
            command=self.supprimer_document,
            style='Menu.TButton'
        ).pack(side='left', padx=5)
        
        # Frame pour la liste des documents
        self.list_frame = ttk.LabelFrame(self.gestion_frame, text="Liste des documents", padding="10")
        self.list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Afficher les documents
        self.afficher_documents_gestion()

    def afficher_documents_gestion(self):
        # Nettoyer le list_frame
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        # Créer le tableau des documents avec padding réduit
        columns = ('ID', 'Type', 'Titre', 'Status', 'Détails')
        self.tree = ttk.Treeview(self.list_frame, columns=columns, show='headings', height=15)
        
        # Configuration des colonnes
        column_widths = {
            'ID': 50,
            'Type': 100,
            'Titre': 300,
            'Status': 100,
            'Détails': 400
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[col], anchor='w')
        
        # Placement direct du tree et scrollbar sans frame intermédiaire
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(self.list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        # Charger les documents
        documents = self.controller.get_all_documents()
        for doc in documents:
            self.tree.insert('', 'end', values=(
                doc.id,
                doc.__class__.__name__,
                doc.titre,
                doc.status,
                str(doc.get_details())
            ))
    
    def show_gestion_utilisateurs(self):
        # Nettoyer le contenu
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Afficher la vue de gestion des utilisateurs
        user_view = UserView(self.content_frame, self.controller)
        user_view.pack(fill='both', expand=True)

    def ajouter_document(self):
        if not self.controller.current_user.is_admin():
            messagebox.showerror("Erreur", "Accès non autorisé")
            return
        dialog = AddDocumentDialog(self, self.controller, self.afficher_documents_gestion)
        dialog.grab_set()

    def show_context_menu(self, event):
        try:
            selection = self.tree.identify_region(event.x, event.y)
            if selection == "cell":
                item = self.tree.identify_item(event.x, event.y)
                if item:
                    context_menu = tk.Menu(self, tearoff=0)
                    if self.controller.current_user.is_admin():
                        context_menu.add_command(label="Modifier", 
                                              command=self.modifier_document)
                        context_menu.add_command(label="Supprimer", 
                                              command=self.supprimer_document)
                        context_menu.add_separator()
                    context_menu.add_command(label="Demander l'emprunt", 
                                          command=self.demander_emprunt)
                    context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            if 'context_menu' in locals():
                context_menu.grab_release()

    def demander_emprunt(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un document")
            return
        
        item = self.tree.item(selection[0])
        doc_id = item['values'][0]
        titre = item['values'][2]
        status = item['values'][3]
        
        if status != 'disponible':
            messagebox.showwarning("Attention", "Ce document n'est pas disponible")
            return
        
        if messagebox.askyesno("Demande d'emprunt", 
                              f"Voulez-vous faire une demande d'emprunt pour '{titre}' ?"):
            success, message = self.controller.demander_emprunt(doc_id)
            if success:
                messagebox.showinfo("Succès", message)
                self.show_catalogue()  # Rafraîchir la liste
            else:
                messagebox.showerror("Erreur", message) 

    def modifier_document(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un document à modifier")
            return
        
        item = self.tree.item(selection[0])
        doc_id = item['values'][0]
        
        # Récupérer le document
        document = self.controller.get_document(doc_id)
        if not document:
            messagebox.showerror("Erreur", "Document introuvable")
            return
        
        # Ouvrir la boîte de dialogue d'édition
        dialog = EditDocumentDialog(self, self.controller, document, self.afficher_documents_gestion)
        dialog.grab_set()

    def supprimer_document(self):
        if not self.controller.current_user.is_admin():
            messagebox.showerror("Erreur", "Accès non autorisé")
            return
        
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un document à supprimer")
            return
        
        item = self.tree.item(selection[0])
        doc_id = item['values'][0]
        titre = item['values'][2]
        
        if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer le document '{titre}' ?"):
            if self.controller.supprimer_document(doc_id):
                messagebox.showinfo("Succès", "Document supprimé avec succès")
                self.afficher_documents_gestion()
            else:
                messagebox.showerror("Erreur", "Impossible de supprimer le document") 

    def show_search(self):
        # Nettoyer le contenu
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Afficher la vue de recherche
        search_view = SearchView(self.content_frame, self.controller)
        search_view.pack(fill='both', expand=True) 