import logging.config as config


LOG_FORMAT = "%(asctime)s.%(msecs)03d %(levelname)-8s %(name)s  %(message)s"
LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": LOG_FORMAT,
            "datefmt": LOG_DATEFMT,
        },
    },
    "handlers": {
        "default": {
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
    "root": {
        "handlers": ["default"],
        "level": "INFO",
    },
}


def configure_logging() -> None:
    config.dictConfig(LOGGING_CONFIG)
