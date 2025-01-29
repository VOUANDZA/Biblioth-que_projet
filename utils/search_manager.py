from datetime import datetime
from typing import List, Dict, Any

class SearchManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.search_fields = {
            'titre': str,
            'type': str,
            'auteur': str,
            'editeur': str,
            'date_publication': datetime,
            'status': str,
            'genre': str
        }
    
    def search_documents(self, criteria: Dict[str, Any]) -> List[Dict]:
        query = """
            SELECT d.id, d.type, d.titre, d.status, d.details, 
                   d.quantite, d.quantite_disponible 
            FROM documents d
            WHERE 1=1
        """
        params = []
        
        if 'titre' in criteria and criteria['titre']:
            query += " AND LOWER(d.titre) LIKE LOWER(?)"
            params.append(f"%{criteria['titre']}%")
        
        if 'type' in criteria and criteria['type']:
            query += " AND d.type = ?"
            params.append(criteria['type'])
        
        if 'status' in criteria and criteria['status']:
            query += " AND d.status = ?"
            params.append(criteria['status'])
        
        if 'date_debut' in criteria and criteria['date_debut']:
            query += " AND json_extract(d.details, '$.date_publication') >= ?"
            params.append(criteria['date_debut'])
        
        if 'date_fin' in criteria and criteria['date_fin']:
            query += " AND json_extract(d.details, '$.date_publication') <= ?"
            params.append(criteria['date_fin'])
        
        # Recherche dans les détails JSON
        for field in ['auteur', 'editeur', 'genre']:
            if field in criteria and criteria[field]:
                query += f" AND json_extract(d.details, '$.{field}') LIKE ?"
                params.append(f"%{criteria[field]}%")
        
        return self.db.execute_query(query, params) 