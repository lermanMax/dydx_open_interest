""" External API Layer

Pure API requests with response Serialization and Validation. Returns models in Local Exchanges formats
"""

from datetime import datetime
from typing import List

import httpx
import structlog

from .settings import Settings

from .models import Candle
from .models import Market

log = structlog.get_logger('external_api')


async def get_candles_for_market(market: str,
                                 date_from: datetime,
                                 date_to: datetime,
                                 limit: int = 100) -> List[Candle]:
    """ dYdX Candles API

    Args:
        market: Market name in local format
        date_from: The start date (inclusive)
        date_to: The end date (inclusive)
        limit: Amount of quants in response. Defaults to 100.

    Returns:
        List[Candle]
    """

    settings = Settings()

    async with httpx.AsyncClient() as client:
        result = await client.get(
            f"{settings.base_path}/{settings.candles_path}/{market}",
            params={
                'resolution': '1HOUR',
                'fromISO': date_from.isoformat(),
                'toISO': date_to.isoformat(),
                'limit': limit
            })
        await log.adebug(
            'api_request_finished',
            url=str(result.url),
            status_code=result.status_code,
            elapsed=result.elapsed,
            rate_limit_remaining=result.headers.get("ratelimit-remaining"),
        )

        data = result.json()
        candles = [Candle(**funding_data) for funding_data in data['candles']]

        return candles


async def get_markets() -> List[Market]:
    """ dYdX markets API

    Returns:
        List[Market]: Markets in local Exchange format
    """

    settings = Settings()
    async with httpx.AsyncClient() as client:
        result = await client.get(
            f'{settings.base_path}/{settings.markets_path}')
        await log.adebug(
            'api_request_finished',
            url=str(result.url),
            status_code=result.status_code,
            elapsed=result.elapsed,
            rate_limit_remaining=result.headers.get("ratelimit-remaining"),
        )

        markets = []
        for _, market_data in result.json()["markets"].items():
            markets.append(Market(**market_data))

        return markets
