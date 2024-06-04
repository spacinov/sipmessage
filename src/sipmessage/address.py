#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import dataclasses
import re

from .parameters import Parameters
from .uri import URI

TOKEN_LWS = r"[a-zA-Z0-9\-.!%*_+`'~ ]*"
QUOTED_STRING = '"(?:[^"]|\\")*"'

ADDRESS_PATTERNS = [
    # name-addr *(SEMI contact-params)
    re.compile(
        # display-name
        "^(?P<name>" + TOKEN_LWS + "|" + QUOTED_STRING + ")"
        # LAQUOT addr-spec RAQUOT
        "[ ]*"
        "<(?P<uri>[^>]+)>"
        # *(SEMI contact-params)
        "[ ]*"
        r"(?:;(?P<parameters>[^\?]*))?"
    ),
    # addr-spec *(SEMI contact-params)
    re.compile(
        # no name
        "^(?P<name>)"
        # addr-spec
        "(?P<uri>[^ ;]+)"
        # *(SEMI contact-params)
        "[ ]*"
        r"(?:;(?P<parameters>[^\?]*))?"
    ),
]


def quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def unquote(value: str) -> str:
    if value.startswith('"'):
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    else:
        return value


@dataclasses.dataclass
class Address:
    """
    An address as used in `Contact`, `From`, `Reply-To` and `To` headers.
    """

    uri: URI
    "The URI of the address."

    name: str = ""
    "The display name of the address."

    parameters: Parameters = dataclasses.field(default_factory=Parameters)
    "The parameters of the address."

    @classmethod
    def parse(cls, value: str) -> "Address":
        """
        Parse the given string into an :class:`Address` instance.

        If parsing fails, a :class:`ValueError` is raised.
        """

        # All linear white space, including folding, has the same semantics as SP.
        value = re.sub(r"\s+", " ", value).strip()

        for pattern in ADDRESS_PATTERNS:
            m = pattern.match(value)
            if m:
                return cls(
                    uri=URI.parse(m.group("uri")),
                    name=unquote(m.group("name").strip()),
                    parameters=Parameters.parse(m.group("parameters")),
                )
        else:
            raise ValueError("Not a valid address")

    def __str__(self) -> str:
        s = ""
        if self.name:
            s += quote(self.name) + " "
        s += "<%s>" % self.uri
        if self.parameters:
            s += ";" + str(self.parameters)
        return s
