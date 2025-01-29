from abc import ABC, abstractmethod
from datetime import datetime

class Document(ABC):
    def __init__(self, titre, status="disponible"):
        self.titre = titre
        self.status = status
    
    @abstractmethod
    def get_description(self):
        pass
    
    @abstractmethod
    def calculer_frais_retard(self, jours_retard):
        pass

class Livre(Document):
    def __init__(self, titre, auteur, nb_pages, genre):
        super().__init__(titre)
        self.auteur = auteur
        self.nb_pages = nb_pages
        self.genre = genre
        
    def get_description(self):
        return f"Livre: {self.titre} par {self.auteur}, {self.nb_pages} pages, Genre: {self.genre}"
    
    def calculer_frais_retard(self, jours_retard):
        return jours_retard * 1.0  # TAUXA = 1.0

class Magazine(Document):
    def __init__(self, titre, editeur, frequence, numero):
        super().__init__(titre)
        self.editeur = editeur
        self.frequence = frequence
        self.numero = numero
    
    def get_description(self):
        return f"Magazine: {self.titre}, Éditeur: {self.editeur}, N°{self.numero}"
    
    def calculer_frais_retard(self, jours_retard):
        return (jours_retard * 1.0) + 2.0  # TAUXA = 1.0, TAUXB = 2.0

class Journal(Document):
    def __init__(self, titre, editeur, date_publication):
        super().__init__(titre)
        self.editeur = editeur
        self.date_publication = date_publication
    
    def get_description(self):
        return f"Journal: {self.titre}, Éditeur: {self.editeur}, Date: {self.date_publication}"
    
    def calculer_frais_retard(self, jours_retard):
        return jours_retard * 1.0  # TAUXA = 1.0

class MultiMedia(Document):
    def __init__(self, titre, type_media, duree):
        super().__init__(titre)
        self.type_media = type_media  # CD ou DVD
        self.duree = duree  # en minutes
    
    def get_description(self):
        return f"{self.type_media}: {self.titre}, Durée: {self.duree} min"
    
    def calculer_frais_retard(self, jours_retard):
        return (self.duree * 1.0) + (jours_retard * 2.0)  # TAUXA = 1.0, TAUXB = 2.0 