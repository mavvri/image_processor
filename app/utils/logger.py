import logging
import os
import sys
from datetime import datetime
from typing import Optional

# Create a simple fallback logger that works in all cases
class SimpleLogger:
    """Simple logger implementation that always works."""
    
    def __init__(self):
        self.logger = logging.getLogger("CarCounter")
        if not self.logger.handlers:
            # Setup simple console handler
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.WARNING)
            formatter = logging.Formatter('%(levelname)s: %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.DEBUG)
    
    def debug(self, message, **kwargs):
        """Log debug information."""
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            full_message = f"{message} | {context}"
        else:
            full_message = message
        self.logger.debug(full_message)
    
    def info(self, message, **kwargs):
        """Log informational messages."""
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            full_message = f"{message} | {context}"
        else:
            full_message = message
        self.logger.info(full_message)
    
    def warning(self, message, **kwargs):
        """Log warning messages."""
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            full_message = f"{message} | {context}"
        else:
            full_message = message
        self.logger.warning(full_message)
    
    def error(self, message, **kwargs):
        """Log error messages."""
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            full_message = f"{message} | {context}"
        else:
            full_message = message
        self.logger.error(full_message)
    
    def log_ui_action(self, action, component, **kwargs):
        """Log UI actions."""
        self.debug(f"UI Action: {action} - Component: {component}", **kwargs)
    
    def log_processing_step(self, step_name, step_index, success=True, **kwargs):
        """Log processing steps."""
        status = "SUCCESS" if success else "FAILED"
        self.info(f"Step [{step_index}] {step_name}: {status}", **kwargs)

# Create global logger instance
logger = SimpleLogger()
