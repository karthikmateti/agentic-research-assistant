import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from backend.config.settings import PROJECT_ROOT, get_settings


def get_logger(name: str) -> logging.Logger:
    settings = get_settings()
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / "application.log"

    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level.upper())

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        file_handler = RotatingFileHandler(
            log_path, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger
