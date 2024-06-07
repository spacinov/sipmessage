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
    f"(?P<address>{grammar.HOST}(?::{grammar.PORT})?)"
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

    address: str
    "The location where the response is to be sent."

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

        return cls(
            transport=m.group("transport"),
            address=m.group("address"),
            parameters=Parameters.parse(m.group("parameters")),
        )

    def __str__(self) -> str:
        s = "SIP/2.0/%s %s" % (self.transport, self.address)
        if self.parameters:
            s += ";" + str(self.parameters)
        return s
