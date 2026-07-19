"""
Database table creation script.
"""
from database.database import db_manager
from utils.logger import get_logger

logger = get_logger()

def init_database():
    """Initialize database tables."""
    try:
        # Import models to ensure they're registered
        from database import models
        
        # Create tables
        success = db_manager.create_tables()
        
        if success:
            logger.info("Database tables initialized successfully")
            return True
        else:
            logger.error("Failed to initialize database tables")
            return False
            
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False

if __name__ == "__main__":
    init_database()