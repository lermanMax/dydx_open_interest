""" Testing Actions

Assuarance that all service "API" works as expected
"""

from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest

import clickhouse

from settings import Settings
import models
import dydx_price_example.models as service_models

import dydx_price_example.actions as actions


@pytest.mark.asyncio
async def test_get_markets():
    """ Test dydx_price_example.actions.get_markets

    Assurances:
        1) Func returns List[Market]
        2) List is not empty
    """

    markets = await actions.get_markets()

    assert isinstance(markets, list)
    assert len(markets) > 0
    assert isinstance(markets[0], models.Market)


@pytest.mark.asyncio
async def test_load_price_main():
    """ Test dydx_price_example.actions.load_price

    We verify here only that action doe not fail
    Data consistancy in data base we verify by Dashboards and alerts in other service

    Assurances:
        Does not fail
    """

    settings = Settings()

    date_to = datetime.now(tz=timezone.utc)
    date_to = date_to.replace(minute=0, second=0, microsecond=0)
    date_from = date_to - timedelta(days=5)

    markets = await actions.get_markets()

    clickhouse.command(f'DROP TABLE IF EXISTS {settings.main_stream}')
    clickhouse.create_table(settings.main_stream, service_models.Price)

    await actions.load_price(markets, date_from, date_to)


@pytest.mark.asyncio
async def test_load_price_now():
    """ Test dydx_price_example.actions.load_price_now
    
    We verify here only that action doe not fail
    Data consistancy in data base we verify by Dashboards and alerts in other service

    Assurances:
        Does not fail
    """

    settings = Settings()

    clickhouse.command(f'DROP TABLE IF EXISTS {settings.main_stream}')
    clickhouse.create_table(settings.main_stream, service_models.Price)

    await actions.load_price_now()


def test_aws_lambda():
    """ Test dydx_price_example.actions.load_price

    We verify here only that action doe not fail
    Data consistancy in data base we verify by Dashboards and alerts in other service

    Assurances:
        Does not fail
    """

    settings = Settings()

    clickhouse.command(f'DROP TABLE IF EXISTS {settings.main_stream}')
    clickhouse.create_table(settings.main_stream, service_models.Price)

    actions.aws_lambda(None, None)
