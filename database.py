import sqlite3
from datetime import datetime
import json

class BibliothequeDB:
    def __init__(self, db_file="bibliotheque.db"):
        self.db_file = db_file
        self.creer_tables()
    
    def creer_tables(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Table Documents
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            titre TEXT NOT NULL,
            status TEXT DEFAULT 'disponible',
            details TEXT NOT NULL
        )''')
        
        # Table Emprunts
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS emprunts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            emprunteur TEXT NOT NULL,
            date_emprunt TEXT NOT NULL,
            date_retour TEXT,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        )''')
        
        conn.commit()
        conn.close()
    
    def ajouter_document(self, type_doc, titre, details):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO documents (type, titre, details) VALUES (?, ?, ?)',
            (type_doc, titre, details)
        )
        conn.commit()
        conn.close()
    
    def rechercher_documents(self, critere, valeur):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            f'SELECT * FROM documents WHERE {critere} LIKE ?',
            (f'%{valeur}%',)
        )
        resultats = cursor.fetchall()
        conn.close()
        return resultats
    
    def emprunter_document(self, doc_id, emprunteur):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            # Vérifier si le document est disponible
            cursor.execute('SELECT status FROM documents WHERE id = ?', (doc_id,))
            if cursor.fetchone()[0] != 'disponible':
                return False
            
            # Mettre à jour le status du document
            cursor.execute(
                'UPDATE documents SET status = ? WHERE id = ?',
                ('emprunté', doc_id)
            )
            
            # Créer l'emprunt
            cursor.execute(
                'INSERT INTO emprunts (document_id, emprunteur, date_emprunt) VALUES (?, ?, ?)',
                (doc_id, emprunteur, datetime.now().strftime('%Y-%m-%d'))
            )
            
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
            # Mettre à jour le status du document
            cursor.execute(
                'UPDATE documents SET status = ? WHERE id = ?',
                ('disponible', doc_id)
            )
            
            # Mettre à jour la date de retour
            cursor.execute(
                '''
                UPDATE emprunts 
                SET date_retour = ? 
                WHERE document_id = ? AND date_retour IS NULL
                ''',
                (datetime.now().strftime('%Y-%m-%d'), doc_id)
            )
            
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()
    
    def calculer_frais_retard(self, emprunt_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT e.date_emprunt, d.type, d.details
                FROM emprunts e
                JOIN documents d ON e.document_id = d.id
                WHERE e.id = ? AND e.date_retour IS NULL
            ''', (emprunt_id,))
            
            resultat = cursor.fetchone()
            if not resultat:
                return 0
            
            date_emprunt = datetime.strptime(resultat[0], '%Y-%m-%d')
            type_doc = resultat[1]
            details = json.loads(resultat[2])
            
            jours_retard = (datetime.now() - date_emprunt).days
            
            if jours_retard <= 0:
                return 0
            
            # Calcul selon le type de document
            if type_doc == 'livre':
                return jours_retard * 1.0
            elif type_doc == 'magazine':
                return (jours_retard * 1.0) + 2.0
            elif type_doc == 'journal':
                return jours_retard * 1.0
            elif type_doc == 'multimedia':
                return (details['duree'] * 1.0) + (jours_retard * 2.0)
            
            return 0
        finally:
            conn.close() 
    
    def get_emprunts_utilisateur(self, emprunteur):
        """Récupère tous les emprunts d'un utilisateur"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT e.id, d.titre, d.type, e.date_emprunt, e.date_retour
                FROM emprunts e
                JOIN documents d ON e.document_id = d.id
                WHERE e.emprunteur = ?
                ORDER BY e.date_emprunt DESC
            ''', (emprunteur,))
            return cursor.fetchall()
        finally:
            conn.close()
    
    def get_documents_disponibles(self):
        """Récupère tous les documents disponibles"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT id, type, titre, details
                FROM documents
                WHERE status = 'disponible'
                ORDER BY type, titre
            ''')
            return cursor.fetchall()
        finally:
            conn.close()
    
    def get_documents_en_retard(self):
        """Récupère tous les documents en retard"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT d.titre, e.emprunteur, e.date_emprunt, 
                       julianday('now') - julianday(e.date_emprunt) as jours_retard
                FROM emprunts e
                JOIN documents d ON e.document_id = d.id
                WHERE e.date_retour IS NULL 
                AND julianday('now') - julianday(e.date_emprunt) > 14
                ORDER BY jours_retard DESC
            ''')
            return cursor.fetchall()
        finally:
            conn.close()
    
    def get_statistiques(self):
        """Récupère les statistiques de la bibliothèque"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        try:
            stats = {}
            
            # Nombre total de documents par type
            cursor.execute('''
                SELECT type, COUNT(*) 
                FROM documents 
                GROUP BY type
            ''')
            stats['documents_par_type'] = dict(cursor.fetchall())
            
            # Nombre de documents empruntés
            cursor.execute('''
                SELECT COUNT(*) 
                FROM documents 
                WHERE status = 'emprunté'
            ''')
            stats['documents_empruntes'] = cursor.fetchone()[0]
            
            # Nombre d'emprunts en retard
            cursor.execute('''
                SELECT COUNT(*) 
                FROM emprunts 
                WHERE date_retour IS NULL 
                AND julianday('now') - julianday(date_emprunt) > 14
            ''')
            stats['emprunts_en_retard'] = cursor.fetchone()[0]
            
            return stats
        finally:
            conn.close() 