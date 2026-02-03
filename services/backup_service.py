"""
Backup Service - Database backup and restore
"""
import os
import shutil
from datetime import datetime
from config import DATABASE_PATH, BACKUP_DIR


class BackupService:
    """Database backup and restore functionality"""
    
    def __init__(self):
        self.backup_dir = BACKUP_DIR
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, custom_name: str = None) -> tuple[bool, str, str]:
        """
        Create a timestamped backup of the database
        Returns: (success, message, backup_path)
        """
        if not os.path.exists(DATABASE_PATH):
            return False, "Database file not found", ""
        
        try:
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if custom_name:
                filename = f"pos_backup_{custom_name}_{timestamp}.db"
            else:
                filename = f"pos_backup_{timestamp}.db"
            
            backup_path = os.path.join(self.backup_dir, filename)
            
            # Copy database file
            shutil.copy2(DATABASE_PATH, backup_path)
            
            return True, f"Backup created successfully", backup_path
            
        except Exception as e:
            return False, f"Backup failed: {str(e)}", ""
    
    def list_backups(self) -> list[dict]:
        """List all available backups"""
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.db'):
                filepath = os.path.join(self.backup_dir, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'path': filepath,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_mtime)
                })
        
        # Sort by creation time, newest first
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups
    
    def restore_backup(self, backup_path: str) -> tuple[bool, str]:
        """
        Restore database from a backup
        Warning: This will overwrite the current database!
        """
        if not os.path.exists(backup_path):
            return False, "Backup file not found"
        
        try:
            # Create a safety backup first
            safety_backup = os.path.join(
                self.backup_dir, 
                f"pre_restore_safety_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            )
            if os.path.exists(DATABASE_PATH):
                shutil.copy2(DATABASE_PATH, safety_backup)
            
            # Restore from backup
            shutil.copy2(backup_path, DATABASE_PATH)
            
            return True, "Database restored successfully. Previous database saved as safety backup."
            
        except Exception as e:
            return False, f"Restore failed: {str(e)}"
    
    def delete_backup(self, backup_path: str) -> tuple[bool, str]:
        """Delete a backup file"""
        if not os.path.exists(backup_path):
            return False, "Backup file not found"
        
        try:
            os.remove(backup_path)
            return True, "Backup deleted"
        except Exception as e:
            return False, f"Delete failed: {str(e)}"
    
    def get_backup_count(self) -> int:
        """Get total number of backups"""
        return len(self.list_backups())
    
    def cleanup_old_backups(self, keep_count: int = 10) -> tuple[int, str]:
        """
        Delete old backups, keeping only the most recent ones
        Returns: (deleted_count, message)
        """
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            return 0, "No cleanup needed"
        
        to_delete = backups[keep_count:]
        deleted = 0
        
        for backup in to_delete:
            success, _ = self.delete_backup(backup['path'])
            if success:
                deleted += 1
        
        return deleted, f"Deleted {deleted} old backups"


# Global service instance
backup_service = BackupService()
