"""
Database Connection Manager
Singleton pattern for SQLite connection with WAL mode for performance
"""
import sqlite3
import threading
import config
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
        self._db_type = getattr(config, 'DB_TYPE', 'sqlite')
    
    def get_connection(self):
        """Get thread-local database connection"""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = self._create_connection()
            # For MySQL, we might need to check if connection is alive
            if self._db_type == 'mysql':
                try:
                    self._local.connection.ping(reconnect=True, attempts=3, delay=5)
                except:
                    # Reconnect if ping fails
                    self._local.connection = self._create_connection()
        return self._local.connection
    
    def _create_connection(self):
        """Create a new database connection"""
        if self._db_type == 'mysql':
            import pymysql
            import pymysql.cursors
            conn = pymysql.connect(
                host=config.MYSQL_CONFIG['host'],
                user=config.MYSQL_CONFIG['user'],
                password=config.MYSQL_CONFIG['password'],
                database=config.MYSQL_CONFIG['database'],
                cursorclass=pymysql.cursors.DictCursor
            )
            return conn
        else:
            # SQLite default
            conn = sqlite3.connect(
                self._db_path,
                timeout=DB_BUSY_TIMEOUT_MS / 1000,
                check_same_thread=False
            )
            try:
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA foreign_keys=ON")
            except:
                pass
            conn.row_factory = sqlite3.Row
            return conn
    
    def close(self):
        """Close the thread-local connection"""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
    
    def execute(self, query: str, params: tuple = ()):
        """Execute a query and return cursor"""
        conn = self.get_connection()
        
        # MySQL Adaptation: Replace ? with %s
        if self._db_type == 'mysql':
            query = query.replace('?', '%s')
            # Pymysql cursor is already DictCursor from connect
            cursor = conn.cursor() 
            cursor.execute(query, params)
            return cursor
        
        return conn.execute(query, params)
    
    def executemany(self, query: str, params_list: list):
        """Execute a query with multiple parameter sets"""
        conn = self.get_connection()
        
        if self._db_type == 'mysql':
            query = query.replace('?', '%s')
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            return cursor
            
        return conn.executemany(query, params_list)
    
    def commit(self):
        """Commit the current transaction"""
        self.get_connection().commit()
    
    def rollback(self):
        """Rollback the current transaction"""
        self.get_connection().rollback()


# Global database instance
db = DatabaseConnection()
