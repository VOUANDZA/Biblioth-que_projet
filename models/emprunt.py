from datetime import datetime, timedelta
from utils.tarification import Tarification
from models.document import Livre, Magazine, Journal, OuvrageMultimedia

class Emprunt:
    def __init__(self, id, document, date_emprunt, date_retour=None, date_retour_prevue=None):
        self.id = id
        self.document = document
        self.date_emprunt = date_emprunt
        self.date_retour = date_retour
        # Si date_retour_prevue n'est pas fournie, on la calcule
        if date_retour_prevue is None:
            self.date_retour_prevue = self.date_emprunt + timedelta(days=Tarification.DUREE_EMPRUNT)
        else:
            self.date_retour_prevue = date_retour_prevue

    def est_en_retard(self):
        if not self.date_retour_prevue:
            return False
        if self.date_retour:
            return self.date_retour > self.date_retour_prevue
        return datetime.now() > self.date_retour_prevue

    def jours_retard(self):
        if not self.est_en_retard():
            return 0
        
        date_fin = self.date_retour if self.date_retour else datetime.now()
        return (date_fin - self.date_retour_prevue).days

    def calculer_penalites(self):
        if not self.est_en_retard():
            return 0.0
        
        jours = self.jours_retard()
        
        if isinstance(self.document, Livre):
            return Tarification.TAUX_A * jours
        elif isinstance(self.document, Magazine):
            return (Tarification.TAUX_A * jours) + Tarification.TAUX_B
        elif isinstance(self.document, Journal):
            return Tarification.TAUX_A * jours
        elif isinstance(self.document, OuvrageMultimedia):
            return (Tarification.TAUX_A * self.document.duree) + (Tarification.TAUX_B * jours)
        return 0.0

    def get_status(self):
        if self.date_retour:
            return "Retourné"
        elif self.est_en_retard():
            return "En retard"
        else:
            return "En cours"

    def __str__(self):
        status = self.get_status()
        return f"Emprunt {self.id} - {self.document.titre} ({status})" 