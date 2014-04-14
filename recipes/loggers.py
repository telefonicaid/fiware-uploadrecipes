import logging


def init_log():
    """
    Define the logger.
    """
    logging.basicConfig(filename='recipes.log',
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%d/%m/%Y-%H:%M:%S', level=logging.DEBUG)


def set_info_log(msg):
    """
    Info log msg
    @param msg: Text msg to save
    """
    logging.info(msg)


def set_error_log(msg):
    """
    Error log msg
    @param msg: Text msg to save
    """
    logging.error(msg)


def set_warning_log(msg):
    """
    Warning log msg
    @param msg: Text msg to save
    """
    logging.warning(msg)


def set_debug_log(msg):
    """
    Debug log msg
    @param msg: Text msg to save
    """
    logging.debug(msg)
