import os
import logging
import logging.config
from pathlib import Path
from datetime import datetime

from logging.handlers import TimedRotatingFileHandler

### APPLICATION LOGGING CONFIGURATION ### 
PATH = "./misc/logs"
LOG_DIR = Path(PATH)
LOG_DIR.mkdir(exist_ok=True)


# handler = TimedRotatingFileHandler(
#     os.path.join(PATH, f"log_{datetime.now()}"),
#     when='midnight',  # 'midnight', 'D', 'W0', 'W1', etc.
#     interval=1,
#     backupCount=7
# )

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        }
    },
    "handlers": {
        'timed_file_handler': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'default',
            'filename': os.path.join(PATH, f"log_{datetime.now().strftime("%d-%m-%Y")}"),
            'when': 'midnight',  # Rotate at midnight
            'interval': 1,       # Rotate every day
            'backupCount': 7,    # Keep 7 backup files
            'encoding': 'utf8',
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default"
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["timed_file_handler", "console"]
    }
}

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
    logging.getLogger("telethon").setLevel(logging.WARNING)

