""" External API Layer

Pure API requests with response Serialization and Validation. Returns models in Local Exchanges formats
"""

from datetime import datetime
from typing import List

import httpx
import structlog

from .settings import Settings

from .models import OpenInterest, OpenInterestHistoryCandle
from .models import Market

log = structlog.get_logger('external_api')


async def get_open_interest_history(
    market: str,
    date_from: datetime,
    date_to: datetime,
) -> List[OpenInterestHistoryCandle]:
    """Coinalyze Get open interest history API

    Args:
        market (str): Example: BTCUSDT_PERP.A BTCUSD_PERP.0
        date_from (datetime): The start date (inclusive)
        date_to (datetime): The end date (inclusive)

    Returns:
        List[OpenInterestHistoryCandle]:
    """
    settings = Settings()

    params = {
        'symbols': f'{market}.{settings.exchange_code}',
        'interval': '1hour',
        'from': int(datetime.timestamp(date_from)),
        'to': int(datetime.timestamp(date_to)),
        'convert_to_usd': settings.open_interest_convert_to_usd,
    }

    async with httpx.AsyncClient() as client:
        result = await client.get(
            f"{settings.history_base_path}/{settings.open_interest_history_path}",
            headers={
                'api_key': settings.coinalyze_api_key,
            },
            params={
                'symbols': f'{market}.{settings.exchange_code}',
                'interval': '1hour',
                'from': int(datetime.timestamp(date_from)),
                'to': int(datetime.timestamp(date_to)),
                'convert_to_usd': settings.open_interest_convert_to_usd,
            })
        await log.adebug(
            'api_request_finished',
            url=str(result.url),
            status_code=result.status_code,
            elapsed=result.elapsed,
            rate_limit_remaining=result.headers.get("ratelimit-remaining"),
        )

        data = result.json()

        if data:
            result = [
                OpenInterestHistoryCandle(**candlestick)
                for candlestick in data[0]['history']
            ]
            return result
        else:
            await log.adebug(f'No data found for {market}')
            return []


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
