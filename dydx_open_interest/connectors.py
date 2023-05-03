""" Layer between API and stream

Usually responsible for data transformation. Serialized + Validated data in local exchange format INcoming, 
and Data in "System Format" ready for stream consumers OUTgoing

Also contents retry policies, if API request was unsuccessful
"""

from datetime import datetime, timedelta, timezone
from typing import List

from .settings import Settings

from models import Task, Market
from .models import OpenInterestHistoryCandle, OpenInterest, OpenInterestCandle

from utils import api_connector
from . import external_api as api


@api_connector(retry_delay=3)
async def api_open_interest_history_connector(task: Task) -> List[OpenInterestCandle]:
    settings = Settings()
    candles = await api.get_open_interest_history(
        task.market.local_name,
        task.date_from,
        task.date_to,
    )

    result = []
    for entry in candles:
        entry: OpenInterestHistoryCandle
        # UNIX timestamp in seconds (entry.t) to datetime object
        _datetime = datetime.utcfromtimestamp(
            entry.t).replace(tzinfo=timezone.utc)

        result.append(
            OpenInterestCandle(
                datetime=_datetime,
                timestamp=entry.t,
                exchange=settings.exchange,
                market=task.market.local_name,
                open=entry.o,
                high=entry.h,
                low=entry.l,
                close=entry.c,
            ))
    return result


@api_connector(retry_delay=3)
async def api_open_interest_now_connector() -> List[OpenInterest]:
    """get open intererst for all markets in this moment

    Returns:
        List[OpenInterest]
    """
    settings = Settings()
    _datetime = datetime.now(tz=timezone.utc)
    _timestamp = int(datetime.timestamp(_datetime))
    local_markets: List[Market] = await api.get_markets()

    result = []
    for local_market in local_markets:
        result.append(
            OpenInterest(
                datetime=_datetime,
                timestamp=_timestamp,
                exchange=settings.exchange,
                market=local_market.market,
                open=local_market.openInterest,
            ))
    return result
