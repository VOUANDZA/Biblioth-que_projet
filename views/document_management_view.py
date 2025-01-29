import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models.document import Livre, Magazine, Journal, OuvrageMultimedia

class AddDocumentDialog(tk.Toplevel):
    def __init__(self, parent, controller, callback, document_to_edit=None):
        super().__init__(parent)
        self.controller = controller
        self.callback = callback
        self.document_to_edit = document_to_edit  # Stocker le document à modifier
        self.mode = 'modification' if document_to_edit else 'ajout'
        self.title("Modifier le document" if self.mode == 'modification' else "Ajouter un document")
        self.setup_ui()
        
        # Pré-remplir les champs si on est en mode modification
        if self.document_to_edit:
            self.pre_remplir_champs()
    
    def setup_ui(self):
        # Type de document
        type_frame = ttk.LabelFrame(self, text="Type de document", padding="10")
        type_frame.pack(fill='x', padx=10, pady=5)
        
        self.type_var = tk.StringVar(value="livre")
        for doc_type in ["livre", "magazine", "journal", "multimedia"]:
            ttk.Radiobutton(type_frame, text=doc_type.capitalize(),
                          variable=self.type_var, value=doc_type,
                          command=self.update_fields).pack(side='left', padx=5)
        
        # Champs communs
        common_frame = ttk.LabelFrame(self, text="Informations générales", padding="10")
        common_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(common_frame, text="Titre:").grid(row=0, column=0, padx=5, pady=5)
        self.titre_var = tk.StringVar()
        ttk.Entry(common_frame, textvariable=self.titre_var).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(common_frame, text="Date de publication:").grid(row=1, column=0, padx=5, pady=5)
        self.date_pub_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(common_frame, textvariable=self.date_pub_var).grid(row=1, column=1, padx=5, pady=5)
        
        # Frame pour les champs spécifiques
        self.specific_frame = ttk.LabelFrame(self, text="Informations spécifiques", padding="10")
        self.specific_frame.pack(fill='x', padx=10, pady=5)
        
        # Boutons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        # Modifier le texte du bouton selon le mode
        action_text = "Modifier" if hasattr(self, 'mode') and self.mode == 'modification' else "Ajouter"
        ttk.Button(button_frame, text=action_text,
                  command=self.ajouter_document).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Annuler",
                  command=self.destroy).pack(side='left', padx=5)
        
        self.update_fields()
    
    def update_fields(self):
        # Nettoyer les champs spécifiques
        for widget in self.specific_frame.winfo_children():
            widget.destroy()
        
        doc_type = self.type_var.get()
        self.specific_vars = {}
        
        if doc_type == "livre":
            fields = [
                ("Auteur:", "auteur"),
                ("Nombre de pages:", "nb_pages"),
                ("Genre:", "genre")
            ]
        elif doc_type == "magazine":
            fields = [
                ("Éditeur:", "editeur"),
                ("Fréquence:", "frequence", ["Hebdomadaire", "Mensuel", "Trimestriel"]),
                ("Numéro:", "numero")
            ]
        elif doc_type == "journal":
            fields = [
                ("Éditeur:", "editeur")
            ]
        else:  # multimedia
            fields = [
                ("Type média:", "type_media", ["CD", "DVD"]),
                ("Durée (minutes):", "duree")
            ]
        
        for i, field in enumerate(fields):
            label, var_name, *options = field
            ttk.Label(self.specific_frame, text=label).grid(row=i, column=0, padx=5, pady=5)
            
            if options:  # Si c'est un choix limité
                self.specific_vars[var_name] = tk.StringVar(value=options[0][0])
                ttk.Combobox(self.specific_frame, 
                            textvariable=self.specific_vars[var_name],
                            values=options[0]).grid(row=i, column=1, padx=5, pady=5)
            else:
                self.specific_vars[var_name] = tk.StringVar()
                ttk.Entry(self.specific_frame,
                         textvariable=self.specific_vars[var_name]).grid(row=i, column=1, padx=5, pady=5)
    
    def pre_remplir_champs(self):
        doc = self.document_to_edit
        self.type_var.set(doc.__class__.__name__.lower())
        self.titre_var.set(doc.titre)
        self.date_pub_var.set(doc.date_publication.strftime('%Y-%m-%d'))
        
        # Mettre à jour les champs spécifiques
        self.update_fields()
        details = doc.get_details()
        
        if isinstance(doc, Livre):
            self.specific_vars["auteur"].set(details.get("auteur", ""))
            self.specific_vars["nb_pages"].set(str(details.get("nb_pages", "")))
            self.specific_vars["genre"].set(details.get("genre", ""))
        elif isinstance(doc, Magazine):
            self.specific_vars["editeur"].set(details.get("editeur", ""))
            self.specific_vars["frequence"].set(details.get("frequence", ""))
            self.specific_vars["numero"].set(details.get("numero", ""))
        elif isinstance(doc, Journal):
            self.specific_vars["editeur"].set(details.get("editeur", ""))
        elif isinstance(doc, OuvrageMultimedia):
            self.specific_vars["type_media"].set(details.get("type_media", ""))
            self.specific_vars["duree"].set(str(details.get("duree", "")))
    
    def ajouter_document(self):
        titre = self.titre_var.get()
        if not titre:
            messagebox.showerror("Erreur", "Le titre est obligatoire")
            return
        
        document = self.creer_document()
        if document:
            if self.mode == 'modification':
                # Assigner l'ID du document existant
                document._id = self.document_to_edit.id
                if self.controller.modifier_document(document._id, document):
                    messagebox.showinfo("Succès", "Document modifié avec succès")
                    self.callback()
                    self.destroy()
                else:
                    messagebox.showerror("Erreur", "Impossible de modifier le document")
            else:
                if self.controller.ajouter_document(document):
                    messagebox.showinfo("Succès", "Document ajouté avec succès")
                    self.callback()
                    self.destroy()
                else:
                    messagebox.showerror("Erreur", "Impossible d'ajouter le document")
    
    def creer_document(self):
        try:
            titre = self.titre_var.get()
            date_pub = datetime.strptime(self.date_pub_var.get(), '%Y-%m-%d')
            doc_type = self.type_var.get()
            
            if doc_type == "livre":
                return Livre(
                    titre=titre,
                    auteur=self.specific_vars["auteur"].get(),
                    nb_pages=int(self.specific_vars["nb_pages"].get()),
                    genre=self.specific_vars["genre"].get(),
                    date_publication=date_pub
                )
            elif doc_type == "magazine":
                return Magazine(
                    titre=titre,
                    editeur=self.specific_vars["editeur"].get(),
                    frequence=self.specific_vars["frequence"].get(),
                    numero=self.specific_vars["numero"].get(),
                    date_publication=date_pub
                )
            elif doc_type == "journal":
                return Journal(
                    titre=titre,
                    editeur=self.specific_vars["editeur"].get(),
                    date_publication=date_pub
                )
            else:  # multimedia
                return OuvrageMultimedia(
                    titre=titre,
                    type_media=self.specific_vars["type_media"].get(),
                    duree=int(self.specific_vars["duree"].get()),
                    date_publication=date_pub
                )
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
            return None 