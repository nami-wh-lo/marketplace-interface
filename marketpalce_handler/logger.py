import logging

_log_format = (
    "%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%("
    "funcName)s(%(lineno)d) - %(message)s "
)


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler


def get_logger():
    logger = logging.getLogger(__name__)
    logger.addHandler(get_stream_handler())
    logger.setLevel(logging.DEBUG)
    return logger
