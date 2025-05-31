import src.config as cfg 

import logging

def setup_logger(
	name: str, 
	level: int,
	format: str
) -> logging.Logger:
	logger = logging.getLogger(name)
	logger.setLevel(level)
	if not logger.handlers:
		formatter = logging.Formatter(format)
		handler = logging.StreamHandler()
		handler.setLevel(level)
		handler.setFormatter(formatter)
		logger.addHandler(handler)
	return logger

logger = setup_logger(
	__name__, 
	cfg.settings.LOGGING_LEVEL,
	cfg.settings.LOGGING_FORMAT
)
logger.debug("Logger initialized for %s", __name__)