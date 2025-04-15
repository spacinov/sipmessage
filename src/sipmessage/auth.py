#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import dataclasses
import re
from collections.abc import Iterator, Mapping

from . import grammar
from .address import quote, unquote

AUTH_CHALLENGE_PATTERN = re.compile(
    f"^(?P<scheme>{grammar.TOKEN}){grammar.LWS}"
    f"(?P<parameters>{grammar.AUTH_PARAM}(?:{grammar.COMMA}{grammar.AUTH_PARAM})*)"
    "$"
)
AUTH_CREDENTIALS_PATTERN = re.compile(
    f"^(?P<scheme>{grammar.TOKEN}){grammar.LWS}"
    f"(?P<parameters>(?:{grammar.TOKEN}|{grammar.AUTH_PARAM}(?:{grammar.COMMA}{grammar.AUTH_PARAM})*))"
    "$"
)

COMMA_PATTERN = re.compile(f"{grammar.SWS}{grammar.COMMA}{grammar.SWS}")
EQUAL_PATTERN = re.compile(f"{grammar.SWS}{grammar.EQUAL}{grammar.SWS}")
TOKEN_PATTERN = re.compile("^" + grammar.TOKEN + "$")

QUOTED_PARAMETERS = frozenset(
    ["cnonce", "domain", "nonce", "opaque", "qop", "realm", "response", "username"]
)


def maybe_quote(v: str, force_quote: bool) -> str:
    if TOKEN_PATTERN.match(v) and not force_quote:
        return v
    else:
        return quote(v)


class AuthParameters(Mapping[str, str]):
    """
    A mapping of :class:`AuthChallenge` or :class:`AuthCredentials` parameters.
    """

    def __init__(self, **kwargs: str) -> None:
        self.__data = dict(kwargs)

    @classmethod
    def parse(cls, value: str) -> "AuthParameters":
        """
        Parse the given string into a :class:`AuthParameters` instance.

        If parsing fails, a :class:`ValueError` is raised.
        """
        data: dict[str, str] = {}
        value = value.strip()
        if value:
            bits = COMMA_PATTERN.split(value)

            for bit in bits:
                # Empty parameters are not allowed.
                if "=" not in bit:
                    raise ValueError("AuthParameters are not valid")

                k, v = EQUAL_PATTERN.split(bit, 1)
                data[unquote(k)] = unquote(v)
        return cls(**data)

    def replace(self, **changes: str) -> "AuthParameters":
        """
        Return a copy of the parameters, updated with the given `changes`.
        """
        data = {}
        data.update(self.__data)
        data.update(**changes)
        return AuthParameters(**data)

    def __getitem__(self, key: str) -> str:
        return self.__data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.__data)

    def __len__(self) -> int:
        return len(self.__data)

    def __repr__(self) -> str:
        data = ""
        for k, v in self.items():
            if data:
                data += ", "
            data += f"{k}={v!r}"
        return f"AuthParameters({data})"

    def __str__(self) -> str:
        bits = [
            k + "=" + maybe_quote(v, force_quote=k in QUOTED_PARAMETERS)
            for (k, v) in self.items()
        ]
        return ", ".join(bits)


@dataclasses.dataclass(frozen=True)
class AuthChallenge:
    """
    A `WWW-Authenticate` or `Proxy-Authenticate` header, used to convey
    an authentication challenge.
    """

    scheme: str
    'The authentication scheme, e.g. `"Digest"`.'

    parameters: AuthParameters = dataclasses.field(default_factory=AuthParameters)
    "The authentication parameters."

    @classmethod
    def parse(cls, value: str) -> "AuthChallenge":
        """
        Parse the given string into an :class:`AuthChallenge` instance.

        If parsing fails, a :class:`ValueError` is raised.
        """
        m = AUTH_CHALLENGE_PATTERN.match(value)
        if m is None:
            raise ValueError("AuthChallenge is not valid")

        return cls(
            scheme=m.group("scheme"),
            parameters=AuthParameters.parse(m.group("parameters")),
        )

    def __str__(self) -> str:
        s = self.scheme.title()
        if self.parameters:
            s += " " + str(self.parameters)
        return s


@dataclasses.dataclass(frozen=True)
class AuthCredentials:
    """
    An `Authorization`, `Proxy-Authorization` header, used to convey
    authentication credentials.
    """

    scheme: str
    'The authentication scheme, e.g. `"Digest"`.'

    parameters: AuthParameters | None = None
    "The authentication parameters."

    token: str | None = None
    "The authentication token."

    @classmethod
    def parse(cls, value: str) -> "AuthCredentials":
        """
        Parse the given string into an :class:`AuthCredentials` instance.

        If parsing fails, a :class:`ValueError` is raised.
        """
        m = AUTH_CREDENTIALS_PATTERN.match(value)
        if m is None:
            raise ValueError("AuthCredentials are not valid")

        if TOKEN_PATTERN.match(m.group("parameters")):
            return cls(
                scheme=m.group("scheme"),
                parameters=None,
                token=m.group("parameters"),
            )
        else:
            return cls(
                scheme=m.group("scheme"),
                parameters=AuthParameters.parse(m.group("parameters")),
            )

    def __post_init__(self) -> None:
        if (self.parameters is None) == (self.token is None):
            raise ValueError("Exactly one of `parameters` or `token` must be set.")

    def __str__(self) -> str:
        s = self.scheme.title()
        if self.token:
            s += " " + self.token
        elif self.parameters:
            s += " " + str(self.parameters)
        return s
