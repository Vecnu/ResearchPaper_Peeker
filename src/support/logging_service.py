import logging
import os
import sys
from datetime import datetime
from pathlib import Path

class Logger:
    """
    Logging service for ResearchPaper_Peeker application.
    Handles logging to both console and file with different log levels.
    """
    
    _instance = None  # Singleton instance
    
    @classmethod
    def get_instance(cls):
        """Get or create singleton instance of Logger"""
        if cls._instance is None:
            try:
                cls._instance = Logger()
            except Exception as e:
                print(f"❌ Error initializing logger: {str(e)}")
                # Fallback to basic logging to console
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] - %(message)s',
                    stream=sys.stdout
                )
                logger = logging.getLogger("ResearchPaperPeeker_Fallback")
                logger.error(f"Failed to initialize logger: {str(e)}")
                
                # Create a minimal implementation
                simple_logger = SimpleLogger()
                cls._instance = simple_logger
                
        return cls._instance
    
    def __init__(self):
        """Initialize the logger"""
        if Logger._instance is not None:
            raise Exception("Logger is a singleton. Use Logger.get_instance() instead.")
        
        # Ensure logs directory exists
        try:
            logs_dir = Path("logs")
            
            # Create directory if it doesn't exist
            if not logs_dir.exists():
                print(f"Creating logs directory: {logs_dir.absolute()}")
                logs_dir.mkdir(parents=True)
            
            # Set up file paths
            self.error_log_path = logs_dir / "errors.log"
            self.app_log_path = logs_dir / "app.log"
            
            # Create empty log files if they don't exist
            if not self.error_log_path.exists():
                print(f"Creating error log file: {self.error_log_path.absolute()}")
                with open(self.error_log_path, 'w', encoding='utf-8') as f:
                    f.write(f"# ResearchPaper_Peeker Error Log - Created {datetime.now()}\n")
            
            if not self.app_log_path.exists():
                print(f"Creating application log file: {self.app_log_path.absolute()}")
                with open(self.app_log_path, 'w', encoding='utf-8') as f:
                    f.write(f"# ResearchPaper_Peeker Application Log - Created {datetime.now()}\n")
            
            # Configure root logger
            self.logger = logging.getLogger("ResearchPaperPeeker")
            self.logger.setLevel(logging.DEBUG)
            
            # Clear any existing handlers to avoid duplication
            if self.logger.handlers:
                self.logger.handlers.clear()
            
            # Create formatters
            file_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(module)s.%(funcName)s:%(lineno)d - %(message)s'
            )
            console_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] - %(message)s'
            )
            
            # Create and configure console handler (INFO level and above)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(console_formatter)
            
            # Create and configure file handlers
            # All logs go to app.log
            app_file_handler = logging.FileHandler(self.app_log_path, encoding='utf-8')
            app_file_handler.setLevel(logging.DEBUG)
            app_file_handler.setFormatter(file_formatter)
            
            # Only errors and critical logs go to errors.log
            error_file_handler = logging.FileHandler(self.error_log_path, encoding='utf-8')
            error_file_handler.setLevel(logging.ERROR)
            error_file_handler.setFormatter(file_formatter)
            
            # Add handlers to logger
            self.logger.addHandler(console_handler)
            self.logger.addHandler(app_file_handler)
            self.logger.addHandler(error_file_handler)
            
            # Test logging to verify it works
            self.info(f"Logging initialized. Logs directory: {logs_dir.absolute()}")
            self.info(f"Error log: {self.error_log_path.absolute()}")
            self.info(f"App log: {self.app_log_path.absolute()}")
            self.debug("This is a test DEBUG message")
            
            # Verify that files exist and are writable
            if not os.access(self.error_log_path, os.W_OK):
                print(f"⚠️ Warning: Error log file is not writable: {self.error_log_path}")
            if not os.access(self.app_log_path, os.W_OK):
                print(f"⚠️ Warning: App log file is not writable: {self.app_log_path}")
                
        except Exception as e:
            print(f"❌ Error setting up logger: {str(e)}")
            raise
    
    def debug(self, message):
        """Log a debug message"""
        self.logger.debug(message)
    
    def info(self, message):
        """Log an info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log a warning message"""
        self.logger.warning(message)
    
    def error(self, message, exc_info=True):
        """Log an error message, optionally with exception info"""
        self.logger.error(message, exc_info=exc_info)
        # Also print to console for immediate visibility
        print(f"❌ ERROR: {message}")
    
    def critical(self, message, exc_info=True):
        """Log a critical message, optionally with exception info"""
        self.logger.critical(message, exc_info=exc_info)
        # Also print to console for immediate visibility
        print(f"🔥 CRITICAL: {message}")
    
    def exception(self, message):
        """Log an exception message with stack trace"""
        self.logger.exception(message)
        # Also print to console for immediate visibility
        print(f"💥 EXCEPTION: {message}")


class SimpleLogger:
    """A simple fallback logger that works when the main logger fails"""
    
    def __init__(self):
        self.logger = logging.getLogger("SimpleLogger")
    
    def debug(self, message):
        print(f"[DEBUG] {message}")
    
    def info(self, message):
        print(f"[INFO] {message}")
    
    def warning(self, message):
        print(f"[WARNING] {message}")
    
    def error(self, message, exc_info=True):
        print(f"[ERROR] {message}")
        if exc_info and sys.exc_info()[0] is not None:
            import traceback
            traceback.print_exc()
    
    def critical(self, message, exc_info=True):
        print(f"[CRITICAL] {message}")
        if exc_info and sys.exc_info()[0] is not None:
            import traceback
            traceback.print_exc()
    
    def exception(self, message):
        print(f"[EXCEPTION] {message}")
        import traceback
        traceback.print_exc()
