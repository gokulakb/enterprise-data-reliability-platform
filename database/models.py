"""
Database models and schema definitions.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from config.settings import DATABASE_URL
from utils.logger import get_logger

logger = get_logger()
Base = declarative_base()

class SourceOrder(Base):
    """Source orders table model."""
    __tablename__ = 'source_orders'
    
    order_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer)
    order_date = Column(DateTime)
    total_amount = Column(Float)
    status = Column(String)
    source_timestamp = Column(DateTime)
    
    def to_dict(self):
        return {
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'total_amount': self.total_amount,
            'status': self.status,
            'source_timestamp': self.source_timestamp.isoformat() if self.source_timestamp else None
        }

class WarehouseOrder(Base):
    """Warehouse orders table model."""
    __tablename__ = 'warehouse_orders'
    
    order_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer)
    order_date = Column(DateTime)
    total_amount = Column(Float)
    status = Column(String)
    warehouse_timestamp = Column(DateTime)
    
    def to_dict(self):
        return {
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'total_amount': self.total_amount,
            'status': self.status,
            'warehouse_timestamp': self.warehouse_timestamp.isoformat() if self.warehouse_timestamp else None
        }

class SourceCustomer(Base):
    """Source customers table model."""
    __tablename__ = 'source_customers'
    
    customer_id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    created_at = Column(DateTime)
    source_timestamp = Column(DateTime)
    
    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'source_timestamp': self.source_timestamp.isoformat() if self.source_timestamp else None
        }

class WarehouseCustomer(Base):
    """Warehouse customers table model."""
    __tablename__ = 'warehouse_customers'
    
    customer_id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    created_at = Column(DateTime)
    warehouse_timestamp = Column(DateTime)
    
    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'warehouse_timestamp': self.warehouse_timestamp.isoformat() if self.warehouse_timestamp else None
        }

class SourceEvent(Base):
    """Source events table model."""
    __tablename__ = 'source_events'
    
    event_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer)
    event_type = Column(String)
    event_timestamp = Column(DateTime)
    source_timestamp = Column(DateTime)
    
    def to_dict(self):
        return {
            'event_id': self.event_id,
            'customer_id': self.customer_id,
            'event_type': self.event_type,
            'event_timestamp': self.event_timestamp.isoformat() if self.event_timestamp else None,
            'source_timestamp': self.source_timestamp.isoformat() if self.source_timestamp else None
        }

class WarehouseEvent(Base):
    """Warehouse events table model."""
    __tablename__ = 'warehouse_events'
    
    event_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer)
    event_type = Column(String)
    event_timestamp = Column(DateTime)
    warehouse_timestamp = Column(DateTime)
    
    def to_dict(self):
        return {
            'event_id': self.event_id,
            'customer_id': self.customer_id,
            'event_type': self.event_type,
            'event_timestamp': self.event_timestamp.isoformat() if self.event_timestamp else None,
            'warehouse_timestamp': self.warehouse_timestamp.isoformat() if self.warehouse_timestamp else None
        }

class PipelineRun(Base):
    """Pipeline runs table model."""
    __tablename__ = 'pipeline_runs'
    
    run_id = Column(Integer, primary_key=True)
    pipeline_name = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(String)
    records_processed = Column(Integer)
    error_message = Column(Text)
    
    def to_dict(self):
        return {
            'run_id': self.run_id,
            'pipeline_name': self.pipeline_name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'records_processed': self.records_processed,
            'error_message': self.error_message
        }

class AuditLog(Base):
    """Audit logs table model."""
    __tablename__ = 'audit_logs'
    
    log_id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    user = Column(String)
    action = Column(String)
    metric_type = Column(String)
    metric_value = Column(Float)
    status = Column(String)
    details = Column(Text)
    
    def to_dict(self):
        return {
            'log_id': self.log_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'user': self.user,
            'action': self.action,
            'metric_type': self.metric_type,
            'metric_value': self.metric_value,
            'status': self.status,
            'details': self.details
        }

# Database initialization
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_session():
    """Get database session."""
    return Session()