from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Optional

import structlog
import pytest
from pydantic import BaseModel

from dydx_price_example.settings import Settings
from dydx_price_example.streams import price_stream
from dydx_price_example.actions import get_markets

log = structlog.get_logger('test')


@pytest.mark.asyncio
async def test_price_stream():
    """ Test dydx_price_example.stream.chunked_stream

    Assurances:
        1) Stream yields List[List[Price]]
        2) Result stream equal or more than provided range

    """

    date_to = datetime.now(tz=timezone.utc)
    date_to = date_to.replace(minute=0, second=0, microsecond=0)
    date_from = date_to - timedelta(days=5)

    markets = await get_markets()

    class Analytics(BaseModel):
        market: str
        count: int = 0
        first_date: Optional[datetime]
        last_date: Optional[datetime]

    analytics = {
        market.name: Analytics(market=market.name) for market in markets
    }

    async for prices_chunk in price_stream(markets, date_from, date_to):
        for prices_batch in prices_chunk:
            for price in prices_batch:
                analytics[price.market].count += 1
                analytics[
                    price.market].first_date = price.datetime if analytics[
                        price.market].first_date is None else min(
                            price.datetime, analytics[price.market].first_date)
                analytics[price.market].last_date = price.datetime if analytics[
                    price.market].last_date is None else max(
                        price.datetime, analytics[price.market].last_date)

    for market_name in analytics.keys():
        assert analytics[market_name].first_date <= date_from
        assert analytics[market_name].last_date >= date_to
        assert analytics[market_name].count * 100 >= (
            analytics[market_name].last_date -
            analytics[market_name].first_date).total_seconds() // 3600
