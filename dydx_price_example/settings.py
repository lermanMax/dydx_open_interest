""" Settings unic for current Module (dydx_price_example)

Always use "env_prefix" with same name as your module
"""

from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    exchange: str = 'dydx'
    base_path: str = 'https://api.dydx.exchange/v3'

    # dYdX Rate Limits for GET: 175 requests per 10 seconds
    api_request_limit: int = 15
    api_limit_window_seconds: int = 1
    api_retry_delay_seconds: int = 3

    markets_path: str = 'markets'

    candles_path: str = 'candles'
    candles_hours_in_batch: int = 100
    candles_granularity_hours: int = 1

    class Config:
        env_prefix = 'dydx_price_example'
        env_file = '.env'
