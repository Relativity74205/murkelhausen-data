import logging
from logging.config import dictConfig

from murkelhausen.config import config
from murkelhausen.util.misc import run_once

log = logging.getLogger(__name__)

ONELINE_FORMATTER = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


@run_once
def setup_logging():
    """Set up basic logging to stdout."""
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "oneline": {"format": ONELINE_FORMATTER},
            },
            "handlers": {
                "console": {
                    "level": config.app.loglevel,
                    "formatter": "oneline",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "murkelhausen": {
                    "handlers": ["console"],
                    "level": config.app.loglevel,
                    "propagate": False,
                },
            },
        }
    )
    log.info("Logger configuration set up successfully.")
