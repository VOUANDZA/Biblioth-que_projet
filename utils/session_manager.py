from datetime import datetime, timedelta
import jwt
import uuid

class SessionManager:
    def __init__(self):
        self.secret_key = "your-secret-key"  # À stocker dans un fichier de configuration
        self.sessions = {}
        self.session_duration = timedelta(hours=2)

    def create_session(self, user_id, username, role):
        session_id = str(uuid.uuid4())
        expiration = datetime.now() + self.session_duration
        
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'username': username,
            'role': role,
            'created_at': datetime.now(),
            'expires_at': expiration,
            'last_activity': datetime.now()
        }
        
        self.sessions[session_id] = session_data
        return session_id

    def get_session(self, session_id):
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        if datetime.now() > session['expires_at']:
            self.destroy_session(session_id)
            return None
        
        session['last_activity'] = datetime.now()
        return session

    def destroy_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def refresh_session(self, session_id):
        session = self.get_session(session_id)
        if session:
            session['expires_at'] = datetime.now() + self.session_duration
            return True
        return False 