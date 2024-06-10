#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import dataclasses
import re

from . import grammar, utils
from .parameters import Parameters
from .uri import URI

TOKEN_LWS = grammar.cset(grammar.C_TOKEN + " ")

ADDRESS_EXCEPTION = ValueError("Address is not valid")
ADDRESS_PATTERNS = [
    # name-addr *(SEMI contact-params)
    re.compile(
        # display-name
        f"^(?P<name>{TOKEN_LWS}*|{grammar.QUOTED_STRING})"
        # LAQUOT addr-spec RAQUOT
        f"{grammar.SWS}<(?P<uri>[^>]+)>{grammar.SWS}"
        # *(SEMI contact-params)
        f"(?P<parameters>(?:{grammar.SEMI}{grammar.GENERIC_PARAM})*)"
    ),
    # addr-spec *(SEMI contact-params)
    re.compile(
        # no name
        "^(?P<name>)"
        # addr-spec
        "(?P<uri>[^ ;]+)"
        # *(SEMI contact-params)
        f"(?P<parameters>(?:{grammar.SEMI}{grammar.GENERIC_PARAM})*)"
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
        return utils.parse_single(cls._parse_one, ADDRESS_EXCEPTION, value)

    @classmethod
    def parse_many(cls, value: str) -> "list[Address]":
        """
        Parse the given string into a list of :class:`Address` instances.

        If parsing fails, a :class:`ValueError` is raised.
        """
        return utils.parse_many(cls._parse_one, ADDRESS_EXCEPTION, value)

    @classmethod
    def _parse_one(cls, value: str) -> "tuple[Address, str]":
        for pattern in ADDRESS_PATTERNS:
            m = pattern.match(value)
            if m:
                return (
                    cls(
                        uri=URI.parse(m.group("uri")),
                        name=unquote(m.group("name").strip()),
                        parameters=Parameters.parse(m.group("parameters")),
                    ),
                    value[m.end() :],
                )
        else:
            raise ADDRESS_EXCEPTION

    def __str__(self) -> str:
        s = ""
        if self.name:
            s += quote(self.name) + " "
        s += f"<{self.uri}>{self.parameters}"
        return s
