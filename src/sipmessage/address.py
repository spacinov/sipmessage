#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import dataclasses
import re

import abnf

from .parameters import Parameters
from .rfc3261 import Rule
from .uri import URI


def get_parts(value: str) -> tuple[str, str, str]:
    uri = ""
    name = ""
    parameters: list[str] = []

    queue = [rule.parse_all(value)]
    while queue:
        n, queue = queue[0], queue[1:]
        if n.name == "addr-spec":
            uri = n.value
        elif n.name == "display-name":
            name = n.value.strip()
            if name.startswith('"'):
                name = name[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        elif n.name == "contact-params":
            parameters.append(n.value)
        else:
            queue.extend(n.children)
    return uri, name, ";".join(parameters)


rule = Rule("contact-param")


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
        value = re.sub(r"\s+", " ", value)

        try:
            uri, name, parameters = get_parts(value)
        except abnf.ParseError:
            raise ValueError("Not a valid address")

        return cls(
            uri=URI.parse(uri),
            name=name,
            parameters=Parameters.parse(parameters),
        )

    def __str__(self) -> str:
        s = ""
        if self.name:
            s += '"%s" ' % self.name.replace("\\", "\\\\").replace('"', '\\"')
        s += "<%s>" % self.uri
        if self.parameters:
            s += ";" + str(self.parameters)
        return s
