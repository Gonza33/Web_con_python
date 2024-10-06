import hashlib
from db_connection import DatabaseConnection

class UserService:
    def __init__(self, db_name):
        self.db_name = db_name

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def authenticate_user(self, username, password):
        hashed_password = self.hash_password(password)
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        with DatabaseConnection(self.db_name) as db:
            db.execute(query, (username, hashed_password))
            user = db.fetchone()
        return user is not None

    def create_user(self, username, password):
        hashed_password = self.hash_password(password)
        query = "INSERT INTO users (username, password) VALUES (?, ?)"
        with DatabaseConnection(self.db_name) as db:
            db.execute(query, (username, hashed_password))

    def user_exists(self, username):
        query = "SELECT * FROM users WHERE username = ?"
        with DatabaseConnection(self.db_name) as db:
            db.execute(query, (username,))
            user = db.fetchone()
        return user is not None
