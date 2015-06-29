import os
import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

if 'SENTRY_DSN' in os.environ:
    try:
        from raven.conf import setup_logging
        from raven.handlers.logging import SentryHandler
        setup_logging(
            SentryHandler(os.environ['SENTRY_DSN'], level=logging.WARNING)
        )
        logger.info('Enabled sentry')
    except (ImportError, KeyError):
        logger.warning('Error importing Sentry')
