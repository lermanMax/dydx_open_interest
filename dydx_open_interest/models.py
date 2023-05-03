""" Models unic for current service
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Union

from models import MainStream
from pydantic import BaseModel


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


class OpenInterestCandle(MainStream):
    """ Clickhouse model/table
    """

    open: Decimal
    high: Union[Decimal, None]
    low: Union[Decimal, None]
    close: Union[Decimal, None]


class OpenInterest(MainStream):
    """ Clickhouse model/table
    """

    open: Decimal


class OpenInterestHistoryCandle(BaseModel):
    """ 
    t	integer <int64> The beginning of the interval, UNIX timestamp in seconds
    o   number <double> Open
    h	number <double> High
    l	number <double> Low
    c	number <double> Close
    """

    t: int
    l: Decimal
    h: Decimal
    o: Decimal
    c: Decimal
