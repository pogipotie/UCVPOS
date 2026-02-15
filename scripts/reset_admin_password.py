import sys
import os
import bcrypt

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db
from repositories.user_repo import user_repo

def reset_password():
    print("Resetting 'admin' password...")
    
    # 1. Connect
    try:
        # db.get_connection() initializes connection based on config
        conn = db.get_connection()
        if not conn:
             print("Failed to get database connection.")
             return
    except Exception as e:
        print(f"Connection error: {e}")
        return

    # 2. Find admin
    user = user_repo.get_by_username("admin")
    
    if not user:
        print("User 'admin' not found. Creating it...")
        from database.models import User
        new_admin = User(
            username="admin", 
            role="admin", 
            full_name="System Administrator", 
            is_active=True
        )
        if user_repo.create_user(new_admin, "admin123"):
             print("Created 'admin' with password 'admin123'")
        else:
             print("Failed to create admin user.")
        return

    # 3. Reset Password
    print(f"Found user: {user.username} (ID: {user.id})")
    
    # Update logic (manual hash to be safe/direct)
    new_password = "admin123"
    try:
        if user_repo.update_password(user.id, new_password):
            print(f"\nSUCCESS! Password for 'admin' reset to: {new_password}")
        else:
            print("\nFAILED to update password.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reset_password()
