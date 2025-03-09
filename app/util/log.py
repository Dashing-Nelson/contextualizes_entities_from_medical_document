import logging

from pythonjsonlogger.json import JsonFormatter

# Configure Logger
logger = logging.getLogger("app-logger")

# Prevent adding multiple handlers (important when importing across files)
if not logger.handlers:
    log_handler = logging.StreamHandler()

    # Define JSON Formatter
    formatter = JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s"
    )

    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    # Optional: Write logs to a file
    file_handler = logging.FileHandler("app.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def set_log_level(level):
    logger.setLevel(level)
