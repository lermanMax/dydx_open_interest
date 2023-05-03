from datetime import datetime
from datetime import timedelta
from datetime import timezone

from typing import Optional

import pytest
from pydantic import BaseModel

from models import Task

from dydx_open_interest.streams import task_stream
from dydx_open_interest.actions import get_markets


@pytest.mark.asyncio
async def test_task_stream():
    """ Test dydx_price_example.actions.task_stream

    Assurances:
        1) Stream yields Task-s
        2) Result stream equal or more than provided range
    """

    date_to = datetime.now(tz=timezone.utc)
    date_to = date_to.replace(minute=0, second=0, microsecond=0)
    date_from = date_to - timedelta(days=50)

    markets = await get_markets()

    class Analytics(BaseModel):
        count: int = 0
        first_date: Optional[datetime]
        last_date: Optional[datetime]

    analytics = {market.name: Analytics() for market in markets}
    async for task in task_stream(markets, date_from, date_to, 1, 100):
        assert isinstance(task, Task)

        analytics[task.market.name].count += 1
        analytics[task.market.name].first_date = task.date_from if analytics[
            task.market.name].first_date is None else min(
                task.date_from, analytics[task.market.name].first_date)
        analytics[task.market.name].last_date = task.date_to if analytics[
            task.market.name].last_date is None else max(
                task.date_to, analytics[task.market.name].last_date)

    for market_name in analytics.keys():
        assert analytics[market_name].first_date <= date_from
        assert analytics[market_name].last_date >= date_to
        assert analytics[market_name].count * 100 >= (
            analytics[market_name].last_date -
            analytics[market_name].first_date).total_seconds() // 3600
