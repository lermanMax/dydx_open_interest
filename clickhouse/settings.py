from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    logging: str = "WARNING"

    host: str
    port: int = 8123
    username: str = "default"
    password: SecretStr = ""

    sync_period_seconds: int = 1
    batch_size: int = 10000

    class Config:
        env_prefix = 'clickhouse_'
        env_file = '.env'
