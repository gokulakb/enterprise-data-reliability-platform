"""
Centralized logging configuration.
"""
import logging
import sys
from pathlib import Path

from config.settings import LOGGING_CONFIG

class Logger:
    """Singleton logger for the application."""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the logger with file and console handlers."""
        self._logger = logging.getLogger('EnterpriseDataReliability')
        self._logger.setLevel(getattr(logging, LOGGING_CONFIG['level']))
        
        # Create formatter
        formatter = logging.Formatter(LOGGING_CONFIG['format'])
        
        # File handler
        log_file = LOGGING_CONFIG['file']
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
    
    def get_logger(self):
        """Return the logger instance."""
        return self._logger

def get_logger():
    """Convenience function to get logger."""
    return Logger().get_logger()