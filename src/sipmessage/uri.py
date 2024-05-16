#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import dataclasses
import urllib.parse

from .parameters import Parameters


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
        """
        parsed = urllib.parse.urlparse(value)
        if "@" in parsed.path:
            user_password, host_port = parsed.path.split("@")
            if ":" in user_password:
                user, password = user_password.split(":")
            else:
                user = user_password
                password = None
        else:
            host_port = parsed.path
            user = None
            password = None
        if ":" in host_port:
            host, port_ = host_port.split(":")
            port = int(port_)
        else:
            host = host_port
            port = None
        return cls(
            scheme=parsed.scheme,
            host=host,
            port=port,
            user=user,
            password=password,
            parameters=Parameters.parse(parsed.params),
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
            s += self.user
            if self.password is not None:
                s += ":" + self.password
            s += "@"
        s += self.host
        if self.port is not None:
            s += ":" + str(self.port)
        if self.parameters:
            s += ";" + str(self.parameters)
        return s
