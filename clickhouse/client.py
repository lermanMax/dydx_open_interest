from datetime import datetime
from datetime import timedelta
from typing import List

from pydantic import BaseModel
import clickhouse_connect

from .settings import Settings


class Client:
    settings: Settings
    batch: List[BaseModel]
    last_sync: datetime
    table: str
    model: BaseModel

    def __init__(self, table, model):
        self.table = table
        self.model = model
        self.batch = []

    async def insert(self, model):
        self.batch.append(list(model.dict().values()))

        if len(self.batch) >= self.settings.batch_size \
                or datetime.now() - self.last_sync > timedelta(seconds=self.settings.sync_period_seconds):
            await self.dump()

    async def dump(self):
        client = clickhouse_connect.get_client(
            host=self.settings.host,
            port=self.settings.port,
            username=self.settings.username,
            password=self.settings.password.get_secret_value())
        client.insert(self.table,
                      self.batch,
                      column_names=list(
                          self.model.schema()['properties'].keys()))
        self.last_sync = datetime.now()
        self.batch = []

    async def __aenter__(self):
        self.settings = Settings()
        self.last_sync = datetime.now()

        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        if len(self.batch) > 0:
            await self.dump()
