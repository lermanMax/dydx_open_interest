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

    # Coinalyze API is using for geting historical data
    history_base_path: str = 'https://api.coinalyze.net/v1'
    exchange_code = '8'
    coinalyze_api_key: str

    # Coinalyze API Rate limit: 40 API calls per minute per API Key
    history_api_request_limit: int = 2
    history_api_limit_window_seconds: int = 3
    history_api_retry_delay_seconds: int = 3

    open_interest_history_path = 'open-interest-history'
    open_interest_convert_to_usd = 'false'

    class Config:
        env_prefix = 'dydx_open_interest_'
        env_file = '.env'
