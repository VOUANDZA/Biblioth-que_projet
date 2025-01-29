def show_document_form(self, document=None):
    # Créer une nouvelle fenêtre
    self.form_window = tk.Toplevel(self)
    self.form_window.title("Modifier document" if document else "Ajouter un document")
    self.form_window.geometry("400x500")
    
    # Variables pour stocker les valeurs des champs
    self.type_var = tk.StringVar(value=document.__class__.__name__ if document else '')
    self.titre_var = tk.StringVar(value=document.titre if document else '')
    
    # Frame pour le type de document
    type_frame = ttk.LabelFrame(self.form_window, text="Type de document")
    type_frame.pack(fill='x', padx=5, pady=5)
    
    types = [('Livre', 'Livre'), ('Magazine', 'Magazine'), 
            ('Journal', 'Journal'), ('Multimédia', 'OuvrageMultimedia')]
    for text, value in types:
        ttk.Radiobutton(type_frame, text=text, value=value, 
                       variable=self.type_var).pack(side='left', padx=5)
    
    # Frame pour les champs communs
    common_frame = ttk.LabelFrame(self.form_window, text="Informations générales")
    common_frame.pack(fill='x', padx=5, pady=5)
    
    ttk.Label(common_frame, text="Titre:").pack(fill='x', padx=5, pady=2)
    ttk.Entry(common_frame, textvariable=self.titre_var).pack(fill='x', padx=5, pady=2)
    
    # Frame pour les champs spécifiques
    self.specific_frame = ttk.LabelFrame(self.form_window, text="Informations spécifiques")
    self.specific_frame.pack(fill='x', padx=5, pady=5)
    
    # Frame pour les boutons
    button_frame = ttk.Frame(self.form_window)
    button_frame.pack(fill='x', padx=5, pady=5)
    
    if document:
        # Mode modification
        ttk.Button(
            button_frame,
            text="Modifier",
            command=lambda: self.save_document(document._id)
        ).pack(side='left', padx=5)
    else:
        # Mode ajout
        ttk.Button(
            button_frame,
            text="Ajouter",
            command=self.save_document
        ).pack(side='left', padx=5)
    
    ttk.Button(
        button_frame,
        text="Annuler",
        command=self.form_window.destroy
    ).pack(side='left', padx=5)
    
    # Mettre à jour les champs spécifiques selon le type
    self.type_var.trace('w', self.update_specific_fields)
    if document:
        # Pré-remplir les champs spécifiques
        self.update_specific_fields()
        self.fill_specific_fields(document) 

def save_document(self, doc_id=None):
    try:
        # Récupérer les valeurs communes
        doc_type = self.type_var.get()
        titre = self.titre_var.get()
        
        if not doc_type or not titre:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
            return
        
        # Créer le document selon son type
        document = None
        if doc_type == 'Livre':
            document = Livre(
                id=doc_id,
                titre=titre,
                auteur=self.specific_vars['auteur'].get(),
                nb_pages=int(self.specific_vars['nb_pages'].get() or 0),
                genre=self.specific_vars['genre'].get(),
                date_publication=datetime.now()
            )
        elif doc_type == 'Magazine':
            document = Magazine(
                id=doc_id,
                titre=titre,
                editeur=self.specific_vars['editeur'].get(),
                frequence=self.specific_vars['frequence'].get(),
                numero=self.specific_vars['numero'].get(),
                date_publication=datetime.now()
            )
        elif doc_type == 'Journal':
            document = Journal(
                id=doc_id,
                titre=titre,
                editeur=self.specific_vars['editeur'].get(),
                date_publication=datetime.now()
            )
        elif doc_type == 'OuvrageMultimedia':
            document = OuvrageMultimedia(
                id=doc_id,
                titre=titre,
                type_media=self.specific_vars['type_media'].get(),
                duree=int(self.specific_vars['duree'].get() or 0),
                date_publication=datetime.now()
            )
        
        if doc_id:
            # Mode modification
            if self.controller.modifier_document(doc_id, document):
                messagebox.showinfo("Succès", "Document modifié avec succès")
                self.form_window.destroy()
                self.refresh_documents()
            else:
                messagebox.showerror("Erreur", "Impossible de modifier le document")
        else:
            # Mode ajout
            if self.controller.ajouter_document(document):
                messagebox.showinfo("Succès", "Document ajouté avec succès")
                self.form_window.destroy()
                self.refresh_documents()
            else:
                messagebox.showerror("Erreur", "Impossible d'ajouter le document")
                
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}") 