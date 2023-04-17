""" Actions/API Implementation of the service

If service is small enough, it's better to locate all actions in one file. If file becomes too big,
you'll better to consider to get rid of actions module, in favour of multiple modules. And then
import actions from them in __init__.py 

But if you do so, may be it's the point to think about a separate service
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import List

import clickhouse

from settings import Settings as MainSettings
from .settings import Settings

from models import Market
from .models import Market as LocalMarket, Price

from .streams import price_stream
from . import external_api as api

from utils import default_stream_config


async def get_markets() -> List[Market]:
    """ Returns list of Exchange markets in "System" format

    Returns:
        List[Market]
    """

    settings = Settings()
    local_markets: List[LocalMarket] = await api.get_markets()

    markets: List[Market] = []
    for local_market in local_markets:
        markets.append(
            Market(
                exchange=settings.exchange,
                local_name=local_market.market,
                name=f'{local_market.baseAsset}{local_market.quoteAsset}T',
                base=local_market.baseAsset,
                quote=f'{local_market.quoteAsset}',
            ))

    return markets


@default_stream_config(get_markets)
async def load_price(markets: List[Market], date_from: datetime,
                     date_to: datetime) -> None:
    """ Gets market prices in selected range

    Args:
        markets: List of markets in "System" format
        date_from: Start of range (inclusive)
        date_to: End of range (inclusive)
    """

    main_settings = MainSettings()
    async with clickhouse.Client(main_settings.main_stream,
                                 Price) as clickhouse_client:
        async for results in price_stream(markets, date_from, date_to):
            for models in results:
                for model in models:
                    if model.datetime >= date_from and model.datetime <= date_to:
                        await clickhouse_client.insert(model)


@default_stream_config(get_markets)
async def load_price_now(markets: List[Market], *args) -> None:
    """ Load current price

    Gets current market prices from API, and writes them to Clickhouse
    The shortcut for "load_price" func with required params

    Args:
        markets: List of markets in "System" format
    """

    date_to = datetime.now(tz=timezone.utc)
    date_from = date_to - timedelta(hours=1)

    await load_price(markets, date_from, date_to)


def aws_lambda(event, context) -> None:
    """ Function to invoke by AWS Lambda

    Loads current price

    Args:
        event: AWS Event
        context: AWS Context
    """

    asyncio.run(load_price_now())
