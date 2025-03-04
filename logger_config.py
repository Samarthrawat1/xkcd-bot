"""
Logger configuration module for XKCD Bot.
Provides colorful logging with both console and file output.
"""

import os
import logging
import colorlog
from datetime import datetime

def setup_logger(name: str = 'xkcd_bot', log_to_file: bool = True) -> logging.Logger:
    """
    Configure and return a logger instance with color formatting and optional file output.
    
    Args:
        name (str): Name of the logger instance
        log_to_file (bool): Whether to also log to a file
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = colorlog.getLogger(name)
    logger.setLevel(logging.INFO)
    
    logger.handlers = []
    
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s [%(levelname)s] %(message)s%(reset)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bold',
        }
    ))
    logger.addHandler(console_handler)
    
    if log_to_file:
        os.makedirs('logs', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = f'logs/xkcd_bot_{timestamp}.log'
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logger.addHandler(file_handler)
        logger.info(f"Logging to file: {log_file}")
    
    return logger

logger = setup_logger()

def get_logger(name: str = 'xkcd_bot') -> logging.Logger:
    """Get or create a logger instance with the given name."""
    return logging.getLogger(name) 