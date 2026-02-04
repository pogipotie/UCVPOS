"""
Settings Service - Application configuration management
Persists settings to a JSON file
"""
import json
import os
from typing import Dict, Any

SETTINGS_FILE = "settings.json"

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
    """Manages application settings"""
    
    def __init__(self):
        self._settings = self._load_settings()
        self._ensure_backup_dir()
        
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create default"""
        if not os.path.exists(SETTINGS_FILE):
            self._save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()
            
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                # Merge with defaults to ensure all keys exist (migrations)
                merged = DEFAULT_SETTINGS.copy()
                self._recursive_update(merged, data)
                return merged
        except Exception as e:
            print(f"Error loading settings: {e}")
            return DEFAULT_SETTINGS.copy()
            
    def _save_settings(self, settings: Dict[str, Any]):
        """Save settings to file"""
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def _recursive_update(self, base_dict, update_dict):
        """Recursively update a dictionary"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict:
                self._recursive_update(base_dict[key], value)
            else:
                base_dict[key] = value

    def _ensure_backup_dir(self):
        """Ensure default backup directory exists"""
        path = self.get("system", "backup_path")
        if path and not os.path.exists(path):
            try:
                os.makedirs(path)
            except:
                pass

    def get(self, section: str, key: str) -> Any:
        """Get a specific setting value"""
        return self._settings.get(section, {}).get(key)
        
    def set(self, section: str, key: str, value: Any):
        """Set a setting value and save"""
        if section not in self._settings:
            self._settings[section] = {}
        self._settings[section][key] = value
        self._save_settings(self._settings)
        
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self._settings
    
    def update_all(self, new_settings: Dict[str, Any]):
        """Update multiple settings at once"""
        self._settings = new_settings
        self._save_settings(self._settings)

# Global instance
settings_service = SettingsService()
