"""
Settings Service - Application configuration management
Persists settings to the database for backup compatibility
"""
import json
import os
from typing import Dict, Any
from database.connection import db


DEFAULT_SETTINGS = {
    "store_info": {
        "name": "UCV Pharmacy",
        "address": "123 Main St, City",
        "phone": "0912-345-6789",
        "header_text": "Thank you for your purchase!"
    },
    "financial": {
        "tax_rate": 12.0,
        "currency_symbol": "₱"
    },
    "system": {
        "backup_path": os.path.join(os.getcwd(), "backups"),
        "printer_name": ""
    }
}


class SettingsService:
    """Manages application settings stored in database"""
    
    def __init__(self):
        self._settings_cache = None  # Cache for performance
        self._ensure_table_exists()
        self._ensure_backup_dir()
        
    def _ensure_table_exists(self):
        """Ensure settings table exists and migrate from JSON if needed"""
        try:
            # Check if settings table has data
            cursor = db.execute("SELECT COUNT(*) FROM settings")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Try to migrate from settings.json
                self._migrate_from_json()
        except Exception as e:
            # Table might not exist yet (first run), silently continue
            pass
    
    def _migrate_from_json(self):
        """Migrate settings from settings.json to database"""
        json_file = "settings.json"
        
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    json_settings = json.load(f)
                
                # Save each section to database
                for section, values in json_settings.items():
                    key = section
                    value = json.dumps(values)
                    db.execute(
                        "INSERT INTO settings (setting_key, setting_value) VALUES (%s, %s) "
                    "ON DUPLICATE KEY UPDATE setting_value = %s",
                    (key, value, value)
                    )
                db.commit()
                print("Settings migrated from settings.json to database")
                
                # Rename old file to indicate migration
                os.rename(json_file, "settings.json.migrated")
                
            except Exception as e:
                print(f"Error migrating settings from JSON: {e}")
                self._save_defaults()
        else:
            # No JSON file, save defaults
            self._save_defaults()
    
    def _save_defaults(self):
        """Save default settings to database"""
        try:
            for section, values in DEFAULT_SETTINGS.items():
                value = json.dumps(values)
                db.execute(
                    "INSERT INTO settings (setting_key, setting_value) VALUES (%s, %s) "
                    "ON DUPLICATE KEY UPDATE setting_value = %s",
                    (section, value, value)
                )
            db.commit()
        except Exception as e:
            print(f"Error saving default settings: {e}")

    def _ensure_backup_dir(self):
        """Ensure default backup directory exists"""
        path = self.get("system", "backup_path")
        if path and not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                pass

    def _load_all(self) -> Dict[str, Any]:
        """Load all settings from database"""
        if self._settings_cache is not None:
            return self._settings_cache
        
        try:
            cursor = db.execute("SELECT setting_key, setting_value FROM settings")
            rows = cursor.fetchall()
            
            settings = {}
            for row in rows:
                key = row['setting_key'] if isinstance(row, dict) else row[0]
                value = row['setting_value'] if isinstance(row, dict) else row[1]
                try:
                    settings[key] = json.loads(value) if value else {}
                except:
                    settings[key] = value
            
            # Merge with defaults to ensure all keys exist
            merged = DEFAULT_SETTINGS.copy()
            self._recursive_update(merged, settings)
            self._settings_cache = merged
            return merged
            
        except Exception as e:
            print(f"Error loading settings: {e}")
            return DEFAULT_SETTINGS.copy()
    
    def _recursive_update(self, base_dict, update_dict):
        """Recursively update a dictionary"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                self._recursive_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def get(self, section: str, key: str) -> Any:
        """Get a specific setting value"""
        settings = self._load_all()
        return settings.get(section, {}).get(key)
        
    def set(self, section: str, key: str, value: Any):
        """Set a setting value and save"""
        settings = self._load_all()
        if section not in settings:
            settings[section] = {}
        settings[section][key] = value
        
        # Save section to database
        try:
            section_value = json.dumps(settings[section])
            db.execute(
                "INSERT INTO settings (setting_key, setting_value) VALUES (%s, %s) "
                "ON DUPLICATE KEY UPDATE setting_value = %s",
                (section, section_value, section_value)
            )
            db.commit()
            self._settings_cache = settings
        except Exception as e:
            print(f"Error saving setting: {e}")
        
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self._load_all()
    
    def update_all(self, new_settings: Dict[str, Any]):
        """Update multiple settings at once"""
        try:
            for section, values in new_settings.items():
                section_value = json.dumps(values)
                db.execute(
                    "INSERT INTO settings (setting_key, setting_value) VALUES (%s, %s) "
                    "ON DUPLICATE KEY UPDATE setting_value = %s",
                    (section, section_value, section_value)
                )
            db.commit()
            self._settings_cache = new_settings
        except Exception as e:
            print(f"Error updating settings: {e}")
    
    def invalidate_cache(self):
        """Clear the settings cache to force reload from database"""
        self._settings_cache = None


# Global instance
settings_service = SettingsService()
