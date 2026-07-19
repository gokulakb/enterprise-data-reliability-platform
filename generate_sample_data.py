"""
Generate sample CSV data files.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_sample_data():
    """Generate sample data CSV files."""
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(exist_ok=True)
    
    print("Generating sample data...")
    
    # Generate source orders
    n_orders = 50
    orders_data = {
        'order_id': range(1, n_orders + 1),
        'customer_id': np.random.randint(1, 20, n_orders),
        'order_date': pd.date_range('2024-01-01', periods=n_orders, freq='H') + pd.Timedelta(days=np.random.randint(0, 10, n_orders)),
        'total_amount': np.random.uniform(50, 5000, n_orders).round(2),
        'status': np.random.choice(['pending', 'processing', 'shipped', 'delivered', 'cancelled'], n_orders),
        'source_timestamp': datetime.now() + pd.Timedelta(seconds=np.random.randint(0, 3600, n_orders))
    }
    source_orders = pd.DataFrame(orders_data)
    
    # Generate warehouse orders (some missing)
    warehouse_orders = source_orders.copy()
    # Remove 10% of records
    warehouse_orders = warehouse_orders.sample(frac=0.9)
    warehouse_orders['warehouse_timestamp'] = datetime.now() + pd.Timedelta(minutes=np.random.randint(1, 60, len(warehouse_orders)))
    
    # Generate source customers
    n_customers = 20
    customer_names = ['Acme Corp', 'TechStart Inc', 'Global Solutions', 'DataFlow Ltd', 
                     'CloudWorks', 'SmartSystems', 'DigitalEdge', 'InnovateHub',
                     'QuantumTech', 'NexGen Solutions', 'Apex Digital', 'CoreLogic',
                     'ZenData', 'CloudSphere', 'DataVault', 'InfoTech',
                     'Apex Solutions', 'Core Systems', 'Zen Solutions', 'Cloud Solutions']
    
    customers_data = {
        'customer_id': range(1, n_customers + 1),
        'name': customer_names[:n_customers],
        'email': [f"{name.lower().replace(' ', '.')}@example.com" for name in customer_names[:n_customers]],
        'created_at': pd.date_range('2023-06-01', periods=n_customers, freq='D'),
        'source_timestamp': datetime.now() + pd.Timedelta(seconds=np.random.randint(0, 3600, n_customers))
    }
    source_customers = pd.DataFrame(customers_data)
    
    # Generate warehouse customers
    warehouse_customers = source_customers.copy()
    warehouse_customers['warehouse_timestamp'] = datetime.now() + pd.Timedelta(minutes=np.random.randint(1, 30, len(warehouse_customers)))
    
    # Generate source events
    n_events = 30
    event_types = ['page_view', 'click', 'purchase', 'signup', 'login', 'logout']
    events_data = {
        'event_id': range(1, n_events + 1),
        'customer_id': np.random.randint(1, 20, n_events),
        'event_type': np.random.choice(event_types, n_events),
        'event_timestamp': pd.date_range('2024-01-10', periods=n_events, freq='H') + pd.Timedelta(days=np.random.randint(0, 5, n_events)),
        'source_timestamp': datetime.now() + pd.Timedelta(seconds=np.random.randint(0, 600, n_events))
    }
    source_events = pd.DataFrame(events_data)
    
    # Generate warehouse events
    warehouse_events = source_events.copy()
    warehouse_events = warehouse_events.sample(frac=0.95)
    warehouse_events['warehouse_timestamp'] = datetime.now() + pd.Timedelta(minutes=np.random.randint(1, 45, len(warehouse_events)))
    
    # Generate pipeline runs
    pipelines = ['order_pipeline', 'customer_pipeline', 'event_pipeline']
    n_runs = 30
    runs_data = []
    for i in range(n_runs):
        start_time = datetime.now() - timedelta(hours=random.randint(1, 48))
        duration = random.randint(30, 300)
        status = 'success' if random.random() < 0.85 else 'failed'
        runs_data.append({
            'run_id': i + 1,
            'pipeline_name': random.choice(pipelines),
            'start_time': start_time,
            'end_time': start_time + timedelta(seconds=duration),
            'status': status,
            'records_processed': random.randint(100, 1000) if status == 'success' else random.randint(0, 50),
            'error_message': '' if status == 'success' else 'Pipeline execution error'
        })
    pipeline_runs = pd.DataFrame(runs_data)
    
    # Generate audit logs
    actions = ['dashboard_view', 'report_export', 'data_validation', 'signoff_approval']
    users = ['admin', 'data_engineer', 'analytics_lead']
    n_logs = 50
    logs_data = []
    for i in range(n_logs):
        logs_data.append({
            'log_id': i + 1,
            'timestamp': datetime.now() - timedelta(hours=random.randint(1, 168)),
            'user': random.choice(users),
            'action': random.choice(actions),
            'metric_type': random.choice(['completeness', 'freshness', 'reconciliation']),
            'metric_value': round(random.uniform(85, 100), 1),
            'status': random.choice(['PASS', 'WARNING', 'FAIL']),
            'details': f"Sample log entry {i+1}"
        })
    audit_logs = pd.DataFrame(logs_data)
    
    # Save all CSV files
    source_orders.to_csv(data_dir / 'source_orders.csv', index=False)
    warehouse_orders.to_csv(data_dir / 'warehouse_orders.csv', index=False)
    source_customers.to_csv(data_dir / 'source_customers.csv', index=False)
    warehouse_customers.to_csv(data_dir / 'warehouse_customers.csv', index=False)
    source_events.to_csv(data_dir / 'source_events.csv', index=False)
    warehouse_events.to_csv(data_dir / 'warehouse_events.csv', index=False)
    pipeline_runs.to_csv(data_dir / 'pipeline_runs.csv', index=False)
    audit_logs.to_csv(data_dir / 'audit_logs.csv', index=False)
    
    print(f"✅ Generated sample data in {data_dir}")
    print(f"  - Source Orders: {len(source_orders)} records")
    print(f"  - Warehouse Orders: {len(warehouse_orders)} records")
    print(f"  - Source Customers: {len(source_customers)} records")
    print(f"  - Warehouse Customers: {len(warehouse_customers)} records")
    print(f"  - Source Events: {len(source_events)} records")
    print(f"  - Warehouse Events: {len(warehouse_events)} records")
    print(f"  - Pipeline Runs: {len(pipeline_runs)} records")
    print(f"  - Audit Logs: {len(audit_logs)} records")

if __name__ == "__main__":
    generate_sample_data()