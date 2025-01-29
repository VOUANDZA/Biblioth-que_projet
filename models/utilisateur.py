class Utilisateur:
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.session_id = None  # Ajout de l'attribut session_id
    
    def is_admin(self):
        return self.role == "administrateur" 