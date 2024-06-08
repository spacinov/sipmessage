#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import dataclasses
import re

from . import grammar
from .parameters import Parameters

VIA_PATTERN = re.compile(
    f"^SIP{grammar.SLASH}2\\.0{grammar.SLASH}(?P<transport>{grammar.TOKEN}) "
    f"(?P<host>{grammar.HOST})"
    f"(?::(?P<port>{grammar.PORT}))?"
    f"(?P<parameters>(?:{grammar.SEMI}{grammar.GENERIC_PARAM})*)"
    "$"
)


@dataclasses.dataclass
class Via:
    """
    A `Via` header, indicating a reponse location for a transaction.
    """

    transport: str
    'The transport for the transaction, e.g `"UDP"`, `"TCP"`, `"TLS"`.'

    host: str
    "The host to which responses should to be sent."

    port: int | None = None
    "The port to which responses should to be sent."

    parameters: Parameters = dataclasses.field(default_factory=Parameters)
    "The parameters of the address."

    @classmethod
    def parse(cls, value: str) -> "Via":
        """
        Parse the given string into a :class:`Via` instance.

        If parsing fails, a :class:`ValueError` is raised.
        """
        value = grammar.simplify_whitespace(value)

        m = VIA_PATTERN.match(value)
        if m is None:
            raise ValueError("Via is not valid")

        port = m.group("port")

        return cls(
            transport=m.group("transport"),
            host=m.group("host"),
            port=int(port) if port else None,
            parameters=Parameters.parse(m.group("parameters")),
        )

    def __str__(self) -> str:
        s = f"SIP/2.0/{self.transport} {self.host}"
        if self.port is not None:
            s += f":{self.port}"
        s += str(self.parameters)
        return s
