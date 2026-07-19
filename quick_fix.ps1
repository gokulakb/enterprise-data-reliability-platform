# Quick Fix Script
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "FIXING DATA RELIABILITY PLATFORM" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Activate virtual environment
.\venv\Scripts\Activate.ps1

Write-Host "`n[1/4] Dropping and recreating database..." -ForegroundColor Yellow
python -c "import sys; sys.path.insert(0, '.'); from database.database import db_manager; db_manager.drop_tables(); db_manager.create_tables()"

Write-Host "`n[2/4] Seeding database..." -ForegroundColor Yellow
python -c "import sys; sys.path.insert(0, '.'); from database.seed_data import seed_database; seed_database()"

Write-Host "`n[3/4] Verifying data..." -ForegroundColor Yellow
python -c "import sys; sys.path.insert(0, '.'); from database.database import get_db_session; from sqlalchemy import text; session = get_db_session(); tables = ['source_orders', 'warehouse_orders', 'source_customers', 'warehouse_customers', 'source_events', 'warehouse_events', 'pipeline_runs', 'audit_logs']; print('\nData Verification:'); [print(f'  {table}: {session.execute(text(f\"SELECT COUNT(*) FROM {table}\")).scalar()} rows') for table in tables]"

Write-Host "`n[4/4] Starting application..." -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
streamlit run app.py