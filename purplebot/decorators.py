import threading
import logging

logger = logging.getLogger(__name__)


def threaded(func):
    '''Run a bot sub command in a thread'''
    def wrapped(*args, **kwargs):
        logger.debug('Running in a thread: %s', func.__name__)
        threading.Thread(target=func, args=args, kwargs=kwargs).start()
    return wrapped

