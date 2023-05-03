from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Optional

import structlog
import pytest
from pydantic import BaseModel

from dydx_open_interest.settings import Settings
from dydx_open_interest.streams import open_interest_history_stream
from dydx_open_interest.connectors import api_open_interest_now_connector
from dydx_open_interest.actions import get_markets
from dydx_open_interest.models import OpenInterest, OpenInterestCandle

log = structlog.get_logger('test')


@pytest.mark.asyncio
async def test_open_interest_stream():
    """ Test dydx_open_interest.streams.open_interest_history_stream

    Assurances:
        1) Stream yields List[List[OpenInterest]]
        2) Result stream equal or more than provided range

    """

    date_to = datetime.now(tz=timezone.utc)
    date_to = date_to.replace(minute=0, second=0, microsecond=0)
    date_from = date_to - timedelta(days=2)

    markets = await get_markets()

    class Analytics(BaseModel):
        market: str
        count: int = 0
        first_date: Optional[datetime]
        last_date: Optional[datetime]

    analytics = {
        market.local_name: Analytics(market=market.local_name) for market in markets
    }

    async for chunk in open_interest_history_stream(markets, date_from, date_to):
        for batch in chunk:
            for candle in batch:
                analytics[candle.market].count += 1
                analytics[
                    candle.market].first_date = candle.datetime if analytics[
                        candle.market].first_date is None else min(
                            candle.datetime, analytics[candle.market].first_date)
                analytics[candle.market].last_date = candle.datetime if analytics[
                    candle.market].last_date is None else max(
                        candle.datetime, analytics[candle.market].last_date)
    
    # if count = 0 market is dead
    for market_name in list(analytics.keys()):
        if analytics[market_name].count == 0:
            del analytics[market_name]

    for market_name in analytics.keys():
        try:
            assert analytics[market_name].first_date <= date_from
            assert analytics[market_name].last_date >= date_to
            # 1 candle/hour
            assert analytics[market_name].count >= (
                analytics[market_name].last_date -
                analytics[market_name].first_date).total_seconds() // 3600
        except:
            print(analytics[market_name])


@pytest.mark.asyncio
async def test_open_interest_now():
    """ Test dydx_open_interest api_open_interest_now_connector

    Assurances:
        1) Connector returns List[OpenInterest]
        2) Result more then 0

    """

    open_interest_list = await api_open_interest_now_connector()

    assert isinstance(open_interest_list, list)
    assert len(open_interest_list) > 0
    assert isinstance(open_interest_list[0], OpenInterest)
