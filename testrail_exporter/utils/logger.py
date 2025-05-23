import logging
import os
from datetime import datetime
from pathlib import Path


class ExportLogger:
    """Handles logging for export operations with file and console output."""
    
    def __init__(self, export_dir):
        self.export_dir = export_dir
        self.logger = logging.getLogger('testrail_exporter')
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create logs subdirectory
        logs_dir = os.path.join(export_dir, 'logs')
        
        # Create log file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f'testrail_export_log_{timestamp}.txt'
        self.log_file_path = os.path.join(logs_dir, log_filename)
        
        # Ensure logs directory exists
        Path(logs_dir).mkdir(parents=True, exist_ok=True)
        
        # File handler for detailed logging
        file_handler = logging.FileHandler(self.log_file_path, mode='w')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler for important messages
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Log initialization
        self.logger.info(f"Export logging initialized. Log file: {self.log_file_path}")
        
    def debug(self, message):
        """Log debug message."""
        self.logger.debug(message)
        
    def info(self, message):
        """Log info message."""
        self.logger.info(message)
        
    def warning(self, message):
        """Log warning message."""
        self.logger.warning(message)
        
    def error(self, message, exc_info=False):
        """Log error message with optional exception info."""
        self.logger.error(message, exc_info=exc_info)
        
    def get_log_file_path(self):
        """Return the path to the current log file."""
        return self.log_file_path
        
    def get_recent_errors(self, count=10):
        """Get the most recent error messages from the log."""
        errors = []
        try:
            with open(self.log_file_path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if 'ERROR' in line or 'WARNING' in line:
                        errors.append(line.strip())
        except Exception:
            pass
        return errors[-count:] if errors else []