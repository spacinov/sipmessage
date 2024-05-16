#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import dataclasses
import re

from .parameters import Parameters
from .uri import URI

ADDRESS_PATTERNS = [
    # name-addr *(SEMI contact-params)
    re.compile(
        # token
        r"^(?P<name>[a-zA-Z0-9\-\._\+~]*)"
        # LWS
        "[ \t]*"
        # LAQUOT addr-spec RAQUOT
        "<(?P<uri>[^>]+)>"
        "[ \t]*"
        r"(?:;(?P<parameters>[^\?]*))?"
    ),
    # name-addr *(SEMI contact-params)
    re.compile(
        # quoted-string
        '^(?:"(?P<name>[^"]+)")'
        # LWS
        "[ \t]*"
        # LAQUOT addr-spec RAQUOT
        "<(?P<uri>[^>]+)>"
        "[ \t]*"
        r"(?:;(?P<parameters>[^\?]*))?"
    ),
    # addr-spec *(SEMI contact-params)
    re.compile(
        # no name
        "^(?P<name>)"
        # addr-spec
        "(?P<uri>[^ \t;]+)"
        "[ \t]*"
        r"(?:;(?P<parameters>[^\?]*))?"
    ),
]


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
        """
        for pattern in ADDRESS_PATTERNS:
            m = pattern.match(value)
            if m:
                return cls(
                    uri=URI.parse(m.group("uri")),
                    name=m.group("name"),
                    parameters=Parameters.parse(m.group("parameters")),
                )
        else:
            raise ValueError("Not a valid address")

    def __str__(self) -> str:
        s = ""
        if self.name:
            s += '"%s" ' % self.name
        s += "<%s>" % self.uri
        if self.parameters:
            s += ";" + str(self.parameters)
        return s
