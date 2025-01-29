import sqlite3
from datetime import datetime, timedelta
import json
from models.document import Livre, Magazine, Journal, OuvrageMultimedia
from models.utilisateur import Utilisateur
from models.emprunt import Emprunt
import hashlib
from utils.tarification import Tarification

class DatabaseManager:
    def __init__(self, db_file="bibliotheque.db"):
        self.db_file = db_file
        self.create_tables()
        self.update_database_schema()
    
    def create_tables(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            # Table Utilisateurs
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS utilisateurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'utilisateur'
            )''')
            
            # Vérifier si un admin existe déjà
            cursor.execute('SELECT COUNT(*) FROM utilisateurs WHERE role = "administrateur"')
            if cursor.fetchone()[0] == 0:
                # Créer un admin par défaut (mot de passe: admin123)
                admin_password = hashlib.sha256("admin123".encode()).hexdigest()
                print(f"Création compte admin - Password hash: {admin_password}")  # Pour débogage
                cursor.execute('''
                    INSERT INTO utilisateurs (username, password, role)
                    VALUES (?, ?, ?)
                ''', ('admin', admin_password, 'administrateur'))
                conn.commit()
                print("Compte admin créé avec succès")
            
            # Table Documents avec quantité
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                titre TEXT NOT NULL,
                status TEXT DEFAULT 'disponible',
                quantite INTEGER DEFAULT 1,
                quantite_disponible INTEGER DEFAULT 1,
                details TEXT NOT NULL
            )''')
            
            # Table pour les demandes d'emprunt
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS demandes_emprunt (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utilisateur_id INTEGER,
                document_id INTEGER,
                date_demande TEXT NOT NULL,
                status TEXT DEFAULT 'en_attente',  -- en_attente, validee, refusee
                commentaire TEXT,
                FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs (id),
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )''')
            
            # Table Emprunts
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS emprunts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                utilisateur_id INTEGER,
                document_id INTEGER,
                date_emprunt TEXT NOT NULL,
                date_retour TEXT,
                date_retour_prevue TEXT,
                FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs (id),
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )''')
            
            conn.commit()
        except Exception as e:
            print(f"Erreur lors de la création des tables: {str(e)}")
            conn.rollback()
        finally:
            conn.close() 

    def update_database_schema(self):
        """Met à jour le schéma de la base de données si nécessaire"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            # Vérifier si la colonne date_retour_prevue existe
            cursor.execute('''
                SELECT COUNT(*) FROM pragma_table_info('emprunts') 
                WHERE name='date_retour_prevue'
            ''')
            
            if cursor.fetchone()[0] == 0:
                # Ajouter la colonne date_retour_prevue
                cursor.execute('''
                    ALTER TABLE emprunts 
                    ADD COLUMN date_retour_prevue TEXT
                ''')
                
                # Mettre à jour les emprunts existants avec une date de retour prévue
                cursor.execute('''
                    UPDATE emprunts 
                    SET date_retour_prevue = date(date_emprunt, '+30 days')
                    WHERE date_retour_prevue IS NULL
                ''')
                
                conn.commit()
                print("Schéma de la base de données mis à jour avec succès")
        
        except Exception as e:
            print(f"Erreur lors de la mise à jour du schéma: {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    def ajouter_utilisateur(self, username, password, role="utilisateur"):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO utilisateurs (username, password, role) VALUES (?, ?, ?)',
                (username, password, role)
            )
            conn.commit()
            return Utilisateur(cursor.lastrowid, username, password, role)
        finally:
            conn.close()

    def get_utilisateur(self, username, password):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            # Ajout de logs pour le débogage
            print(f"Tentative de connexion - Username: {username}")
            cursor.execute(
                'SELECT id, username, password, role FROM utilisateurs WHERE username = ?',
                (username,)
            )
            result = cursor.fetchone()
            if result:
                stored_id, stored_username, stored_password, stored_role = result
                print(f"Utilisateur trouvé - Role: {stored_role}")
                print(f"Password match: {stored_password == password}")
                if stored_password == password:
                    return Utilisateur(stored_id, stored_username, stored_password, stored_role)
            return None
        finally:
            conn.close()

    def ajouter_document(self, document):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            # Vérifier si un document avec le même titre existe déjà
            cursor.execute('''
                SELECT id FROM documents 
                WHERE LOWER(titre) = LOWER(?) AND type = ?
            ''', (document.titre, document.__class__.__name__.lower()))
            
            if cursor.fetchone():
                print(f"Un document avec le titre '{document.titre}' existe déjà")
                return None
            
            # Déterminer le type de document et normaliser le type pour les multimédias
            type_doc = document.__class__.__name__.lower()
            if type_doc == 'ouvrageMultimedia'.lower():
                type_doc = 'multimedia'  # Normaliser le type pour la base de données
            
            # Préparer les détails selon le type de document
            details = {}
            if type_doc == 'livre':
                details = {
                    'auteur': document._auteur,
                    'nb_pages': document._nb_pages,
                    'genre': document._genre,
                    'date_publication': document._date_publication.strftime('%Y-%m-%d')
                }
            elif type_doc == 'magazine':
                details = {
                    'editeur': document._editeur,
                    'frequence': document._frequence,
                    'numero': document._numero,
                    'date_publication': document._date_publication.strftime('%Y-%m-%d')
                }
            elif type_doc == 'journal':
                details = {
                    'editeur': document._editeur,
                    'date_publication': document._date_publication.strftime('%Y-%m-%d')
                }
            elif type_doc == 'multimedia':  # Utiliser le type normalisé
                details = {
                    'type_media': document._type_media,
                    'duree': document._duree,
                    'date_publication': document._date_publication.strftime('%Y-%m-%d')
                }
            
            # Insérer le document
            cursor.execute('''
                INSERT INTO documents (type, titre, status, details, quantite, quantite_disponible)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                type_doc,
                document.titre,
                document.status,
                json.dumps(details),
                1,  # quantité par défaut
                1   # quantité disponible par défaut
            ))
            
            conn.commit()
            document._id = cursor.lastrowid
            return document
            
        except Exception as e:
            print(f"Erreur lors de l'ajout du document: {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_document(self, doc_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT type, titre, status, details 
                FROM documents 
                WHERE id = ?
            ''', (doc_id,))
            
            result = cursor.fetchone()
            if not result:
                print(f"Document introuvable avec l'ID {doc_id}")
                return None
            
            type_doc, titre, status, details = result
            details = json.loads(details)
            
            # Convertir la date_publication
            try:
                date_publication = datetime.strptime(
                    details.get('date_publication', datetime.now().strftime('%Y-%m-%d')),
                    '%Y-%m-%d'
                )
            except (ValueError, TypeError):
                date_publication = datetime.now()
            
            print(f"Type de document trouvé: {type_doc}")  # Debug
            
            if type_doc == 'livre':
                return Livre(
                    doc_id, titre,
                    details.get('auteur', ''),
                    int(details.get('nb_pages', 0)),
                    details.get('genre', ''),
                    date_publication,
                    status
                )
            elif type_doc == 'magazine':
                return Magazine(
                    doc_id, titre,
                    details.get('editeur', ''),
                    details.get('frequence', ''),
                    details.get('numero', ''),
                    date_publication,
                    status
                )
            elif type_doc == 'journal':
                return Journal(
                    doc_id, titre,
                    details.get('editeur', ''),
                    date_publication,
                    status
                )
            elif type_doc == 'multimedia':  # Changé de 'ouvrageMultimedia' à 'multimedia'
                return OuvrageMultimedia(
                    doc_id, titre,
                    details.get('type_media', ''),
                    int(details.get('duree', 0)),
                    date_publication,
                    status
                )
            else:
                print(f"Type de document non reconnu: {type_doc}")
                return None
        except Exception as e:
            print(f"Erreur lors de la récupération du document: {str(e)}")
            return None
        finally:
            conn.close()

    def creer_emprunt(self, utilisateur_id, doc_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            # Vérifier la disponibilité
            cursor.execute('''
                SELECT quantite_disponible FROM documents WHERE id = ?
            ''', (doc_id,))
            if cursor.fetchone()[0] <= 0:
                return False
            
            # Créer l'emprunt
            date_emprunt = datetime.now().strftime('%Y-%m-%d')
            date_retour_prevue = (datetime.now() + timedelta(days=Tarification.DUREE_EMPRUNT)).strftime('%Y-%m-%d')
            
            cursor.execute('''
                INSERT INTO emprunts (utilisateur_id, document_id, date_emprunt, date_retour_prevue)
                VALUES (?, ?, ?, ?)
            ''', (utilisateur_id, doc_id, date_emprunt, date_retour_prevue))
            
            # Mettre à jour la quantité disponible
            cursor.execute('''
                UPDATE documents 
                SET quantite_disponible = quantite_disponible - 1
                WHERE id = ?
            ''', (doc_id,))
            
            conn.commit()
            return True
        finally:
            conn.close()

    def get_emprunts_utilisateur(self, user_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT e.id, e.document_id, e.date_emprunt, e.date_retour, e.date_retour_prevue,
                       d.type, d.titre, d.details, d.status
                FROM emprunts e
                JOIN documents d ON e.document_id = d.id
                WHERE e.utilisateur_id = ?
                ORDER BY e.date_emprunt DESC
            ''', (user_id,))
            
            emprunts = []
            for row in cursor.fetchall():
                emprunt_id, doc_id, date_emprunt, date_retour, date_retour_prevue, doc_type, titre, details_json, status = row
                details = json.loads(details_json)
                
                # Créer le document selon son type
                if doc_type.lower() == 'livre':
                    document = Livre(
                        id=doc_id,
                        titre=titre,
                        auteur=details.get('auteur', ''),
                        nb_pages=details.get('nb_pages', 0),
                        genre=details.get('genre', ''),
                        date_publication=datetime.strptime(details.get('date_publication', '2000-01-01'), '%Y-%m-%d'),
                        status=status
                    )
                elif doc_type.lower() == 'magazine':
                    document = Magazine(
                        id=doc_id,
                        titre=titre,
                        editeur=details.get('editeur', ''),
                        frequence=details.get('frequence', ''),
                        numero=details.get('numero', ''),
                        date_publication=datetime.strptime(details.get('date_publication', '2000-01-01'), '%Y-%m-%d'),
                        status=status
                    )
                elif doc_type.lower() == 'journal':
                    document = Journal(
                        id=doc_id,
                        titre=titre,
                        editeur=details.get('editeur', ''),
                        date_publication=datetime.strptime(details.get('date_publication', '2000-01-01'), '%Y-%m-%d'),
                        status=status
                    )
                else:  # multimedia
                    document = OuvrageMultimedia(
                        id=doc_id,
                        titre=titre,
                        type_media=details.get('type_media', ''),
                        duree=details.get('duree', 0),
                        date_publication=datetime.strptime(details.get('date_publication', '2000-01-01'), '%Y-%m-%d'),
                        status=status
                    )
                
                # Créer l'emprunt avec toutes les dates
                emprunt = Emprunt(
                    id=emprunt_id,
                    document=document,
                    date_emprunt=datetime.strptime(date_emprunt, '%Y-%m-%d'),
                    date_retour=datetime.strptime(date_retour, '%Y-%m-%d') if date_retour else None,
                    date_retour_prevue=datetime.strptime(date_retour_prevue, '%Y-%m-%d') if date_retour_prevue else None
                )
                emprunts.append(emprunt)
            
            return emprunts
        
        finally:
            conn.close()

    def get_all_documents(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT DISTINCT d.id, d.type, d.titre, d.status, d.details, 
                       d.quantite, d.quantite_disponible 
                FROM documents d
                GROUP BY d.id  -- Grouper par ID pour éviter les doublons
            ''')
            documents = []
            seen_ids = set()  # Pour suivre les IDs déjà traités
            
            for row in cursor.fetchall():
                doc_id, type_doc, titre, status, details, quantite, quantite_disponible = row
                
                # Éviter les doublons
                if doc_id in seen_ids:
                    continue
                seen_ids.add(doc_id)
                
                details = json.loads(details)
                status = 'disponible' if quantite_disponible > 0 else 'indisponible'
                
                try:
                    date_publication = datetime.strptime(
                        details.get('date_publication', datetime.now().strftime('%Y-%m-%d')),
                        '%Y-%m-%d'
                    )
                except (ValueError, TypeError):
                    date_publication = datetime.now()
                
                doc = None
                if type_doc == 'livre':
                    doc = Livre(
                        doc_id, titre,
                        details.get('auteur', ''),
                        int(details.get('nb_pages', 0)),
                        details.get('genre', ''),
                        date_publication,
                        status
                    )
                elif type_doc == 'magazine':
                    doc = Magazine(
                        doc_id, titre,
                        details.get('editeur', ''),
                        details.get('frequence', ''),
                        details.get('numero', ''),
                        date_publication,
                        status
                    )
                elif type_doc == 'journal':
                    doc = Journal(
                        doc_id, titre,
                        details.get('editeur', ''),
                        date_publication,
                        status
                    )
                elif type_doc == 'multimedia':  # Type normalisé
                    doc = OuvrageMultimedia(
                        doc_id, titre,
                        details.get('type_media', ''),
                        int(details.get('duree', 0)),
                        date_publication,
                        status
                    )
                
                if doc:  # Ajouter seulement si un document valide a été créé
                    documents.append(doc)
                
            return documents
        finally:
            conn.close()

    def get_utilisateur_by_id(self, user_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'SELECT id, username, password, role FROM utilisateurs WHERE id = ?',
                (user_id,)
            )
            result = cursor.fetchone()
            if result:
                return Utilisateur(*result)
            return None
        finally:
            conn.close()

    def supprimer_document(self, doc_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close() 

    def get_all_users(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT id, username, password, role FROM utilisateurs')
            return [Utilisateur(*row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def modifier_utilisateur(self, user_id, username, password=None, role=None):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            # Vérifier si le username existe déjà pour un autre utilisateur
            cursor.execute('SELECT id FROM utilisateurs WHERE username = ? AND id != ?', 
                          (username, user_id))
            if cursor.fetchone():
                return False
            
            if password and role:
                cursor.execute('''
                    UPDATE utilisateurs 
                    SET username = ?, password = ?, role = ?
                    WHERE id = ?
                ''', (username, password, role, user_id))
            elif password:
                cursor.execute('''
                    UPDATE utilisateurs 
                    SET username = ?, password = ?
                    WHERE id = ?
                ''', (username, password, user_id))
            elif role:
                cursor.execute('''
                    UPDATE utilisateurs 
                    SET username = ?, role = ?
                    WHERE id = ?
                ''', (username, role, user_id))
            else:
                cursor.execute('''
                    UPDATE utilisateurs 
                    SET username = ?
                    WHERE id = ?
                ''', (username, user_id))
            
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()

    def supprimer_utilisateur(self, user_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            # Vérifier s'il y a des emprunts en cours
            cursor.execute('''
                SELECT COUNT(*) FROM emprunts 
                WHERE utilisateur_id = ? AND date_retour IS NULL
            ''', (user_id,))
            if cursor.fetchone()[0] > 0:
                return False
            
            cursor.execute('DELETE FROM utilisateurs WHERE id = ?', (user_id,))
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()

    def retourner_document(self, doc_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            # Vérifier si le document est emprunté
            cursor.execute('''
                SELECT e.id 
                FROM emprunts e
                WHERE e.document_id = ? AND e.date_retour IS NULL
            ''', (doc_id,))
            emprunt = cursor.fetchone()
            if not emprunt:
                print("Aucun emprunt trouvé pour ce document")
                return False
            
            # Mettre à jour la date de retour
            date_retour = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                UPDATE emprunts 
                SET date_retour = ? 
                WHERE document_id = ? AND date_retour IS NULL
            ''', (date_retour, doc_id))
            
            # Mettre à jour le statut et la quantité disponible du document
            cursor.execute('''
                UPDATE documents 
                SET status = 'disponible',
                    quantite_disponible = quantite_disponible + 1
                WHERE id = ?
            ''', (doc_id,))
            
            conn.commit()
            print(f"Document {doc_id} retourné avec succès")
            return True
            
        except Exception as e:
            print(f"Erreur lors du retour du document: {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def modifier_document(self, doc_id, document):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            # Vérifier si le document existe
            cursor.execute('SELECT id FROM documents WHERE id = ?', (doc_id,))
            if not cursor.fetchone():
                print(f"Document avec l'ID {doc_id} introuvable")
                return False

            # Normaliser le type pour les documents multimédias
            type_doc = document.__class__.__name__.lower()
            if type_doc == 'ouvrageMultimedia'.lower():
                type_doc = 'multimedia'
            
            # Préparer les détails selon le type
            details = {}
            if type_doc == 'livre':
                details = {
                    'auteur': document._auteur,
                    'nb_pages': document._nb_pages,
                    'genre': document._genre,
                    'date_publication': document._date_publication.strftime('%Y-%m-%d')
                }
            elif type_doc == 'magazine':
                details = {
                    'editeur': document._editeur,
                    'frequence': document._frequence,
                    'numero': document._numero,
                    'date_publication': document._date_publication.strftime('%Y-%m-%d')
                }
            elif type_doc == 'journal':
                details = {
                    'editeur': document._editeur,
                    'date_publication': document._date_publication.strftime('%Y-%m-%d')
                }
            elif type_doc == 'multimedia':
                details = {
                    'type_media': document._type_media,
                    'duree': document._duree,
                    'date_publication': document._date_publication.strftime('%Y-%m-%d')
                }
            
            # Mettre à jour le document existant
            cursor.execute('''
                UPDATE documents 
                SET type = ?,
                    titre = ?,
                    status = ?,
                    details = ?
                WHERE id = ?
            ''', (
                type_doc,
                document.titre,
                document.status,
                json.dumps(details),
                doc_id  # Utiliser l'ID passé en paramètre, pas celui du document
            ))
            
            if cursor.rowcount == 0:
                print(f"Aucune modification effectuée pour le document {doc_id}")
                return False
            
            conn.commit()
            print(f"Document {doc_id} modifié avec succès")
            return True
            
        except Exception as e:
            print(f"Erreur lors de la modification du document: {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def creer_demande_emprunt(self, utilisateur_id, document_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            # Vérifier la disponibilité
            disponible, message = self.verifier_disponibilite(document_id)
            if not disponible:
                return False, message
            
            # Vérifier si l'utilisateur n'a pas déjà une demande en cours
            cursor.execute('''
                SELECT COUNT(*) FROM demandes_emprunt 
                WHERE utilisateur_id = ? AND document_id = ? AND status = 'en_attente'
            ''', (utilisateur_id, document_id))
            if cursor.fetchone()[0] > 0:
                return False, "Une demande est déjà en cours pour ce document"
            
            # Vérifier si l'utilisateur n'a pas déjà emprunté ce document
            cursor.execute('''
                SELECT COUNT(*) FROM emprunts 
                WHERE utilisateur_id = ? AND document_id = ? AND date_retour IS NULL
            ''', (utilisateur_id, document_id))
            if cursor.fetchone()[0] > 0:
                return False, "Vous avez déjà emprunté ce document"
            
            # Créer la demande
            date_demande = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                INSERT INTO demandes_emprunt (utilisateur_id, document_id, date_demande)
                VALUES (?, ?, ?)
            ''', (utilisateur_id, document_id, date_demande))
            
            conn.commit()
            return True, "Demande d'emprunt créée avec succès"
        finally:
            conn.close()

    def get_demandes_emprunt(self, status='en_attente'):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT de.id, de.utilisateur_id, de.document_id, de.date_demande,
                       u.username, d.titre, d.type
                FROM demandes_emprunt de
                JOIN utilisateurs u ON de.utilisateur_id = u.id
                JOIN documents d ON de.document_id = d.id
                WHERE de.status = ?
            ''', (status,))
            return cursor.fetchall()
        finally:
            conn.close()

    def traiter_demande_emprunt(self, demande_id, decision, commentaire=""):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            # Récupérer les informations de la demande
            cursor.execute('''
                SELECT utilisateur_id, document_id FROM demandes_emprunt
                WHERE id = ? AND status = 'en_attente'
            ''', (demande_id,))
            result = cursor.fetchone()
            if not result:
                return False, "Demande introuvable ou déjà traitée"
            
            utilisateur_id, document_id = result
            
            if decision == 'validee':
                # Vérifier la disponibilité
                cursor.execute('''
                    SELECT quantite_disponible FROM documents WHERE id = ?
                ''', (document_id,))
                if cursor.fetchone()[0] <= 0:
                    return False, "Document non disponible"
                
                # Créer l'emprunt
                date_emprunt = datetime.now().strftime('%Y-%m-%d')
                cursor.execute('''
                    INSERT INTO emprunts (utilisateur_id, document_id, date_emprunt)
                    VALUES (?, ?, ?)
                ''', (utilisateur_id, document_id, date_emprunt))
                
                # Mettre à jour la quantité disponible
                cursor.execute('''
                    UPDATE documents 
                    SET quantite_disponible = quantite_disponible - 1
                    WHERE id = ?
                ''', (document_id,))
            
            # Mettre à jour le statut de la demande
            cursor.execute('''
                UPDATE demandes_emprunt
                SET status = ?, commentaire = ?
                WHERE id = ?
            ''', (decision, commentaire, demande_id))
            
            conn.commit()
            return True, "Demande traitée avec succès"
        finally:
            conn.close() 

    def verifier_disponibilite(self, doc_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT quantite_disponible, status FROM documents WHERE id = ?
            ''', (doc_id,))
            result = cursor.fetchone()
            if not result:
                return False, "Document introuvable"
            
            quantite_disponible, status = result
            if quantite_disponible <= 0:
                return False, "Document non disponible"
            if status != 'disponible':
                return False, "Document non empruntable actuellement"
            
            return True, "Document disponible"
        finally:
            conn.close() 

    def search_documents(self, criteria):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            query = """
                SELECT id, type, titre, status, details
                FROM documents
                WHERE 1=1
            """
            params = []
            
            if criteria.get('titre'):
                query += " AND LOWER(titre) LIKE LOWER(?)"
                params.append(f"%{criteria['titre']}%")
            
            if criteria.get('type'):
                query += " AND LOWER(type) = LOWER(?)"
                params.append(criteria['type'].lower())
            
            if criteria.get('auteur'):
                query += " AND json_extract(details, '$.auteur') LIKE ?"
                params.append(f"%{criteria['auteur']}%")
            
            if criteria.get('editeur'):
                query += " AND json_extract(details, '$.editeur') LIKE ?"
                params.append(f"%{criteria['editeur']}%")
            
            if criteria.get('date_debut'):
                query += " AND json_extract(details, '$.date_publication') >= ?"
                params.append(criteria['date_debut'])
            
            if criteria.get('date_fin'):
                query += " AND json_extract(details, '$.date_publication') <= ?"
                params.append(criteria['date_fin'])
            
            cursor.execute(query, params)
            documents = []
            
            for row in cursor.fetchall():
                doc_id, type_doc, titre, status, details = row
                details = json.loads(details)
                
                 # Récupérer date_publication depuis les détails
            date_publication = details.get('date_publication', None)
            if date_publication:
                # Convertir en objet datetime si c'est une chaîne
                date_publication = datetime.strptime(date_publication, '%Y-%m-%d')
                
                if type_doc == 'livre':
                    doc = Livre(
                        doc_id, titre,
                        details.get('auteur', ''),
                        int(details.get('nb_pages', 0)),
                        details.get('genre', ''),
                        details.get('date_publication', ''),
                        status
                    )
                elif type_doc == 'magazine':
                    doc = Magazine(
                        doc_id, titre,
                        details.get('editeur', ''),
                        details.get('frequence', ''),
                        details.get('numero', ''),
                        details.get('date_publication', ''),
                        status
                    )
                elif type_doc == 'journal':
                    doc = Journal(
                        doc_id, titre,
                        details.get('editeur', ''),
                        date_publication,
                        status
                    )
                elif type_doc == 'multimedia':
                    doc = OuvrageMultimedia(
                        doc_id, titre,
                        details.get('type_media', ''),
                        int(details.get('duree', 0)),
                        date_publication,
                        status
                    )
                
                documents.append(doc)
            
            return documents
        finally:
            conn.close() 

    def get_demandes_utilisateur(self, user_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT de.id, de.document_id, de.date_demande, de.status, 
                       de.commentaire, d.titre, d.type
                FROM demandes_emprunt de
                JOIN documents d ON de.document_id = d.id
                WHERE de.utilisateur_id = ?
                ORDER BY de.date_demande DESC
            ''', (user_id,))
            
            return [{
                'id': row[0],
                'document_id': row[1],
                'date_demande': row[2],
                'status': row[3],
                'commentaire': row[4],
                'titre_document': row[5],
                'type_document': row[6]
            } for row in cursor.fetchall()]
        finally:
            conn.close()

    def annuler_demande_emprunt(self, demande_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE demandes_emprunt
                SET status = 'annulee'
                WHERE id = ? AND status = 'en_attente'
            ''', (demande_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def relancer_demande_emprunt(self, demande_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            # Récupérer les informations de la demande originale
            cursor.execute('''
                SELECT utilisateur_id, document_id
                FROM demandes_emprunt
                WHERE id = ?
            ''', (demande_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            user_id, doc_id = result
            
            # Créer une nouvelle demande
            date_demande = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                INSERT INTO demandes_emprunt (utilisateur_id, document_id, date_demande, status)
                VALUES (?, ?, ?, 'en_attente')
            ''', (user_id, doc_id, date_demande))
            
            conn.commit()
            return True
        finally:
            conn.close() 