from typing import Optional
from database.models import User
from repositories.user_repo import user_repo

class AuthService:
    """Authentication and Session Management"""
    
    def __init__(self):
        self._current_user: Optional[User] = None
    
    def login(self, username, password) -> Optional[User]:
        """Attempt login"""
        print(f"Attempting login for: {username}")
        user = user_repo.get_by_username(username)
        
        if user and user.is_active:
            if user_repo.verify_password(user, password):
                self._current_user = user
                user_repo.update_last_login(user.id)
                print(f"Login successful for {username} (Role: {user.role})")
                return user
        
        print("Login failed")
        return None
    
    def logout(self):
        """Clear session"""
        self._current_user = None
    
    def get_current_user(self) -> Optional[User]:
        """Get currently logged in user"""
        return self._current_user
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self._current_user and self._current_user.role == 'admin'
    
    def verify_password(self, username: str, password: str) -> bool:
        """Verify a user's password without logging in"""
        user = user_repo.get_by_username(username)
        if user:
            return user_repo.verify_password(user, password)
        return False
    
    def ensure_default_admin(self):
        """Create default admin if no users exist"""
        users = user_repo.get_all()
        if not users:
            print("No users found. Creating default admin (admin/admin123)...")
            admin = User(
                username="admin",
                role="admin",
                full_name="System Administrator",
                is_active=True
            )
            user_repo.create_user(admin, "admin123")

auth_service = AuthService()
