from __future__ import annotations

import logging
from typing import List, Union, Any

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logger(level: Union[str, int] = "INFO", ignored: List[str] | None = None):
    logging.basicConfig(filename="logfile.log", filemode="w", level=logging.getLevelName(level))
    # logging.basicConfig(handlers=[InterceptHandler()], level=logging.getLevelName(level))
    if ignored:
        for ignore in ignored:
            logger.disable(ignore)
    logging.info("Logging is successfully configured")


def log_handler(handler_name: str, user_id, state: Any):
    if state:
        logging.info(f"Start [{handler_name}] handler for user [{user_id}] with state [{state}]")
    else:
        logging.info(f"Start [{handler_name}] handler for user [{user_id}]")

