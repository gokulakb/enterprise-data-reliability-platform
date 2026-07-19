"""
Seed database with realistic enterprise data.
"""
import sys
import os
from pathlib import Path

# Add project root to path if running directly
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import numpy as np

from database.models import (
    SourceOrder, WarehouseOrder, SourceCustomer, WarehouseCustomer,
    SourceEvent, WarehouseEvent, PipelineRun, AuditLog
)
from database.database import get_db_session
from config.settings import DATABASE_URL
from utils.logger import get_logger

logger = get_logger()

class DataSeeder:
    """Seed the database with realistic test data."""
    
    def __init__(self):
        self.session = get_db_session()
        self.engine = create_engine(DATABASE_URL)
        self.seed_count = 50  # Reduced for testing
        
    def seed_all(self):
        """Seed all tables with test data."""
        try:
            logger.info("Starting data seeding...")
            
            # Clear existing data first
            self._clear_tables()
            
            # Generate realistic data with inconsistencies
            self.seed_customers()
            self.seed_orders()
            self.seed_events()
            self.seed_pipeline_runs()
            self.seed_audit_logs()
            
            self.session.commit()
            logger.info("Data seeding completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error seeding data: {str(e)}")
            self.session.rollback()
            return False
    
    def _clear_tables(self):
        """Clear all tables before seeding."""
        try:
            tables = ['source_orders', 'warehouse_orders', 'source_customers', 
                     'warehouse_customers', 'source_events', 'warehouse_events', 
                     'pipeline_runs', 'audit_logs']
            for table in tables:
                self.session.execute(text(f"DELETE FROM {table}"))
            self.session.commit()
            logger.info("Cleared existing data from tables")
        except Exception as e:
            logger.error(f"Error clearing tables: {str(e)}")
            self.session.rollback()
    
    def _generate_timestamp(self, days_back: int = 30):
        """Generate a random timestamp within the last N days."""
        return datetime.now() - timedelta(
            days=random.randint(1, days_back), 
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
    
    def seed_customers(self):
        """Seed customer data with intentional inconsistencies."""
        customer_names = ['Acme Corp', 'TechStart Inc', 'Global Solutions', 'DataFlow Ltd', 
                         'CloudWorks', 'SmartSystems', 'DigitalEdge', 'InnovateHub',
                         'QuantumTech', 'NexGen Solutions', 'Apex Digital', 'CoreLogic',
                         'ZenData', 'CloudSphere', 'DataVault', 'InfoTech']
        
        for i in range(1, self.seed_count + 1):
            name = random.choice(customer_names)
            email = f"{name.lower().replace(' ', '.')}@example.com"
            created_at = self._generate_timestamp(365)
            source_timestamp = self._generate_timestamp(30)
            
            # Create source customer
            source_customer = SourceCustomer(
                customer_id=i,
                name=name,
                email=email,
                created_at=created_at,
                source_timestamp=source_timestamp
            )
            self.session.add(source_customer)
            
            # Create warehouse customer (some with mismatches)
            if random.random() < 0.15:  # 15% mismatch
                warehouse_customer = WarehouseCustomer(
                    customer_id=i,
                    name=name + " (Updated)" if random.random() < 0.5 else name,
                    email=f"updated_{email}" if random.random() < 0.5 else email,
                    created_at=created_at + timedelta(days=random.randint(1, 30)),
                    warehouse_timestamp=self._generate_timestamp(10)
                )
            else:
                warehouse_customer = WarehouseCustomer(
                    customer_id=i,
                    name=name,
                    email=email,
                    created_at=created_at,
                    warehouse_timestamp=self._generate_timestamp(10)
                )
            self.session.add(warehouse_customer)
        
        logger.info(f"Seeded {self.seed_count} customer records")
    
    def seed_orders(self):
        """Seed order data with intentional inconsistencies."""
        statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        
        for i in range(1, self.seed_count + 1):
            customer_id = random.randint(1, self.seed_count)
            order_date = self._generate_timestamp(180)
            total_amount = round(random.uniform(50, 5000), 2)
            status = random.choice(statuses)
            source_timestamp = self._generate_timestamp(30)
            
            # Create source order
            source_order = SourceOrder(
                order_id=i,
                customer_id=customer_id,
                order_date=order_date,
                total_amount=total_amount,
                status=status,
                source_timestamp=source_timestamp
            )
            self.session.add(source_order)
            
            # Create warehouse order (some with mismatches or missing)
            if random.random() < 0.08:  # 8% missing in warehouse
                continue
                
            if random.random() < 0.12:  # 12% mismatch
                warehouse_order = WarehouseOrder(
                    order_id=i,
                    customer_id=customer_id + random.randint(1, 5),
                    order_date=order_date + timedelta(hours=random.randint(1, 48)),
                    total_amount=total_amount * (1 + random.uniform(-0.2, 0.2)),
                    status=random.choice(['pending', 'processing']),
                    warehouse_timestamp=self._generate_timestamp(5)
                )
            else:
                warehouse_order = WarehouseOrder(
                    order_id=i,
                    customer_id=customer_id,
                    order_date=order_date,
                    total_amount=total_amount,
                    status=status,
                    warehouse_timestamp=self._generate_timestamp(5)
                )
            self.session.add(warehouse_order)
        
        logger.info(f"Seeded {self.seed_count} order records")
    
    def seed_events(self):
        """Seed event data with intentional inconsistencies."""
        event_types = ['page_view', 'click', 'purchase', 'signup', 'login', 'logout', 'download']
        
        for i in range(1, self.seed_count + 1):
            customer_id = random.randint(1, self.seed_count)
            event_type = random.choice(event_types)
            event_timestamp = self._generate_timestamp(90)
            source_timestamp = self._generate_timestamp(30)
            
            # Create source event
            source_event = SourceEvent(
                event_id=i,
                customer_id=customer_id,
                event_type=event_type,
                event_timestamp=event_timestamp,
                source_timestamp=source_timestamp
            )
            self.session.add(source_event)
            
            # Create warehouse event (some with delays or missing)
            if random.random() < 0.07:  # 7% missing in warehouse
                continue
                
            warehouse_event = WarehouseEvent(
                event_id=i,
                customer_id=customer_id,
                event_type=event_type,
                event_timestamp=event_timestamp + timedelta(hours=random.randint(1, 24)),
                warehouse_timestamp=self._generate_timestamp(5)
            )
            self.session.add(warehouse_event)
        
        logger.info(f"Seeded {self.seed_count} event records")
    
    def seed_pipeline_runs(self):
        """Seed pipeline runs with realistic statuses."""
        pipelines = ['order_pipeline', 'customer_pipeline', 'event_pipeline', 
                    'reconciliation_pipeline', 'quality_pipeline']
        
        for i in range(1, 50):
            pipeline = random.choice(pipelines)
            start_time = self._generate_timestamp(48)
            duration = random.randint(5, 180)  # 5 seconds to 3 minutes
            
            # 15% chance of failure
            if random.random() < 0.15:
                status = random.choice(['failed', 'failed', 'success'])
                error = random.choice([
                    'Connection timeout', 'Data mismatch detected', 
                    'Schema validation failed', 'Transform error',
                    'Resource limit exceeded'
                ]) if status == 'failed' else ''
                records_processed = random.randint(0, 100)
            else:
                status = random.choice(['success', 'success', 'success', 'running'])
                error = ''
                records_processed = random.randint(100, 1000)
            
            run = PipelineRun(
                run_id=i,
                pipeline_name=pipeline,
                start_time=start_time,
                end_time=start_time + timedelta(seconds=duration),
                status=status,
                records_processed=records_processed,
                error_message=error
            )
            self.session.add(run)
        
        logger.info(f"Seeded 49 pipeline runs")
    
    def seed_audit_logs(self):
        """Seed audit logs with historical events."""
        actions = ['dashboard_view', 'report_export', 'data_validation', 'signoff_approval',
                  'alert_acknowledge', 'threshold_update', 'pipeline_trigger', 'data_refresh']
        users = ['admin', 'data_engineer', 'analytics_lead', 'executive']
        
        # Clear existing audit logs first to avoid duplicate key errors
        try:
            self.session.execute(text("DELETE FROM audit_logs"))
            self.session.commit()
        except Exception as e:
            logger.warning(f"Could not clear audit_logs: {str(e)}")
        
        for i in range(1, 50):
            action = random.choice(actions)
            metric_type = random.choice(['completeness', 'freshness', 'reconciliation', 'quality'])
            status = random.choice(['PASS', 'WARNING', 'FAIL', 'PENDING'])
            
            log = AuditLog(
                log_id=i,
                timestamp=self._generate_timestamp(60),
                user=random.choice(users),
                action=action,
                metric_type=metric_type,
                metric_value=round(random.uniform(85, 100), 1),
                status=status,
                details=f"Audit log for {action} on {metric_type}"
            )
            self.session.add(log)
        
        logger.info(f"Seeded 49 audit logs")


def seed_database():
    """Main function to seed database."""
    seeder = DataSeeder()
    return seeder.seed_all()


if __name__ == "__main__":
    seed_database()