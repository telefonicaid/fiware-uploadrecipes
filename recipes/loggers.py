import logging


def init_log():
    logging.basicConfig(filename='recipes.log',
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%d/%m/%Y-%H:%M:%S', level=logging.DEBUG)


def set_info_log(msg):
    logging.info(msg)


def set_error_log(msg):
    logging.error(msg)


def set_warning_log(msg):
    logging.warning(msg)


def set_debug_log(msg):
    logging.debug(msg)
