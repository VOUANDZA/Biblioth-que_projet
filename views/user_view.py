import tkinter as tk
from tkinter import ttk, messagebox
import hashlib

class UserView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        # Style
        style = ttk.Style()
        style.configure('User.TFrame', background='white')
        self.configure(style='User.TFrame', padding="20")
        
        # Titre
        ttk.Label(self, text="Gestion des Utilisateurs",
                 font=('Helvetica', 16, 'bold')).pack(pady=10)
        
        # Frame pour l'ajout/modification
        self.setup_edit_frame()
        
        # Frame pour la liste des utilisateurs
        self.setup_user_list()
    
    def setup_edit_frame(self):
        edit_frame = ttk.LabelFrame(self, text="Ajouter/Modifier un utilisateur", padding="10")
        edit_frame.pack(fill='x', padx=5, pady=5)
        
        # Username
        ttk.Label(edit_frame, text="Nom d'utilisateur:").grid(row=0, column=0, padx=5, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.username_var).grid(row=0, column=1, padx=5, pady=5)
        
        # Password
        ttk.Label(edit_frame, text="Mot de passe:").grid(row=1, column=0, padx=5, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.password_var, show="*").grid(row=1, column=1, padx=5, pady=5)
        
        # Role
        ttk.Label(edit_frame, text="Rôle:").grid(row=2, column=0, padx=5, pady=5)
        self.role_var = tk.StringVar(value="utilisateur")
        role_frame = ttk.Frame(edit_frame)
        role_frame.grid(row=2, column=1, padx=5, pady=5)
        ttk.Radiobutton(role_frame, text="Utilisateur", variable=self.role_var,
                       value="utilisateur").pack(side='left', padx=5)
        ttk.Radiobutton(role_frame, text="Administrateur", variable=self.role_var,
                       value="administrateur").pack(side='left', padx=5)
        
        # Boutons
        button_frame = ttk.Frame(edit_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Ajouter",
                  command=self.ajouter_utilisateur).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Modifier",
                  command=self.modifier_utilisateur).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Supprimer",
                  command=self.supprimer_utilisateur).pack(side='left', padx=5)
    
    def setup_user_list(self):
        list_frame = ttk.Frame(self)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Création du tableau
        columns = ('ID', 'Username', 'Rôle')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # Configuration des colonnes
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'ID':
                self.tree.column(col, width=50)
            else:
                self.tree.column(col, width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Placement
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Sélection d'un utilisateur
        self.tree.bind('<<TreeviewSelect>>', self.on_user_select)
        
        # Charger les utilisateurs
        self.charger_utilisateurs()
    
    def charger_utilisateurs(self):
        # Nettoyer la liste
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Charger les utilisateurs
        utilisateurs = self.controller.get_all_users()
        for user in utilisateurs:
            self.tree.insert('', 'end', values=(
                user.id,
                user.username,
                user.role
            ))
    
    def on_user_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        
        # Récupérer les données de l'utilisateur sélectionné
        item = self.tree.item(selection[0])
        self.username_var.set(item['values'][1])
        self.role_var.set(item['values'][2])
        self.password_var.set("")  # Vider le mot de passe
    
    def ajouter_utilisateur(self):
        username = self.username_var.get()
        password = self.password_var.get()
        role = self.role_var.get()
        
        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        # Hash du mot de passe
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if self.controller.ajouter_utilisateur(username, hashed_password, role):
            messagebox.showinfo("Succès", "Utilisateur ajouté avec succès")
            self.charger_utilisateurs()
            self.clear_fields()
        else:
            messagebox.showerror("Erreur", "Impossible d'ajouter l'utilisateur")
    
    def clear_fields(self):
        self.username_var.set("")
        self.password_var.set("")
        self.role_var.set("utilisateur") 
    
    def modifier_utilisateur(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un utilisateur à modifier")
            return
        
        item = self.tree.item(selection[0])
        user_id = item['values'][0]
        username = self.username_var.get()
        password = self.password_var.get()
        role = self.role_var.get()
        
        if not username:
            messagebox.showerror("Erreur", "Le nom d'utilisateur ne peut pas être vide")
            return
        
        # Si un nouveau mot de passe est fourni, le hasher
        hashed_password = None
        if password:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if self.controller.modifier_utilisateur(user_id, username, hashed_password, role):
            messagebox.showinfo("Succès", "Utilisateur modifié avec succès")
            self.charger_utilisateurs()
            self.clear_fields()
        else:
            messagebox.showerror("Erreur", "Impossible de modifier l'utilisateur")
    
    def supprimer_utilisateur(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un utilisateur à supprimer")
            return
        
        item = self.tree.item(selection[0])
        user_id = item['values'][0]
        username = item['values'][1]
        
        if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer l'utilisateur {username} ?"):
            if self.controller.supprimer_utilisateur(user_id):
                messagebox.showinfo("Succès", "Utilisateur supprimé avec succès")
                self.charger_utilisateurs()
                self.clear_fields()
            else:
                messagebox.showerror("Erreur", "Impossible de supprimer l'utilisateur") 