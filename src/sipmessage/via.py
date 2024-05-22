#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import dataclasses
import re

from .parameters import Parameters


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
        m = re.match(r"SIP/2\.0/([A-Z]+) (.+)", value)
        if m is None:
            raise ValueError("Malformed Via header")

        transport = m.group(1)
        address, _, rest = m.group(2).partition(";")
        return cls(
            transport=transport,
            address=address,
            parameters=Parameters.parse(rest),
        )

    def __str__(self) -> str:
        s = "SIP/2.0/%s %s" % (self.transport, self.address)
        if self.parameters:
            s += ";" + str(self.parameters)
        return s
