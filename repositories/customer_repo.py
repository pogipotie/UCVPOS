from typing import List, Optional
from database.connection import db
from database.models import Customer
from datetime import datetime

class CustomerRepository:
    def create(self, customer: Customer) -> Optional[Customer]:
        """Create a new customer"""
        try:
            query = """
                INSERT INTO customers (name, id_number, type, address, contact_number)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor = db.execute(query, (
                customer.name,
                customer.id_number,
                customer.type,
                customer.address,
                customer.contact_number
            ))  
            db.commit()
            customer.id = cursor.lastrowid
            return customer
        except Exception as e:
            print(f"Error creating customer: {e}")
            return None

    def get_by_id_number(self, id_number: str, customer_type: str = None) -> Optional[Customer]:
        """Get customer by ID number (and optional type)"""
        try:
            if customer_type:
                query = "SELECT * FROM customers WHERE id_number = %s AND type = %s"
                params = (id_number, customer_type)
            else:
                query = "SELECT * FROM customers WHERE id_number = %s LIMIT 1"
                params = (id_number,)
                
            cursor = db.execute(query, params)
            row = cursor.fetchone()
            return self._map_row_to_customer(row) if row else None
        except Exception as e:
            print(f"Error getting customer by ID number: {e}")
            return None

    def search(self, query_str: str, limit: int = 10, customer_type: str = None) -> List[Customer]:
        """Search customers by name or ID number, optionally filtered by type"""
        try:
            search_term = f"%{query_str}%"
            if customer_type:
                query = """
                    SELECT * FROM customers 
                    WHERE (name LIKE %s OR id_number LIKE %s) AND type = %s
                    ORDER BY name ASC
                    LIMIT %s
                """
                params = (search_term, search_term, customer_type, limit)
            else:
                query = """
                    SELECT * FROM customers 
                    WHERE name LIKE %s OR id_number LIKE %s
                    ORDER BY name ASC
                    LIMIT %s
                """
                params = (search_term, search_term, limit)
                
            cursor = db.execute(query, params)
            rows = cursor.fetchall()
            return [self._map_row_to_customer(row) for row in rows]
        except Exception as e:
            print(f"Error searching customers: {e}")
            return []

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get customer by PK ID"""
        try:
            query = "SELECT * FROM customers WHERE id = %s"
            cursor = db.execute(query, (customer_id,))
            row = cursor.fetchone()
            return self._map_row_to_customer(row) if row else None
        except Exception as e:
            print(f"Error getting customer by ID: {e}")
            return None

    def _map_row_to_customer(self, row) -> Customer:
        """Map database row to Customer object"""
        return Customer(
            id=row['id'],
            name=row['name'],
            id_number=row['id_number'],
            type=row['type'],
            address=row.get('address'),
            contact_number=row.get('contact_number'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )

customer_repo = CustomerRepository()
