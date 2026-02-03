"""
Database Connection Manager
Singleton pattern for SQLite connection with WAL mode for performance
"""
import sqlite3
import threading
from config import DATABASE_PATH, DB_BUSY_TIMEOUT_MS


class DatabaseConnection:
    """Thread-safe singleton database connection manager"""
    
    _instance = None
    _lock = threading.Lock()
    _local = threading.local()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._db_path = DATABASE_PATH
    
    def get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = self._create_connection()
        return self._local.connection
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection with optimal settings"""
        conn = sqlite3.connect(
            self._db_path,
            timeout=DB_BUSY_TIMEOUT_MS / 1000,
            check_same_thread=False
        )
        # Enable WAL mode for better concurrent read performance
        conn.execute("PRAGMA journal_mode=WAL")
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys=ON")
        # Return rows as dictionaries
        conn.row_factory = sqlite3.Row
        return conn
    
    def close(self):
        """Close the thread-local connection"""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return cursor"""
        conn = self.get_connection()
        return conn.execute(query, params)
    
    def executemany(self, query: str, params_list: list) -> sqlite3.Cursor:
        """Execute a query with multiple parameter sets"""
        conn = self.get_connection()
        return conn.executemany(query, params_list)
    
    def commit(self):
        """Commit the current transaction"""
        self.get_connection().commit()
    
    def rollback(self):
        """Rollback the current transaction"""
        self.get_connection().rollback()


# Global database instance
db = DatabaseConnection()
