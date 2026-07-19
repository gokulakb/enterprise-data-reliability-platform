"""
Load data from CSV files into database.
"""
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

from config.settings import DATABASE_URL, DATA_DIR
from utils.logger import get_logger

logger = get_logger()

def load_csv_to_db():
    """Load CSV data into database."""
    print("=" * 60)
    print("LOADING CSV DATA INTO DATABASE")
    print("=" * 60)
    
    engine = create_engine(DATABASE_URL)
    
    csv_files = [
        'source_orders.csv',
        'warehouse_orders.csv',
        'source_customers.csv',
        'warehouse_customers.csv',
        'source_events.csv',
        'warehouse_events.csv',
        'pipeline_runs.csv',
        'audit_history.csv'
    ]
    
    for csv_file in csv_files:
        csv_path = DATA_DIR / csv_file
        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                table_name = csv_file.replace('.csv', '')
                df.to_sql(table_name, engine, if_exists='replace', index=False)
                print(f"✅ Loaded {len(df)} rows into {table_name}")
            except Exception as e:
                print(f"❌ Failed to load {csv_file}: {str(e)}")
        else:
            print(f"⚠️ CSV file not found: {csv_path}")
    
    print("\n" + "=" * 60)
    print("✅ Data loading complete!")
    print("=" * 60)

if __name__ == "__main__":
    load_csv_to_db()