import json
import logging

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def get_logger(log_file: str, log_level: int = logging.INFO, log_format: str = None) -> logging.Logger:
    """
    Create a logger

    Args:
        log_file (str): log file path
        log_level (int): log level(default=INFO)
        log_format (str): log format

    Returns:
        logging.Logger: logger object
    """
    # set up default log format
    if log_format is None:
        log_format = '%(message)s'
    
    # set up logger name
    logger_name = f"logger_{log_file}"
    logger = logging.getLogger(logger_name)
    
    if not logger.hasHandlers():
        logger.setLevel(log_level)
        # set up file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
        # set up stream handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(console_handler)
    
    return logger


