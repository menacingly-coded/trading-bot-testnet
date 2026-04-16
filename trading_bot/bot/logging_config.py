from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_dir: str = "logs", log_file: str = "trading_bot.log") -> Path:
    """
    Configure app logging to a rotating file + console.
    Returns the log file path.
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_path = Path(log_dir) / log_file

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if setup_logging is called twice.
    if logger.handlers:
        return log_path

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(log_path, maxBytes=2_000_000, backupCount=3)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(fmt)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console)

    return log_path