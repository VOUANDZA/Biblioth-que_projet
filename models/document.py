from abc import ABC, abstractmethod
from datetime import datetime

class Document(ABC):
    def __init__(self, id=None, titre="", date_publication=None, status="disponible"):
        self._id = id
        self._titre = titre
        # Convertir la date_publication en datetime si c'est une chaîne
        if isinstance(date_publication, str):
            try:
                self._date_publication = datetime.strptime(date_publication, '%Y-%m-%d')
            except (ValueError, TypeError):
                self._date_publication = datetime.now()
        else:
            self._date_publication = date_publication or datetime.now()
        self._status = status
    
    @property
    def id(self): return self._id
    @property
    def titre(self): return self._titre
    @property
    def status(self): return self._status
    @property
    def date_publication(self): return self._date_publication
    
    @abstractmethod
    def calculer_frais_retard(self, jours_retard):
        pass
    
    def get_details(self):
        # Implémentation de base pour tous les documents
        return {
            'id': self._id,
            'titre': self._titre,
            'date_publication': self._date_publication.strftime('%Y-%m-%d'),
            'status': self._status
        }

class Livre(Document):
    def __init__(self, id=None, titre="", auteur="", nb_pages=0, genre="", 
                 date_publication=None, status="disponible"):
        super().__init__(id, titre, date_publication, status)
        self._auteur = auteur
        self._nb_pages = nb_pages
        self._genre = genre
    
    def calculer_frais_retard(self, jours_retard):
        return 0.50 * jours_retard  # 50 centimes par jour
    
    def get_details(self):
        details = super().get_details()
        details.update({
            'auteur': self._auteur,
            'nb_pages': self._nb_pages,
            'genre': self._genre
        })
        return details

class Magazine(Document):
    def __init__(self, id=None, titre="", editeur="", frequence="", numero="",
                 date_publication=None, status="disponible"):
        super().__init__(id, titre, date_publication, status)
        self._editeur = editeur
        self._frequence = frequence  # hebdomadaire, mensuel, etc.
        self._numero = numero
    
    def calculer_frais_retard(self, jours_retard):
        return (0.30 * jours_retard) + 1.0  # 30 centimes par jour + 1€ fixe
    
    def get_details(self):
        details = super().get_details()
        details.update({
            'editeur': self._editeur,
            'frequence': self._frequence,
            'numero': self._numero
        })
        return details

class Journal(Document):
    def __init__(self, id=None, titre="", editeur="", date_publication=None, status="disponible"):
        super().__init__(id, titre, date_publication, status)
        self._editeur = editeur
    
    def calculer_frais_retard(self, jours_retard):
        return 0.70 * jours_retard  # 70 centimes par jour
    
    def get_details(self):
        details = super().get_details()
        details.update({
            'editeur': self._editeur
        })
        return details

class OuvrageMultimedia(Document):
    def __init__(self, id=None, titre="", type_media="", duree=0, 
                 date_publication=None, status="disponible"):
        super().__init__(id, titre, date_publication, status)
        self._type_media = type_media  # CD ou DVD
        self._duree = duree  # en minutes
    
    def calculer_frais_retard(self, jours_retard):
        # 1€ par jour + supplément selon le type
        supplement = 2.0 if self._type_media.upper() == "DVD" else 1.0
        return (1.0 * jours_retard) + supplement
    
    def get_details(self):
        details = super().get_details()
        details.update({
            'type_media': self._type_media,
            'duree': self._duree
        })
        return details 