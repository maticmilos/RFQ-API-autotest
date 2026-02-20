import logging


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_request(logger: logging.Logger, method: str, url: str):
    """Log outgoing HTTP request."""
    logger.info(f"Sending {method} request to {url}")


def log_response(logger: logging.Logger, status_code: int, response_time: float):
    """Log HTTP response."""
    logger.info(f"Received response: {status_code} ({response_time:.3f}s)")