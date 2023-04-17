""" Models unic for current service (dydx_price_example)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from models import MainStream
from pydantic import BaseModel


class Price(MainStream):
    """ Clickhouse model/table

    Always use MainStream as parent Class, if you want to write to main_stream
    """

    price: Decimal
    min_price: Decimal
    max_price: Decimal


class Candle(BaseModel):
    """ Candle API model

    In local Exchange format
    """

    startedAt: datetime
    updatedAt: datetime
    market: str
    resolution: str
    low: Decimal
    high: Decimal
    open: Decimal
    close: Decimal
    baseTokenVolume: Decimal
    trades: int
    usdVolume: Decimal
    startingOpenInterest: Decimal


class Market(BaseModel):
    """ Market API model

    In local Exchange format
    """

    market: str
    status: str
    baseAsset: str
    quoteAsset: str
    stepSize: Decimal
    tickSize: Optional[Decimal]
    indexPrice: Decimal
    oraclePrice: Decimal
    priceChange24H: Decimal
    nextFundingRate: Decimal
    nextFundingAt: datetime
    minOrderSize: Decimal
    type: str
    initialMarginFraction: Decimal
    maintenanceMarginFraction: Decimal
    transferMarginFraction: Decimal
    volume24H: Decimal
    trades24H: int
    openInterest: Decimal
    incrementalInitialMarginFraction: Decimal
    incrementalPositionSize: Decimal
    maxPositionSize: Decimal
    baselinePositionSize: Decimal
    assetResolution: Decimal
    syntheticAssetId: str
