import asyncio
from datetime import datetime, timedelta, timezone
import functools
from typing import List
import logging

import structlog

from settings import Settings
from models import Market

log = structlog.get_logger('utils')


def api_connector(retry_delay: int):
    """ Continiously resends a request if it fails

    Sometimes request could fail. If we do some long living load of data, we dont want to stop this load.
    Resending request usually works well.
    
    As we use lambdas for computations, and if the logic results in infinity loop, lambdas time restrictions
    wont allow us to do this forever. They will stop execution after some amount of time. So we don't care
    of such type os situstions

    Args:
        retry_delay: How long to sleep, if request fails (in seconds)
    """

    def wrapper(func):

        @functools.wraps(func)
        async def wrapped(*args):
            while True:
                try:
                    return await func(*args)
                except Exception as e:
                    await log.awarning('api_request_error', exc_info=e)
                    await asyncio.sleep(retry_delay)

        return wrapped

    return wrapper


def default_stream_config(get_markets):
    """ Decorator to retrieve default params

    Args:
        get_markets: Function to retrieve markets (should return List[Market] in "System" format)
    """

    def wrapper(func):

        @functools.wraps(func)
        async def wrapped(markets: List[Market] = None,
                          date_from: datetime = None,
                          date_to: datetime = None):
            if markets is None:
                markets = await get_markets()
            if date_from is None or date_to is None:
                date_to = datetime.now(tz=timezone.utc)
                date_from = date_to - timedelta(days=365)

            return await func(markets, date_from, date_to)

        return wrapped

    return wrapper


def configure_structlog():
    """ Default Logging configuration

    """
    settings = Settings()

    log_level = getattr(logging, settings.log_level)
    processors = [
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.log_format == "JSON":
        processors += [structlog.processors.JSONRenderer()]
    else:
        processors += [structlog.dev.ConsoleRenderer()]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False)
