"""
Fix data seeding script - Run this to populate your database with sample data.
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from database.create_tables import init_database
from database.seed_data import DataSeeder
from utils.logger import get_logger

logger = get_logger()

def fix_data():
    """Fix data seeding issues."""
    print("=" * 60)
    print("FIXING DATA SEEDING ISSUES")
    print("=" * 60)
    
    # Step 1: Initialize database
    print("\n[1/3] Initializing database...")
    if init_database():
        print("✅ Database initialized successfully")
    else:
        print("❌ Failed to initialize database")
        return False
    
    # Step 2: Seed data
    print("\n[2/3] Seeding data...")
    seeder = DataSeeder()
    if seeder.seed_all():
        print("✅ Data seeded successfully")
    else:
        print("❌ Failed to seed data")
        return False
    
    # Step 3: Verify data
    print("\n[3/3] Verifying data...")
    from database.database import get_db_session
    from sqlalchemy import text
    session = get_db_session()
    
    tables = ['source_orders', 'warehouse_orders', 'source_customers', 
              'warehouse_customers', 'source_events', 'warehouse_events', 
              'pipeline_runs', 'audit_logs']
    
    for table in tables:
        try:
            result = session.execute(text(f'SELECT COUNT(*) FROM {table}'))
            count = result.scalar() or 0
            print(f"  {table}: {count} rows")
        except:
            print(f"  {table}: Table not found")
    
    print("\n" + "=" * 60)
    print("✅ Data fix complete! Restart your application.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    fix_data()