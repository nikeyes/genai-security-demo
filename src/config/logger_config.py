import logging


def setup_logger(name: str, debug: bool = False) -> logging.Logger:
    """
    Configure and return a logger with consistent settings.

    Args:
        name (str): Logger name, typically __name__ from the calling module
        debug (bool): Enable debug level logging if True

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers if they already exist
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        log_level = logging.DEBUG if debug else logging.INFO
        logger.setLevel(log_level)
        console_handler.setLevel(log_level)

    return logger
