import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models.document import Livre, Magazine, Journal, OuvrageMultimedia

class EditDocumentDialog(tk.Toplevel):
    def __init__(self, parent, controller, document, callback):
        super().__init__(parent)
        self.controller = controller
        self.document = document
        self.callback = callback
        
        self.title(f"Modifier le document - {document.titre}")
        self.geometry("500x600")
        self.resizable(False, False)
        
        self.setup_ui()
        self.load_document_data()
    
    def setup_ui(self):
        # Type de document
        type_frame = ttk.LabelFrame(self, text="Type de document", padding="10")
        type_frame.pack(fill='x', padx=10, pady=5)
        
        self.type_var = tk.StringVar()
        for doc_type in ["livre", "magazine", "journal", "multimedia"]:
            ttk.Radiobutton(type_frame, text=doc_type.capitalize(),
                          variable=self.type_var, value=doc_type,
                          command=self.update_fields).pack(side='left', padx=5)
        
        # Informations générales
        common_frame = ttk.LabelFrame(self, text="Informations générales", padding="10")
        common_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(common_frame, text="Titre:").grid(row=0, column=0, padx=5, pady=5)
        self.titre_var = tk.StringVar()
        ttk.Entry(common_frame, textvariable=self.titre_var, width=40).grid(row=0, column=1, padx=5)
        
        ttk.Label(common_frame, text="Date de publication:").grid(row=1, column=0, padx=5, pady=5)
        self.date_var = tk.StringVar()
        ttk.Entry(common_frame, textvariable=self.date_var).grid(row=1, column=1, padx=5)
        
        # Frame pour les champs spécifiques
        self.specific_frame = ttk.LabelFrame(self, text="Informations spécifiques", padding="10")
        self.specific_frame.pack(fill='x', padx=10, pady=5)
        
        # Boutons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', pady=10, padx=10)
        
        ttk.Button(button_frame, text="Enregistrer", command=self.save_changes).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Annuler", command=self.destroy).pack(side='right', padx=5)
    
    def update_fields(self):
        # Nettoyer les champs spécifiques
        for widget in self.specific_frame.winfo_children():
            widget.destroy()
        
        self.specific_vars = {}
        doc_type = self.type_var.get()
        
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
            ttk.Label(self.specific_frame, text=label).grid(row=i, column=0, sticky='e', padx=5, pady=5)
            
            if options:  # Si c'est un choix limité
                self.specific_vars[var_name] = tk.StringVar()
                ttk.Combobox(self.specific_frame, 
                            textvariable=self.specific_vars[var_name],
                            values=options[0]).grid(row=i, column=1, sticky='w', padx=5)
            else:
                self.specific_vars[var_name] = tk.StringVar()
                ttk.Entry(self.specific_frame,
                         textvariable=self.specific_vars[var_name]).grid(row=i, column=1, sticky='w', padx=5)
    
    def load_document_data(self):
        # Déterminer le type de document
        if isinstance(self.document, Livre):
            doc_type = "livre"
        elif isinstance(self.document, Magazine):
            doc_type = "magazine"
        elif isinstance(self.document, Journal):
            doc_type = "journal"
        else:
            doc_type = "multimedia"
        
        # Définir le type et mettre à jour les champs
        self.type_var.set(doc_type)
        self.update_fields()
        
        # Charger les informations générales
        self.titre_var.set(self.document.titre)
        self.date_var.set(self.document.date_publication.strftime('%Y-%m-%d'))
        
        # Charger les informations spécifiques
        details = self.document.get_details()
        
        if isinstance(self.document, Livre):
            self.specific_vars["auteur"].set(details.get("auteur", ""))
            self.specific_vars["nb_pages"].set(str(details.get("nb_pages", "")))
            self.specific_vars["genre"].set(details.get("genre", ""))
        elif isinstance(self.document, Magazine):
            self.specific_vars["editeur"].set(details.get("editeur", ""))
            self.specific_vars["frequence"].set(details.get("frequence", ""))
            self.specific_vars["numero"].set(details.get("numero", ""))
        elif isinstance(self.document, Journal):
            self.specific_vars["editeur"].set(details.get("editeur", ""))
        elif isinstance(self.document, OuvrageMultimedia):
            self.specific_vars["type_media"].set(details.get("type_media", ""))
            self.specific_vars["duree"].set(str(details.get("duree", "")))
    
    def save_changes(self):
        try:
            # Créer un nouveau document selon le type sélectionné
            doc_type = self.type_var.get()
            titre = self.titre_var.get()
            date_pub = datetime.strptime(self.date_var.get(), '%Y-%m-%d')
            
            if doc_type == "livre":
                new_doc = Livre(
                    titre=titre,
                    auteur=self.specific_vars["auteur"].get(),
                    nb_pages=int(self.specific_vars["nb_pages"].get()),
                    genre=self.specific_vars["genre"].get(),
                    date_publication=date_pub
                )
            elif doc_type == "magazine":
                new_doc = Magazine(
                    titre=titre,
                    editeur=self.specific_vars["editeur"].get(),
                    frequence=self.specific_vars["frequence"].get(),
                    numero=self.specific_vars["numero"].get(),
                    date_publication=date_pub
                )
            elif doc_type == "journal":
                new_doc = Journal(
                    titre=titre,
                    editeur=self.specific_vars["editeur"].get(),
                    date_publication=date_pub
                )
            else:  # multimedia
                new_doc = OuvrageMultimedia(
                    titre=titre,
                    type_media=self.specific_vars["type_media"].get(),
                    duree=int(self.specific_vars["duree"].get()),
                    date_publication=date_pub
                )
            
            # Conserver l'ID du document original
            new_doc._id = self.document.id
            
            # Sauvegarder les modifications
            if self.controller.modifier_document(new_doc.id, new_doc):
                messagebox.showinfo("Succès", "Document modifié avec succès")
                self.callback()
                self.destroy()
            else:
                messagebox.showerror("Erreur", "Impossible de modifier le document")
                
        except ValueError as e:
            messagebox.showerror("Erreur", f"Erreur de validation: {str(e)}") 