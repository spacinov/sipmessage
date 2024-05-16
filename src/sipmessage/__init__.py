#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import importlib.metadata

from .parameters import Parameters
from .uri import URI

__all__ = ["Parameters", "URI"]
__version__ = importlib.metadata.version("sipmessage")
