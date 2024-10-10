#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import dataclasses
import re
import string
import urllib.parse

from . import grammar
from .parameters import Parameters

C_VISUAL_SEPARATOR = "-.()"

PHONEDIGIT = grammar.cset(string.digits + C_VISUAL_SEPARATOR)
PHONEDIGIT_HEX = grammar.cset(string.hexdigits + "*#" + C_VISUAL_SEPARATOR)
GLOBAL_NUMBER_DIGITS = f"\\+{PHONEDIGIT}*{grammar.DIGIT}{PHONEDIGIT}*"
LOCAL_NUMBER_DIGITS = (
    f"{PHONEDIGIT_HEX}*{grammar.cset(string.hexdigits + '*#')}{PHONEDIGIT_HEX}*"
)

SIP_URI_PATTERN = re.compile(
    "^"
    "(?P<scheme>sip|sips):"
    f"(?:(?P<user>{grammar.USER})(?::(?P<password>{grammar.PASSWORD}))?@)?"
    f"(?P<host>{grammar.HOST})"
    f"(?::(?P<port>{grammar.PORT}))?"
    f"(?P<parameters>(?:;{grammar.URI_PARAM})*)"
    "$"
)
TEL_URI_PATTERN = re.compile(
    "^"
    "(?P<scheme>tel):"
    f"(?P<subscriber>(?:{GLOBAL_NUMBER_DIGITS}|{LOCAL_NUMBER_DIGITS}))"
    f"(?P<parameters>(?:;{grammar.URI_PARAM})*)"
    "$"
)


@dataclasses.dataclass(frozen=True)
class URI:
    """
    A SIP, SIPS or TEL URI as described by RFC3261 and RFC3966.
    """

    scheme: str
    "The URI scheme specifier."

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
        if m := SIP_URI_PATTERN.match(value):
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
        elif m := TEL_URI_PATTERN.match(value):
            parameters = m.group("parameters")

            return cls(
                scheme=m.group("scheme"),
                host="",
                user=m.group("subscriber"),
                parameters=Parameters.parse(parameters),
            )
        else:
            raise ValueError("URI is not valid")

    @property
    def global_phone_number(self) -> str | None:
        """
        The global phone number (E.164) of this URI, if described by the URI.

        This is one of the possibilities for the `userinfo` part described in RFC3261,
        with telephone-subscriber in RFC2806:

        > userinfo = user | telephone-subscriber
        > telephone-subscriber = global-phone-number | local-phone-number

        The phone number is returned without any visual separators.
        """
        if self.user is None:
            return None
        if re.match(GLOBAL_NUMBER_DIGITS, self.user):
            return re.sub(grammar.cset(C_VISUAL_SEPARATOR), "", self.user)
        else:
            return None

    def __str__(self) -> str:
        s = self.scheme + ":"
        if self.scheme == "tel":
            assert self.user is not None
            s += self.user
        else:
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
