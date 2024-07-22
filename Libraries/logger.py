import logging
from datetime import datetime
import os

log_format = f"%(asctime)s - [%(levelname)s] - %(message)s"


def get_file_handler():
    now = datetime.now()
    output_dir = "Outputs"
    os.makedirs(output_dir, exist_ok=True)
    file_handler = logging.FileHandler(
        f"{output_dir}/log-{now.strftime('%d-%m')}.log", encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format))
    return file_handler


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(log_format))
    return stream_handler


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_file_handler())
    logger.addHandler(get_stream_handler())
    return logger
