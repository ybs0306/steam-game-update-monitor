import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger("SteamMonitor")
    logger.setLevel(logging.INFO)

    # * Setting log msg format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # * Use rotating method to store log
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "monitor.log"), maxBytes=1*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # * Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # * Logger adds output target
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
