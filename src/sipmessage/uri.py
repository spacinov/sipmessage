#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import dataclasses
import re
import urllib.parse

from . import grammar
from .parameters import Parameters

URI_PATTERN = re.compile(
    "^"
    "(?P<scheme>sip|sips):"
    f"(?:(?P<user>{grammar.USER})(?::(?P<password>{grammar.PASSWORD}))?@)?"
    f"(?P<host>{grammar.HOST})"
    f"(?::(?P<port>{grammar.PORT}))?"
    f"(?P<parameters>(?:;{grammar.URI_PARAM})*)"
    "$"
)


@dataclasses.dataclass
class URI:
    """
    A SIP or SIPS URL as described by RFC3261.
    """

    scheme: str
    "The URL scheme specifier."

    host: str
    "The host providing the SIP resource."

    user: str | None = None
    "The identifier of a particular resource at the host being addressed."

    password: str | None = None
    "A password associated with the user."

    port: int | None = None
    "The port number where the request is to be sent."

    parameters: Parameters = dataclasses.field(default_factory=Parameters)
    "Parameters affecting a request constructed from the URI."

    @classmethod
    def parse(cls, value: str) -> "URI":
        """
        Parse the given string into a :class:`URI` instance.

        If parsing fails, a :class:`ValueError` is raised.
        """
        m = URI_PATTERN.match(value)
        if not m:
            raise ValueError("URI is not valid")

        port = m.group("port")
        user = m.group("user")
        password = m.group("password")
        parameters = m.group("parameters")

        return cls(
            scheme=m.group("scheme"),
            host=m.group("host"),
            port=int(port) if port else None,
            user=urllib.parse.unquote(user) if user else None,
            password=urllib.parse.unquote(password) if password else None,
            parameters=Parameters.parse(parameters),
        )

    @property
    def global_phone_number(self) -> str | None:
        """
        The global phone number (E.164) of this URI, if described by the URI.

        This is one of the possibilities for the `userinfo` part described in RFC3261,
        with telephone-subscriber in RFC2806:

        > userinfo = user | telephone-subscriber
        > telephone-subscriber = global-phone-number | local-phone-number
        """
        if self.user is None:
            return None
        if self.user[0] == "+" and self.user[1:].isnumeric():
            return self.user
        else:
            return None

    def __str__(self) -> str:
        s = self.scheme + ":"
        if self.user is not None:
            s += urllib.parse.quote(self.user, safe=grammar.C_USER_SAFE)
            if self.password is not None:
                s += ":" + urllib.parse.quote(
                    self.password, safe=grammar.C_PASSWORD_SAFE
                )
            s += "@"
        s += self.host
        if self.port is not None:
            s += f":{self.port}"
        s += str(self.parameters)
        return s
