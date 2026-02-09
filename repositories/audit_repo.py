"""
Audit Repository - Audit trail and void logs
Non-editable records for compliance
"""
from typing import List
from datetime import date
from database.connection import db
from database.models import AuditLog, VoidLog


class AuditRepository:
    """Data access layer for audit logs"""
    
    def log_action(self, action: str, entity_type: str, 
                   entity_id: int = None, details: str = None) -> int:
        """Create an audit log entry"""
        cursor = db.execute(
            """INSERT INTO audit_logs 
               (action, entity_type, entity_id, details)
               VALUES (?, ?, ?, ?)""",
            (action, entity_type, entity_id, details)
        )
        db.commit()
        return cursor.lastrowid
    
    def get_logs(self, limit: int = 100, offset: int = 0) -> List[AuditLog]:
        """Get audit logs with pagination"""
        cursor = db.execute(
            """SELECT * FROM audit_logs 
               ORDER BY timestamp DESC
               LIMIT ? OFFSET ?""",
            (limit, offset)
        )
        return [self._row_to_audit_log(row) for row in cursor.fetchall()]
    
    def get_logs_by_entity(self, entity_type: str, 
                           entity_id: int = None) -> List[AuditLog]:
        """Get audit logs for a specific entity"""
        if entity_id:
            cursor = db.execute(
                """SELECT * FROM audit_logs 
                   WHERE entity_type = ? AND entity_id = ?
                   ORDER BY timestamp DESC""",
                (entity_type, entity_id)
            )
        else:
            cursor = db.execute(
                """SELECT * FROM audit_logs 
                   WHERE entity_type = ?
                   ORDER BY timestamp DESC""",
                (entity_type,)
            )
        return [self._row_to_audit_log(row) for row in cursor.fetchall()]
    
    def get_logs_by_date(self, date: date) -> List[AuditLog]:
        """Get audit logs for a specific date"""
        start = f"{date.isoformat()} 00:00:00"
        end = f"{date.isoformat()} 23:59:59"
        cursor = db.execute(
            """SELECT * FROM audit_logs 
               WHERE timestamp BETWEEN ? AND ?
               ORDER BY timestamp DESC""",
            (start, end)
        )
        return [self._row_to_audit_log(row) for row in cursor.fetchall()]
    
    def get_logs_by_date_range(self, start_date: date, end_date: date) -> List[AuditLog]:
        """Get audit logs between two dates"""
        start = f"{start_date.isoformat()} 00:00:00"
        end = f"{end_date.isoformat()} 23:59:59"
        cursor = db.execute(
            """SELECT * FROM audit_logs 
               WHERE timestamp BETWEEN ? AND ?
               ORDER BY timestamp DESC""",
            (start, end)
        )
        return [self._row_to_audit_log(row) for row in cursor.fetchall()]
    
    def _row_to_audit_log(self, row) -> AuditLog:
        """Convert database row to AuditLog object"""
        return AuditLog(
            id=row['id'],
            action=row['action'],
            entity_type=row['entity_type'],
            entity_id=row['entity_id'],
            details=row['details'],
            timestamp=row['timestamp']
        )


class VoidLogRepository:
    """Data access layer for void logs - these records are immutable"""
    
    def create(self, void_log: VoidLog) -> int:
        """Create a void log entry"""
        cursor = db.execute(
            """INSERT INTO void_logs 
               (sale_id, reason, voided_by, original_total)
               VALUES (?, ?, ?, ?)""",
            (
                void_log.sale_id,
                void_log.reason,
                void_log.voided_by,
                void_log.original_total
            )
        )
        db.commit()
        return cursor.lastrowid
    
    def get_by_sale_id(self, sale_id: int) -> List[VoidLog]:
        """Get void logs for a specific sale"""
        cursor = db.execute(
            "SELECT * FROM void_logs WHERE sale_id = ?",
            (sale_id,)
        )
        return [self._row_to_void_log(row) for row in cursor.fetchall()]
    
    def get_all(self, limit: int = 100) -> List[VoidLog]:
        """Get all void logs"""
        cursor = db.execute(
            "SELECT * FROM void_logs ORDER BY voided_at DESC LIMIT ?",
            (limit,)
        )
        return [self._row_to_void_log(row) for row in cursor.fetchall()]
    
    def get_by_date(self, date: date) -> List[VoidLog]:
        """Get void logs for a specific date"""
        start = f"{date.isoformat()} 00:00:00"
        end = f"{date.isoformat()} 23:59:59"
        cursor = db.execute(
            """SELECT * FROM void_logs 
               WHERE voided_at BETWEEN ? AND ?
               ORDER BY voided_at DESC""",
            (start, end)
        )
        return [self._row_to_void_log(row) for row in cursor.fetchall()]
    
    def _row_to_void_log(self, row) -> VoidLog:
        """Convert database row to VoidLog object"""
        return VoidLog(
            id=row['id'],
            sale_id=row['sale_id'],
            reason=row['reason'],
            voided_by=row['voided_by'],
            voided_at=row['voided_at'],
            original_total=row['original_total']
        )


# Global repository instances
audit_repo = AuditRepository()
void_log_repo = VoidLogRepository()
