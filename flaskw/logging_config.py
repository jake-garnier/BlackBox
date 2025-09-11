"""
Logging configuration for BlackBox application.
"""
import logging
import logging.config
import os
from datetime import datetime

def setup_logging(app):
    """Configure logging for the Flask application."""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Logging configuration
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            },
            'detailed': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s (%(filename)s:%(lineno)d): %(message)s',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'default',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'detailed',
                'filename': 'logs/blackbox.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': 'logs/blackbox_errors.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        },
        'loggers': {
            'flaskw': {
                'level': 'INFO',
                'handlers': ['console', 'file', 'error_file'],
                'propagate': False
            },
            'werkzeug': {
                'level': 'WARNING',
                'handlers': ['console', 'file'],
                'propagate': False
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console', 'file']
        }
    }
    
    # Set logging level based on environment
    if app.config.get('DEBUG'):
        logging_config['loggers']['flaskw']['level'] = 'DEBUG'
        logging_config['handlers']['console']['level'] = 'DEBUG'
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Set up Flask's logger
    app.logger.setLevel(logging.INFO)
    
    # Log application startup
    app.logger.info('BlackBox application started')
    
    return logging.getLogger('flaskw')