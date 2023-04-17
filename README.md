# Veska Python Boilerplate

This is a setup for python microservices

It contents some business logic to show how code could be structured

There are some ["problems"](https://github.com/GigaTechnologies/veska-python-boilerplate/issues) which should be solved. But as a concept to show - it works just fine


## Requirements

To run this boilerplate you should install [PDM](https://pdm.fming.dev)

Also, [Clickhouse](https://clickhouse.com) is required to run commands which affect database


## Installation

After you install PDM, run:

`pdm install` for production ready environment or `pdm install -d` for development


## Usage

`pdm run cli [service_name] [action] [arguments]` to run specific action of a service

For example, you can run `pdm run cli dydx_price_example load_price_now` to load all current prices for all markets for dYdX exchange

This method we use for AWS Lambdas. Each Lambda runs specific action from a service.

Or as a CLI for system management

Also:

`pdm run test -k [test_name]` for testing. This is just a shortcut for `pdm run pytest -s -k [test_name]`

You can run directly "pytest" for testing if you want


## Configuration

Check `.env.example` for example configuration

You can configure by Environment variables or by `.env` file. Variables have priority against `.env`

Basic configurations consists of:

* Logging config
* Clickhouse config
* Business config

## Code Contract

The Rules how to write code using this boilerplate you can find in [CODE_CONTRACT.md](https://github.com/GigaTechnologies/veska-python-boilerplate/blob/main/CODE_CONTRACT.md)