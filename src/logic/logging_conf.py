import logging
import logging.config
from pathlib import Path
from datetime import datetime


### APPLICATION LOGGING CONFIGURATION ### 
LOG_DIR = Path("./misc/logs")
LOG_DIR.mkdir(exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        }
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": LOG_DIR / f"app_{datetime.now().strftime('%Y-%m-%d')}.log",
            "formatter": "default",
            "encoding": "utf-8"
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default"
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["file", "console"]
    }
}

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)
    logging.getLogger("telethon").setLevel(logging.WARNING)

