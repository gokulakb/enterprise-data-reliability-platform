"""
Database seeding script - Run this from the project root.
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.seed_data import seed_database

if __name__ == "__main__":
    print("=" * 60)
    print("SEEDING DATABASE")
    print("=" * 60)
    
    # First, clear existing data
    from database.database import get_db_session
    from sqlalchemy import text
    session = get_db_session()
    
    print("\n[1/3] Clearing existing data...")
    tables = ['source_orders', 'warehouse_orders', 'source_customers', 
             'warehouse_customers', 'source_events', 'warehouse_events', 
             'pipeline_runs', 'audit_logs']
    
    for table in tables:
        try:
            session.execute(text(f"DELETE FROM {table}"))
            print(f"  ✅ Cleared {table}")
        except Exception as e:
            print(f"  ⚠️ Could not clear {table}: {str(e)}")
    session.commit()
    
    print("\n[2/3] Seeding new data...")
    success = seed_database()
    
    print("\n[3/3] Verifying data...")
    for table in tables:
        try:
            result = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  {table}: {result} rows")
        except:
            print(f"  {table}: Table not found")
    
    print("\n" + "=" * 60)
    if success:
        print("✅ DATABASE SEEDED SUCCESSFULLY!")
    else:
        print("❌ DATABASE SEEDING FAILED!")
    print("=" * 60)