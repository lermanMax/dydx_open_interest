""" Global Models

Usually refer to them as "System" format
"""

from datetime import datetime

from pydantic import BaseModel
from pydantic import validator


class Market(BaseModel):
    """ Market model

    Use this model as main Market model in DTO in all services
    """

    exchange: str
    local_name: str

    name: str
    base: str
    quote: str


class Task(BaseModel):
    """ Task model

    Model for the Stream of Tasks
    Use this model as main Task model in DTO in all services
    """

    market: Market
    date_from: datetime
    date_to: datetime


class MainStream(BaseModel):
    """ Main Stream model

    Base model for writing data in Clickhouse main_stream
    Use this model as parent for your data models, which you plan to insert
    in "main_stream", in all services
    """

    datetime: datetime
    timestamp: int
    exchange: str
    market: str

    @validator('datetime')
    def name_must_contain_space(cls, v: datetime):
        clean_date = v.replace(minute=0, second=0, microsecond=0)
        return clean_date

    class Config:
        primary_key: str = '(exchange, market, datetime)'
        ttl: str = 'datetime + INTERVAL 12 month'
        engine: str = 'MergeTree'
