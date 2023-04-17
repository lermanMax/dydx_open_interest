""" Global Settings
"""

from pydantic import BaseSettings


class Settings(BaseSettings):
    log_level: str = "WARNING"
    log_format: str = "JSON"

    main_stream: str

    class Config:
        env_file = '.env'