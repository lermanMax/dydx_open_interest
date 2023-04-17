import clickhouse_connect

from .settings import Settings


def command(command):
    settings = Settings()
    client = clickhouse_connect.get_client(
        host=settings.host,
        port=settings.port,
        username=settings.username,
        password=settings.password.get_secret_value())

    client.command(command)


def query(*args):
    settings = Settings()
    client = clickhouse_connect.get_client(
        host=settings.host,
        port=settings.port,
        username=settings.username,
        password=settings.password.get_secret_value())

    return client.query(*args)


def create_table(table_name, model):
    settings = Settings()

    datatypes_mapping = {
        'string': 'String',
        'integer': 'Int64',
        'number': 'Float64',
        'date-time': 'DateTime(\'UTC\') DEFAULT now()',
        'boolean': 'UInt8',
    }

    client = clickhouse_connect.get_client(
        host=settings.host,
        port=settings.port,
        username=settings.username,
        password=settings.password.get_secret_value())

    fields = []
    for property, config in model.schema()['properties'].items():
        field = [
            f'{property}',
            f'{datatypes_mapping[config.get("format", None) or config["type"]]}',
        ]
        if property in model.schema()["required"]:
            field.append('NOT NULL')

        fields.append(' '.join(field))
    fields = ',\n'.join(fields)

    client.command(f"""
        CREATE TABLE IF NOT EXISTS {table_name}
        (
            updated_at DateTime DEFAULT now(),
            {fields}
        ) ENGINE = {model.Config.engine}
        ORDER BY {model.Config.primary_key}
        PRIMARY KEY {model.Config.primary_key}
        TTL {model.Config.ttl}
        """)
