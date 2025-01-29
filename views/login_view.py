import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from PIL import Image, ImageTk

class LoginView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
        
    def setup_ui(self):
        # Style
        style = ttk.Style()
        style.configure('Login.TFrame', background='white')
        self.configure(style='Login.TFrame', padding="20")
        
        # Titre
        title_frame = ttk.Frame(self, style='Login.TFrame')
        title_frame.pack(fill='x', pady=20)
        
        ttk.Label(title_frame, 
                 text="Bibliothèque", 
                 font=('Helvetica', 24, 'bold'),
                 background='white').pack()
        
        # Image
        try:
            # Charger et redimensionner l'image avec le bon chemin
            image = Image.open("image/library3.jpg")  # Correction du chemin
            # Redimensionner l'image à une taille raisonnable (par exemple 300x200)
            image = image.resize((300, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Créer et placer le label pour l'image
            image_label = ttk.Label(title_frame, image=photo)
            image_label.image = photo  # Garder une référence!
            image_label.pack(pady=(0, 20))
        except Exception as e:
            print(f"Erreur lors du chargement de l'image: {e}")
        
        # Frame de connexion
        login_frame = ttk.LabelFrame(self, text="Connexion", padding="20")
        login_frame.pack(padx=20, pady=20)
        
        # Username
        ttk.Label(login_frame, text="Nom d'utilisateur:").grid(row=0, column=0, padx=5, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.username_var).grid(row=0, column=1, padx=5, pady=5)
        
        # Password
        ttk.Label(login_frame, text="Mot de passe:").grid(row=1, column=0, padx=5, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.password_var, show="*").grid(row=1, column=1, padx=5, pady=5)
        
        # Bouton de connexion
        ttk.Button(login_frame, 
                  text="Se connecter",
                  command=self.login).grid(row=2, column=0, columnspan=2, pady=20)
        
        # Ajouter un message d'aide
    
      #  help_text = "Compte admin par défaut:\nIdentifiant: admin\nMot de passe: admin123"
        #help_label = ttk.Label(
        #self,
           # text=help_text,
           # font=('Helvetica', 8),
          #  foreground='gray'
       # )
        #help_label.pack(pady=10)
    
    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        # Hash du mot de passe
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Tentative de connexion via le contrôleur
        if self.controller.login(username, hashed_password):
            self.username_var.set("")
            self.password_var.set("")
        else:
            messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect") 