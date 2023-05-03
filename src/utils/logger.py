import logging
from pprint import pformat


def setup_logging(filename):
    stream_handler = logging.StreamHandler()
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(
        filename=filename,
        filemode="a",
        level=logging.INFO,
        format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt="%d-%m-%y %H:%M:%S",
    )
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s", "%d-%m-%y %H:%M:%S")
    )
    logging.getLogger().addHandler(stream_handler)


def setup_logging_display_only():
    stream_handler = logging.StreamHandler()
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%d-%m-%y %H:%M:%S",
    )
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s", "%d-%m-%y %H:%M:%S")
    )
    logging.getLogger().addHandler(stream_handler)


def pprint(obj):
    logging.info(pformat(obj, indent=4))

def print(*obj):
    message = " ".join([str(o) for o in obj])
    logging.info(message)