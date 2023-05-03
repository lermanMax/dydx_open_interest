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
from .models import Market as LocalMarket, OpenInterest, OpenInterestCandle

from . import external_api as api
from . import connectors
from .streams import open_interest_history_stream


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


async def load_open_interest(date_from: str, date_to: str) -> None:
    """ Gets open interest in selected range for all markets

    Args:
        date_from (ISO string): Start of range (inclusive) 
        date_to (ISO string): End of range (inclusive) 
    """
    # transform ISO date str to datetime object
    date_from = datetime.strptime(date_from, '%Y-%m-%dT%H:%M:%S.%fZ')
    date_to = datetime.strptime(date_to, '%Y-%m-%dT%H:%M:%S.%fZ')

    await load_open_interest_history(date_from, date_to)


async def load_open_interest_history(date_from: datetime,
                                     date_to: datetime) -> None:
    """ Gets open interest in selected range for all markets

    Args:
        date_from: Start of range (inclusive)
        date_to: End of range (inclusive)
    """

    main_settings = MainSettings()
    markets = await get_markets()

    async with clickhouse.Client(main_settings.main_stream,
                                 OpenInterestCandle) as clickhouse_client:
        async for results in open_interest_history_stream(
                markets, date_from, date_to):
            for models in results:
                for model in models:
                    if date_from <= model.datetime <= date_to:
                        await clickhouse_client.insert(model)


async def load_open_interest_now() -> None:
    """ Gets open interest in selected range for all markets
    """
    main_settings = MainSettings()

    async with clickhouse.Client(main_settings.main_stream,
                                 OpenInterest) as clickhouse_client:
        for model in await connectors.api_open_interest_now_connector():
            await clickhouse_client.insert(model)


def aws_lambda(event, context) -> None:
    """ Function to invoke by AWS Lambda

    Loads current price

    Args:
        event: AWS Event
        context: AWS Context
    """

    asyncio.run(load_open_interest_now())
