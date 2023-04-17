import asyncio
import argparse
import importlib

from utils import configure_structlog


async def main():
    configure_structlog()

    mode_help = """
        Running options:

            [service] [action] [arguments]

    """

    parser = argparse.ArgumentParser(description='cli')

    parser.add_argument('service', help=mode_help)
    parser.add_argument('action', help=mode_help)
    parser.add_argument('arguments', nargs='*', help=mode_help)
    args = parser.parse_args()

    service = importlib.import_module(args.service, args)
    await getattr(service, args.action)(*args.arguments)


if __name__ == '__main__':
    asyncio.run(main())
