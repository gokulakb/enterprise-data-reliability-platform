"""
Database connection and initialization.
"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from pathlib import Path

from config.settings import DATABASE_URL
from utils.logger import get_logger

logger = get_logger()
Base = declarative_base()
metadata = MetaData()

class DatabaseManager:
    """Manages database connections and sessions."""
    
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize database engine and session factory."""
        try:
            # Ensure database directory exists
            db_path = Path(DATABASE_URL.replace('sqlite:///', ''))
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self._engine = create_engine(
                DATABASE_URL,
                echo=False,
                connect_args={'check_same_thread': False}
            )
            self._session_factory = sessionmaker(bind=self._engine)
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def get_session(self) -> Session:
        """Get a database session."""
        if self._session_factory is None:
            self._initialize()
        return self._session_factory()
    
    def get_engine(self):
        """Get database engine."""
        if self._engine is None:
            self._initialize()
        return self._engine
    
    def create_tables(self):
        """Create all tables."""
        try:
            from database.models import Base
            Base.metadata.create_all(self._engine)
            logger.info("Database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            return False
    
    def drop_tables(self):
        """Drop all tables."""
        try:
            from database.models import Base
            Base.metadata.drop_all(self._engine)
            logger.info("Database tables dropped successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to drop tables: {str(e)}")
            return False

# Singleton instance
db_manager = DatabaseManager()

def get_db_session():
    """Convenience function to get database session."""
    return db_manager.get_session()

def init_db():
    """Initialize database."""
    return db_manager.create_tables()