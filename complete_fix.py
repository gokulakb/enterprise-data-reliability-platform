"""
Complete fix for data issues.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

def complete_fix():
    """Run complete fix for data issues."""
    print("=" * 70)
    print("COMPLETE DATA FIX FOR ENTERPRISE DATA RELIABILITY PLATFORM")
    print("=" * 70)
    
    # Step 1: Generate sample data
    print("\n[1/4] Generating sample CSV data...")
    from generate_sample_data import generate_sample_data
    generate_sample_data()
    
    # Step 2: Initialize database
    print("\n[2/4] Initializing database...")
    from database.create_tables import init_database
    if init_database():
        print("✅ Database initialized")
    else:
        print("❌ Database initialization failed")
        return
    
    # Step 3: Load data from CSV
    print("\n[3/4] Loading data from CSV...")
    from load_csv_data import load_csv_to_db
    load_csv_to_db()
    
    # Step 4: Verify data
    print("\n[4/4] Verifying data...")
    from database.database import get_db_session
    from sqlalchemy import text
    session = get_db_session()
    
    tables = ['source_orders', 'warehouse_orders', 'source_customers', 
              'warehouse_customers', 'source_events', 'warehouse_events', 
              'pipeline_runs', 'audit_logs']
    
    total_rows = 0
    for table in tables:
        try:
            result = session.execute(text(f'SELECT COUNT(*) FROM {table}'))
            count = result.scalar() or 0
            total_rows += count
            print(f"  {table}: {count} rows")
        except:
            print(f"  {table}: Table not found")
    
    print("\n" + "=" * 70)
    if total_rows > 0:
        print(f"✅ SUCCESS! {total_rows} total rows loaded into database.")
        print("✅ Your application should now display data.")
        print("\n👉 Run: streamlit run app.py")
    else:
        print("❌ No data found. Please check the error messages above.")
    print("=" * 70)

if __name__ == "__main__":
    complete_fix()