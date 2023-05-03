""" Streams provided by the module

Apparently, the core of the service. Consider to choose streams as your architecture desicion, if you 
work with continious tasks or deal with large amount of data
"""

import asyncio
from datetime import datetime, timedelta
from typing import List
import aiostream

from pydantic import validate_arguments

from .settings import Settings

from models import Market, Task
from .models import OpenInterest, OpenInterestCandle

from .connectors import api_open_interest_history_connector


@validate_arguments
async def open_interest_history_stream(markets: List[Market],
                                       date_from: datetime,
                                       date_to: datetime) -> List[OpenInterestCandle]:
    """ Open_interest_history stream

    Args:
        markets: List of markets in "System" format
        date_from: Start of range (inclusive)
        date_to: End of range (inclusive)

    Yields:
        List[OpenInterest]
    """

    settings = Settings()

    # preparing chunks, to make asynchronious requests
    chunked_tasks_stream = aiostream.stream.chunks(
        light_task_stream(markets, date_from, date_to),
        settings.history_api_request_limit,
    )

    # making requests with assurance of exchange rate limits
    async for chunk_of_tasks in aiostream.stream.spaceout(
        chunked_tasks_stream, settings.history_api_limit_window_seconds):
        yield await asyncio.gather(*[
            api_open_interest_history_connector(task) for task in chunk_of_tasks
        ])


@validate_arguments
async def task_stream(markets: List[Market], date_from: datetime,
                      date_to: datetime, window_size: int,
                      ws_per_request: int) -> Task:
    """ Generates Task-s
        Each Task represents a single API request 

    Args:
        markets: Markets for which Task-s would be generated
        date_from: The date from which Task-s would be generated (inclusive)
        date_to: The date till which Task-s would be generated (inclusive)
        window_size: The size of quant in batch which would be returned by API (in hours)
        ws_per_request: Amount of quants returned by API

    Yields:
        Task: Task model defined in models.py
    """

    ws_to_fetch = int(
        (date_to - date_from).total_seconds()) // (window_size * 60 * 60)
    batches_to_fetch = ws_to_fetch // ws_per_request + 1

    for market in markets:
        market_tasks = [
            Task(
                market=market,
                date_from=date_to -
                timedelta(hours=window_size * ws_per_request * multiplier),
                date_to=date_to - timedelta(hours=window_size * ws_per_request *
                                            (multiplier - 1)),
            ) for multiplier in range(1, batches_to_fetch + 1)
        ]

        market_tasks[-1].date_from = market_tasks[-1].date_from if market_tasks[
            -1].date_from > date_from else date_from
        for market_task in market_tasks:
            yield market_task


@validate_arguments
async def light_task_stream(markets: List[Market], date_from: datetime,
                            date_to: datetime) -> Task:
    """ Generates Task-s 
        Each Task represents a single API request 
        (ligth version. for api without quants limit. one market = one task)

    Args:
        markets: Markets for which Task-s would be generated
        date_from: The date from which Task-s would be generated (inclusive)
        date_to: The date till which Task-s would be generated (inclusive)

    Yields:
        Task: Task model defined in models.py
    """
    for market in markets:
        yield Task(
            market=market,
            date_from=date_from,
            date_to=date_to,
        )
