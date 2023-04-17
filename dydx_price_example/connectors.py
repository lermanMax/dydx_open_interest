""" Layer between API and stream

Usually responsible for data transformation. Serialized + Validated data in local exchange format INcoming, 
and Data in "System Format" ready for stream consumers OUTgoing

Also contents retry policies, if API request was unsuccessful
"""

from datetime import datetime, timedelta
from typing import List

from .settings import Settings

from models import Task
from .models import Price, Candle

from utils import api_connector
from . import external_api as api


@api_connector(retry_delay=3)
async def api_price_connector(task: Task) -> List[Price]:
    settings = Settings()
    candles_batch = await api.get_candles_for_market(
        task.market.local_name,
        task.date_from,
        task.date_to,
    )

    result = []
    for model in candles_batch:
        model: Candle

        # Hack for collecting price data in main_stream (needed only for this particular scenario)
        # When we recieve Candle, the last one is incomplete (because hour is just started)
        # So we use the previous one as the reference
        date = model.startedAt + timedelta(hours=1)

        result.append(
            Price(
                datetime=date,
                timestamp=datetime.timestamp(date),
                exchange=settings.exchange,
                market=task.market.name,
                price=model.close,
                max_price=model.high,
                min_price=model.low,
            ))

    return result
