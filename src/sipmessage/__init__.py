#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import importlib.metadata

from .address import Address
from .auth import AuthChallenge, AuthCredentials, AuthParameters
from .cseq import CSeq
from .message import Headers, Message, Request, Response
from .parameters import Parameters
from .uri import URI
from .via import Via

__all__ = [
    "Address",
    "AuthChallenge",
    "AuthCredentials",
    "AuthParameters",
    "CSeq",
    "Headers",
    "Message",
    "Parameters",
    "Request",
    "Response",
    "URI",
    "Via",
]
__version__ = importlib.metadata.version("sipmessage")
