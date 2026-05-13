"""
Backup Service - Database backup and restore
Supports both SQLite and MySQL databases
"""
import os
import shutil
import subprocess
from datetime import datetime
from config import DATABASE_PATH, BACKUP_DIR, DB_TYPE, MYSQL_CONFIG
from services.settings_service import settings_service


class BackupService:
    """Database backup and restore functionality"""
    
    @property
    def backup_dir(self):
        # Always fetch the latest backup path from settings
        custom_path = settings_service.get("system", "backup_path")
        if custom_path:
            path = custom_path
        else:
            path = BACKUP_DIR
            
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            print(f"Error creating backup directory {path}: {e}")
            path = BACKUP_DIR
            os.makedirs(path, exist_ok=True)
            
        return path
    
    def __init__(self):
        # Initialization logic can be empty as backup_dir is now a property
        pass
    
    def create_backup(self, custom_name: str = None) -> tuple[bool, str, str]:
        """
        Create a timestamped backup of the database
        Returns: (success, message, backup_path)
        """
        try:
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if custom_name:
                base_name = f"pos_backup_{custom_name}_{timestamp}"
            else:
                base_name = f"pos_backup_{timestamp}"
            
            if DB_TYPE == 'mysql':
                return self._create_mysql_backup(base_name)
            else:
                return self._create_sqlite_backup(base_name)
                
        except Exception as e:
            return False, f"Backup failed: {str(e)}", ""
    
    def create_secure_backup(self, zip_password: str, custom_name: str = None) -> tuple[bool, str, str]:
        """
        Create a password-protected ZIP backup of the database
        Returns: (success, message, zip_path)
        """
        import pyzipper
        
        try:
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if custom_name:
                base_name = f"pos_backup_{custom_name}_{timestamp}"
            else:
                base_name = f"pos_backup_{timestamp}"
            
            # Step 1: Create the database backup first
            if DB_TYPE == 'mysql':
                success, message, sql_path = self._create_mysql_backup(base_name)
            else:
                success, message, sql_path = self._create_sqlite_backup(base_name)
            
            if not success:
                return False, message, ""
            
            # Step 2: Create password-protected ZIP
            zip_filename = f"{base_name}_secure.zip"
            zip_path = os.path.join(self.backup_dir, zip_filename)
            
            # Use AES-256 encryption
            with pyzipper.AESZipFile(
                zip_path,
                'w',
                compression=pyzipper.ZIP_DEFLATED,
                encryption=pyzipper.WZ_AES
            ) as zf:
                zf.setpassword(zip_password.encode('utf-8'))
                # Add the SQL/DB file to the ZIP
                backup_filename = os.path.basename(sql_path)
                zf.write(sql_path, backup_filename)
            
            # Step 3: Delete the original unencrypted file
            if os.path.exists(sql_path):
                os.remove(sql_path)
            
            return True, "Secure backup created successfully", zip_path
            
        except Exception as e:
            return False, f"Secure backup failed: {str(e)}", ""
    
    def _create_sqlite_backup(self, base_name: str) -> tuple[bool, str, str]:
        """Create SQLite backup by copying the database file"""
        if not os.path.exists(DATABASE_PATH):
            return False, "Database file not found", ""
        
        filename = f"{base_name}.db"
        backup_path = os.path.join(self.backup_dir, filename)
        
        # Copy database file
        shutil.copy2(DATABASE_PATH, backup_path)
        
        return True, "Backup created successfully", backup_path
    
    def _create_mysql_backup(self, base_name: str) -> tuple[bool, str, str]:
        """Create MySQL backup using mysqldump"""
        filename = f"{base_name}.sql"
        backup_path = os.path.join(self.backup_dir, filename)
        
        # Build mysqldump command
        host = MYSQL_CONFIG.get('host', 'localhost')
        user = MYSQL_CONFIG.get('user', 'root')
        password = MYSQL_CONFIG.get('password', '')
        database = MYSQL_CONFIG.get('database', 'ucvpos_db')
        
        # Common XAMPP mysqldump paths on Windows
        mysqldump_paths = [
            r"C:\xampp\mysql\bin\mysqldump.exe",
            r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
            r"C:\Program Files (x86)\MySQL\MySQL Server 8.0\bin\mysqldump.exe",
            "mysqldump"  # Try PATH
        ]
        
        mysqldump_exe = None
        for path in mysqldump_paths:
            if path == "mysqldump" or os.path.exists(path):
                mysqldump_exe = path
                break
        
        if not mysqldump_exe:
            return False, "mysqldump not found. Please ensure MySQL/XAMPP is installed.", ""
        
        # Build command
        cmd = [mysqldump_exe, f"--host={host}", f"--user={user}", database]
        
        if password:
            cmd.insert(3, f"--password={password}")
        
        try:
            # Run mysqldump and save output to file
            with open(backup_path, 'w', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True
                )
            
            if result.returncode != 0:
                # Clean up empty file on error
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                return False, f"mysqldump error: {result.stderr}", ""
            
            return True, "MySQL backup created successfully", backup_path
            
        except FileNotFoundError:
            return False, "mysqldump not found in PATH. Please ensure MySQL is installed.", ""
        except Exception as e:
            return False, f"Backup failed: {str(e)}", ""
    
    def list_backups(self) -> list[dict]:
        """List all available backups"""
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.db') or filename.endswith('.sql') or filename.endswith('.zip'):
                filepath = os.path.join(self.backup_dir, filename)
                stat = os.stat(filepath)
                
                # Determine type
                if filename.endswith('.zip'):
                    backup_type = 'Secure (ZIP)'
                elif filename.endswith('.sql'):
                    backup_type = 'MySQL'
                else:
                    backup_type = 'SQLite'
                
                backups.append({
                    'filename': filename,
                    'path': filepath,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_mtime),
                    'type': backup_type
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
            if backup_path.endswith('.sql'):
                return self._restore_mysql_backup(backup_path)
            else:
                return self._restore_sqlite_backup(backup_path)
                
        except Exception as e:
            return False, f"Restore failed: {str(e)}"
    
    def _restore_sqlite_backup(self, backup_path: str) -> tuple[bool, str]:
        """Restore SQLite database from backup"""
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
    
    def _restore_mysql_backup(self, backup_path: str) -> tuple[bool, str]:
        """Restore MySQL database from SQL backup"""
        host = MYSQL_CONFIG.get('host', 'localhost')
        user = MYSQL_CONFIG.get('user', 'root')
        password = MYSQL_CONFIG.get('password', '')
        database = MYSQL_CONFIG.get('database', 'ucvpos_db')
        
        # Common XAMPP mysql paths on Windows
        mysql_paths = [
            r"C:\xampp\mysql\bin\mysql.exe",
            r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe",
            "mysql"
        ]
        
        mysql_exe = None
        for path in mysql_paths:
            if path == "mysql" or os.path.exists(path):
                mysql_exe = path
                break
        
        if not mysql_exe:
            return False, "mysql client not found. Please ensure MySQL/XAMPP is installed."
        
        # Build command
        cmd = [mysql_exe, f"--host={host}", f"--user={user}", database]
        
        if password:
            cmd.insert(3, f"--password={password}")
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True
                )
            
            if result.returncode != 0:
                return False, f"MySQL restore error: {result.stderr}"
            
            return True, "MySQL database restored successfully."
            
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
