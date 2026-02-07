"""
Migration Script: SQLite to MySQL
Transfers all data from pos.db to the MySQL database defined in config.py
"""
import sys
import os
import sqlite3
import pymysql
import pymysql.cursors
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

def migrate():
    print("Starting migration from SQLite to MySQL...")
    
    # 1. Connect to SQLite
    if not os.path.exists(config.DATABASE_PATH):
        print(f"Error: SQLite database not found at {config.DATABASE_PATH}")
        return
        
    sqlite_conn = sqlite3.connect(config.DATABASE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    print(f"Connected to SQLite: {config.DATABASE_PATH}")
    
    # 2. Connect to MySQL
    try:
        mysql_conn = pymysql.connect(
            host=config.MYSQL_CONFIG['host'],
            user=config.MYSQL_CONFIG['user'],
            password=config.MYSQL_CONFIG['password'],
            database=config.MYSQL_CONFIG['database'],
            cursorclass=pymysql.cursors.DictCursor
        )
        print(f"Connected to MySQL: {config.MYSQL_CONFIG['host']}/{config.MYSQL_CONFIG['database']}")
    except pymysql.Error as err:
        print(f"Error connecting to MySQL: {err}")
        print("Please ensure XAMPP MySQL is running and the database exists.")
        return

    # 3. Initialize MySQL Schema
    print("Initializing MySQL schema...")
    from database.schema_mysql import SCHEMA_SQL, INDEX_SQL
    
    cursor = mysql_conn.cursor()
    
    # Disable FK checks
    cursor.execute("SET FOREIGN_KEY_CHECKS=0")
    
    # Run Schema
    for statement in SCHEMA_SQL.split(';'):
        if statement.strip():
            try:
                cursor.execute(statement)
            except Exception as e:
                print(f"Schema Error: {e}")
                
    mysql_conn.commit()
    print("Schema created.")

    # 4. Transfer Data
    tables = [
        'users',
        'products',
        'sales',
        'sale_items',
        'payments',
        'audit_logs',
        'void_logs'
    ]
    
    sqlite_cursor = sqlite_conn.cursor()
    
    for table in tables:
        print(f"Migrating table: {table}...")
        try:
            # Get all data from SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"  - No data in {table}")
                continue
                
            # Get column names
            columns = [description[0] for description in sqlite_cursor.description]
            cols_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            
            # Prepare Insert Query
            insert_query = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"
            
            # Convert rows to tuples
            data = [tuple(row) for row in rows]
            
            # Bulk Insert
            cursor.executemany(insert_query, data)
            mysql_conn.commit()
            print(f"  - Migrated {len(data)} rows.")
            
        except Exception as e:
            print(f"Error migrating {table}: {e}")
            
    # Re-enable FK checks
    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    
    # Create Indexes
    print("Creating indexes...")
    for statement in INDEX_SQL.split(';'):
        if statement.strip():
             try:
                cursor.execute(statement)
             except Exception as e:
                 pass 
    
    mysql_conn.commit()
    
    cursor.close()
    mysql_conn.close()
    sqlite_conn.close()
    
    print("\nMigration completed successfully!")
    print("To use MySQL, update config.py: DB_TYPE = 'mysql'")

if __name__ == "__main__":
    migrate()
