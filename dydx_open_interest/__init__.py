""" Service root

Use this module only for imports from other modules. Mainly, this is an API for "pdm run cli" command
"""

from .actions import aws_lambda
from .actions import get_markets
from .actions import load_open_interest
from .actions import load_open_interest_now