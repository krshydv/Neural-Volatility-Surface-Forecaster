import logging
import sys


def configure_logging(environment: str) -> None:
    log_level = logging.DEBUG if environment == "development" else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
