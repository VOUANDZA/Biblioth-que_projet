from database.db_manager import DatabaseManager
from models.utilisateur import Utilisateur
from utils.session_manager import SessionManager
from utils.logger import LibraryLogger
from utils.config_manager import ConfigManager
from utils.theme_manager import ThemeManager
from utils.error_handler import ErrorHandler
from datetime import timedelta

class MainController:
    def __init__(self):
        self.db = DatabaseManager()
        self.current_user = None
        self.session_manager = SessionManager()
        self.logger = LibraryLogger()
        self.main_window = None
        self.config = ConfigManager()
        self.theme_manager = ThemeManager()
        self.error_handler = ErrorHandler(self.logger)
    
    def set_main_window(self, window):
        self.main_window = window
    
    def login(self, username, password):
        try:
            user = self.db.get_utilisateur(username, password)
            if user:
                self.current_user = user
                # Créer une session et stocker l'ID
                session_id = self.session_manager.create_session(
                    user.id, user.username, user.role
                )
                self.current_user.session_id = session_id  # Stocker l'ID de session
                self.logger.log_action(
                    'login_success',
                    user.id,
                    {'username': username}
                )
                self.main_window.show_dashboard()
                return True
            
            self.logger.log_action(
                'login_failed',
                None,
                {'username': username, 'reason': 'Invalid credentials'}
            )
            return False
            
        except Exception as e:
            self.logger.log_error(
                'login_error',
                None,
                {'username': username, 'error': str(e)}
            )
            return False
    
    def logout(self):
        if self.current_user:
            self.logger.log_action(
                'logout',
                self.current_user.id,
                {'username': self.current_user.username}
            )
            self.session_manager.destroy_session(self.current_user.session_id)
            self.current_user = None
            self.main_window.show_login()
    
    def get_all_documents(self):
        return self.db.get_all_documents()
    
    def get_user_emprunts(self):
        if not self.current_user:
            return []
        return self.db.get_emprunts_utilisateur(self.current_user.id)
    
    def emprunter_document(self, doc_id):
        try:
            if not self.current_user:
                return False
            return self.db.creer_emprunt(self.current_user.id, doc_id)
        except Exception as e:
            print(f"Erreur d'emprunt: {str(e)}")
            return False
    
    def retourner_document(self, doc_id):
        try:
            success = self.db.retourner_document(doc_id)
            if success:
                self.logger.log_action(
                    'document_retourne',
                    self.current_user.id,
                    {'document_id': doc_id}
                )
                return True
            return False
        except Exception as e:
            self.logger.log_error(
                'retour_document_error',
                self.current_user.id,
                {'document_id': doc_id, 'error': str(e)}
            )
            return False
    
    def ajouter_document(self, document):
        if not self.current_user or not self.current_user.is_admin():
            return False
        return self.db.ajouter_document(document)
    
    def supprimer_document(self, doc_id):
        if not self.current_user or not self.current_user.is_admin():
            return False
        return self.db.supprimer_document(doc_id)
    
    def ajouter_utilisateur(self, username, password, role="utilisateur"):
        if not self.current_user or not self.current_user.is_admin():
            return False
        return self.db.ajouter_utilisateur(username, password, role)
    
    def get_all_users(self):
        return self.db.get_all_users()
    
    def modifier_utilisateur(self, user_id, username, password=None, role=None):
        if not self.current_user or not self.current_user.is_admin():
            return False
        return self.db.modifier_utilisateur(user_id, username, password, role)
    
    def supprimer_utilisateur(self, user_id):
        if not self.current_user or not self.current_user.is_admin():
            return False
        return self.db.supprimer_utilisateur(user_id)
    
    def modifier_document(self, doc_id, document):
        if not self.current_user or not self.current_user.is_admin():
            return False
        return self.db.modifier_document(doc_id, document)
    
    def demander_emprunt(self, doc_id):
        if not self.current_user:
            return False, "Vous devez être connecté"
        return self.db.creer_demande_emprunt(self.current_user.id, doc_id)
    
    def get_demandes_emprunt(self):
        if not self.current_user or not self.current_user.is_admin():
            return []
        return self.db.get_demandes_emprunt()
    
    def traiter_demande_emprunt(self, demande_id, decision, commentaire=""):
        if not self.current_user or not self.current_user.is_admin():
            return False, "Accès non autorisé"
        return self.db.traiter_demande_emprunt(demande_id, decision, commentaire)
    
    def initialize_app(self, root):
        # Appliquer le thème initial
        theme = self.config.get('theme', 'light')
        self.theme_manager.apply_theme(root, theme)
        
        # Configurer la session
        self.session_manager.session_duration = timedelta(
            seconds=self.config.get('session_duration', 7200)
        ) 
    
    def search_documents(self, criteria):
        return self.db.search_documents(criteria) 
    
    def get_mes_demandes(self):
        if not self.current_user:
            return []
        return self.db.get_demandes_utilisateur(self.current_user.id)
    
    def annuler_demande_emprunt(self, demande_id):
        try:
            success = self.db.annuler_demande_emprunt(demande_id)
            if success:
                self.logger.log_action(
                    'demande_annulee',
                    self.current_user.id,
                    {'demande_id': demande_id}
                )
            return success
        except Exception as e:
            self.logger.log_error(
                'demande_annulation_error',
                self.current_user.id,
                {'demande_id': demande_id, 'error': str(e)}
            )
            return False
    
    def relancer_demande_emprunt(self, demande_id):
        try:
            success = self.db.relancer_demande_emprunt(demande_id)
            if success:
                self.logger.log_action(
                    'demande_relancee',
                    self.current_user.id,
                    {'demande_id': demande_id}
                )
            return success
        except Exception as e:
            self.logger.log_error(
                'demande_relance_error',
                self.current_user.id,
                {'demande_id': demande_id, 'error': str(e)}
            )
            return False
    
    def get_document(self, doc_id):
        """Récupère un document par son ID"""
        try:
            document = self.db.get_document(doc_id)
            if document:
                self.logger.log_action(
                    'get_document',
                    self.current_user.id if self.current_user else None,
                    {'document_id': doc_id}
                )
                return document
            else:
                self.logger.log_error(
                    'get_document_not_found',
                    self.current_user.id if self.current_user else None,
                    {'document_id': doc_id}
                )
                return None
        except Exception as e:
            self.logger.log_error(
                'get_document_error',
                self.current_user.id if self.current_user else None,
                {'document_id': doc_id, 'error': str(e)}
            )
            return None 