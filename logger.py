import logging
from logging.handlers import RotatingFileHandler


def setup_logging(
        filename: str = "./data/logs/bot.log",
        backup_count: int = 5,
        max_bytes: int = 5*1024*1024):

    # Configure logging with file rotation
    log_formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s')
    log_handler = RotatingFileHandler(
        filename, maxBytes=max_bytes, backupCount=backup_count)
    log_handler.setFormatter(log_formatter)
    log_handler.setLevel(logging.INFO)

    # Get the root logger and set its handler to the RotatingFileHandler
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(log_handler)
