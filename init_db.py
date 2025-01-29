import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
import hashlib
from datetime import datetime, timedelta
from models.document import Livre, Magazine, Journal, OuvrageMultimedia

def initialiser_bibliotheque():
    db = DatabaseManager()
    
    # Créer un administrateur
    admin_password = hashlib.sha256("admin123".encode()).hexdigest()
    db.ajouter_utilisateur("admin", admin_password, "administrateur")
    
    # Créer un utilisateur test
    user_password = hashlib.sha256("user123".encode()).hexdigest()
    db.ajouter_utilisateur("user", user_password, "utilisateur")
    
    # Ajouter des livres
    livres = [
        Livre(titre="1984", auteur="George Orwell", nb_pages=328, genre="Science-fiction"),
        Livre(titre="Le Petit Prince", auteur="Saint-Exupéry", nb_pages=96, genre="Conte"),
        Livre(titre="Harry Potter", auteur="J.K. Rowling", nb_pages=320, genre="Fantasy")
    ]
    
    # Ajouter des magazines
    magazines = [
        Magazine(titre="Science & Vie", editeur="Mondadori", frequence="Mensuel", numero="1234"),
        Magazine(titre="National Geographic", editeur="NG Society", frequence="Mensuel", numero="456")
    ]
    
    # Ajouter des journaux
    journaux = [
        Journal(titre="Le Monde", editeur="Groupe Le Monde", date_publication=datetime.now()),
        Journal(titre="Le Figaro", editeur="Groupe Figaro", date_publication=datetime.now() - timedelta(days=1))
    ]
    
    # Ajouter des documents multimédia
    multimedia = [
        OuvrageMultimedia(titre="Inception", type_media="DVD", duree=148),
        OuvrageMultimedia(titre="The Dark Side of the Moon", type_media="CD", duree=43)
    ]
    
    # Ajouter tous les documents à la base
    for doc in livres + magazines + journaux + multimedia:
        db.ajouter_document(doc)
    
    print("Base de données initialisée avec succès!")
    print("\nComptes de test:")
    print("Admin - username: admin, password: admin123")
    print("User  - username: user,  password: user123")

if __name__ == "__main__":
    initialiser_bibliotheque()