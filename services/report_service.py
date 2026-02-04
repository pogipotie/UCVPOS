"""
Report Service - Sales reports and data exports
"""
import csv
import os
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
from repositories.sales_repo import sales_repo
from repositories.product_repo import product_repo
from config import BASE_DIR


class ReportService:
    """Business logic for generating reports and exports"""
    
    def get_daily_report(self, report_date: date = None, cashier_username: str = None) -> Dict[str, Any]:
        """Generate daily sales report"""
        if report_date is None:
            report_date = date.today()
        
        summary = sales_repo.get_daily_summary(report_date, cashier_username)
        sales = sales_repo.get_sales_by_date(report_date, cashier_username)
        
        # Populate items for detailed reporting
        for sale in sales:
            sale.items = sales_repo.get_sale_items(sale.id)
        
        return {
            'date': report_date,
            'summary': summary,
            'sales': sales,
            'generated_at': datetime.now()
        }
    
    def get_monthly_report(self, year: int = None, month: int = None) -> Dict[str, Any]:
        """Generate monthly sales report"""
        if year is None or month is None:
            today = date.today()
            year = today.year
            month = today.month
        
        summary = sales_repo.get_monthly_summary(year, month)
        
        # Get daily breakdown
        from calendar import monthrange
        last_day = monthrange(year, month)[1]
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        
        daily_summaries = []
        current = start_date
        while current <= end_date:
            daily = sales_repo.get_daily_summary(current)
            if daily['total_transactions'] > 0:
                daily_summaries.append(daily)
            current += timedelta(days=1)
        
        return {
            'year': year,
            'month': month,
            'summary': summary,
            'daily_breakdown': daily_summaries,
            'generated_at': datetime.now()
        }
    
    def get_low_stock_report(self) -> Dict[str, Any]:
        """Generate low stock alert report"""
        products = product_repo.get_low_stock()
        
        return {
            'title': 'Low Stock Report',
            'products': products,
            'count': len(products),
            'generated_at': datetime.now()
        }
    
    def get_expiry_report(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Generate expiry report"""
        expired = product_repo.get_expired()
        expiring_soon = product_repo.get_expiring_soon(days_ahead)
        
        return {
            'title': 'Expiry Report',
            'expired_products': expired,
            'expiring_soon': expiring_soon,
            'expired_count': len(expired),
            'expiring_soon_count': len(expiring_soon),
            'generated_at': datetime.now()
        }
    
    def get_inventory_report(self) -> Dict[str, Any]:
        """Generate full inventory report"""
        products = product_repo.get_all(limit=100000)
        
        total_value = sum(p.price * p.stock_quantity for p in products)
        total_items = sum(p.stock_quantity for p in products)
        
        return {
            'title': 'Inventory Report',
            'products': products,
            'total_products': len(products),
            'total_items': total_items,
            'total_value': total_value,
            'generated_at': datetime.now()
        }
    
    def export_to_csv(self, data: List[Dict], filename: str, 
                      headers: List[str] = None) -> str:
        """Export data to CSV file"""
        exports_dir = os.path.join(BASE_DIR, "exports")
        os.makedirs(exports_dir, exist_ok=True)
        
        filepath = os.path.join(exports_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if data:
                if headers is None:
                    headers = list(data[0].keys())
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
        
        return filepath
    
    def export_sales_to_csv(self, start_date: date, end_date: date, cashier_username: str = None) -> str:
        """Export sales data to CSV"""
        sales = sales_repo.get_sales_by_date_range(start_date, end_date, cashier_username)
        
        data = []
        for sale in sales:
            # Fetch items for detail
            items = sales_repo.get_sale_items(sale.id)
            products_str = ", ".join([f"{i.product_name} ({i.quantity})" for i in items])
            
            data.append({
                'Sale ID': sale.id,
                'Date': sale.sale_date,
                'Items': products_str,
                'Total': sale.total_amount,
                'Status': sale.status,
                'Cashier': sale.cashier_name or 'N/A'
            })
        
        filename = f"sales_{start_date.isoformat()}_to_{end_date.isoformat()}.csv"
        return self.export_to_csv(data, filename)
    
    def export_inventory_to_csv(self) -> str:
        """Export inventory to CSV"""
        products = product_repo.get_all(limit=100000)
        
        data = []
        for p in products:
            data.append({
                'Barcode': p.barcode,
                'Name': p.name,
                'Price': p.price,
                'Stock': p.stock_quantity,
                'Min Stock': p.min_stock_level,
                'Batch': p.batch_number or '',
                'Expiry': p.expiry_date.isoformat() if p.expiry_date else '',
                'Prescription Required': 'Yes' if p.prescription_required else 'No'
            })
        
        filename = f"inventory_{date.today().isoformat()}.csv"
        return self.export_to_csv(data, filename)
    
    def export_to_excel(self, data: List[Dict], filename: str, 
                        sheet_name: str = 'Data') -> str:
        """Export data to Excel file"""
        try:
            from openpyxl import Workbook
        except ImportError:
            raise ImportError("openpyxl is required for Excel export")
        
        exports_dir = os.path.join(BASE_DIR, "exports")
        os.makedirs(exports_dir, exist_ok=True)
        
        filepath = os.path.join(exports_dir, filename)
        
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name
        
        if data:
            # Write headers
            headers = list(data[0].keys())
            ws.append(headers)
            
            # Write data rows
            for row in data:
                ws.append([row.get(h, '') for h in headers])
        
        wb.save(filepath)
        return filepath


# Global service instance
report_service = ReportService()
