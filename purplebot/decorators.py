import threading
import logging

logger = logging.getLogger(__name__)


def threaded(func):
    def wrapped(*args, **kwargs):
        logger.debug('Running in a thread: %s', func.__name__)
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        #return func(*args, **kwargs)
    return wrapped
