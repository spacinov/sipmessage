#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import importlib.metadata

from .address import Address
from .cseq import CSeq
from .parameters import Parameters
from .uri import URI
from .via import Via

__all__ = ["Address", "CSeq", "Parameters", "URI", "Via"]
__version__ = importlib.metadata.version("sipmessage")
