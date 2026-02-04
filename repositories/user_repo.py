from typing import Optional, List
import bcrypt
from datetime import datetime
from database.connection import db
from database.models import User

class UserRepository:
    """Repository for user data access"""
    
    def create_user(self, user: User, password: str) -> Optional[User]:
        """Create a new user with hashed password"""
        try:
            # Hash password
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
            query = """
                INSERT INTO users (username, password_hash, role, full_name, is_active)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor = db.execute(query, (
                user.username,
                password_hash,
                user.role,
                user.full_name,
                1 if user.is_active else 0
            ))
            db.commit()
            
            user.id = cursor.lastrowid
            user.password_hash = password_hash
            return user
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def get_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        query = "SELECT * FROM users WHERE username = ?"
        row = db.execute(query, (username,)).fetchone()
        
        if row:
            return self._map_row_to_user(row)
        return None
    
    def get_all(self) -> List[User]:
        """List all users"""
        query = "SELECT * FROM users ORDER BY username"
        rows = db.execute(query).fetchall()
        return [self._map_row_to_user(row) for row in rows]
    
    def verify_password(self, user: User, password: str) -> bool:
        """Verify password against hash"""
        if not user or not user.password_hash:
            return False
            
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                user.password_hash.encode('utf-8')
            )
        except Exception as e:
            print(f"Password verification error: {e}")
            return False
    
    def update_last_login(self, user_id: int):
        """Update last login timestamp"""
        query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute(query, (user_id,))
        db.commit()

    def update_user(self, user: User) -> bool:
        """Update user details"""
        try:
            query = """
                UPDATE users 
                SET role = ?, full_name = ?, is_active = ?
                WHERE id = ?
            """
            db.execute(query, (
                user.role,
                user.full_name,
                1 if user.is_active else 0,
                user.id
            ))
            db.commit()
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
            
    def update_password(self, user_id: int, new_password: str) -> bool:
        """Reset user password"""
        try:
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
            
            query = "UPDATE users SET password_hash = ? WHERE id = ?"
            db.execute(query, (password_hash, user_id))
            db.commit()
            return True
        except Exception as e:
            print(f"Error changing password: {e}")
            return False

    def _map_row_to_user(self, row) -> User:
        """Map database row to User object"""
        return User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            role=row['role'],
            full_name=row['full_name'],
            is_active=bool(row['is_active']),
            created_at=row['created_at'], # raw timestamp string for now
            last_login=row['last_login']
        )

user_repo = UserRepository()
