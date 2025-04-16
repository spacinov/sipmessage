#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import dataclasses
from typing import Union

from .address import Address
from .auth import AuthChallenge, AuthCredentials
from .cseq import CSeq
from .uri import URI
from .via import Via


class Headers:
    def __init__(self) -> None:
        self._list: list[tuple[str, list[str]]] = []

    def add(self, key: str, value: str) -> None:
        """
        Add a new header.
        """
        ikey = key.lower()
        for i, (k, values) in enumerate(self._list):
            if k.lower() == ikey:
                values.append(value)
                break
        else:
            self._list.append((key, [value]))

    def get(self, key: str, default: str | None = None) -> str | None:
        """
        Return the first value for the given header or `default`.
        """
        ikey = key.lower()
        for k, values in self._list:
            if k.lower() == ikey:
                return values[0]
        return default

    def getlist(self, key: str) -> list[str]:
        """
        Return all the values for the given header.
        """
        ikey = key.lower()
        for k, values in self._list:
            if k.lower() == ikey:
                return values
        return []

    def remove(self, key: str) -> None:
        """
        Remove the given header.
        """
        ikey = key.lower()
        for i, (k, _values) in enumerate(self._list[:]):
            if k.lower() == ikey:
                self._list.pop(i)
                break

    def set(self, key: str, value: str) -> None:
        """
        Remove all values for the given header and replace them
        with the given `value`.
        """
        ikey = key.lower()
        for i, (k, _values) in enumerate(self._list[:]):
            if k.lower() == ikey:
                self._list[i] = (k, [value])
                break
        else:
            self._list.append((key, [value]))

    def setlist(self, key: str, values: list[str]) -> None:
        """
        Remove all values for the given header and replace them
        with the given `values`.
        """
        ikey = key.lower()
        for i, (k, _values) in enumerate(self._list[:]):
            if k.lower() == ikey:
                self._list[i] = (k, values)
                break
        else:
            self._list.append((key, values))

    def __getitem__(self, key: str) -> str:
        ikey = key.lower()
        for k, values in self._list:
            if k.lower() == ikey:
                return values[0]
        raise KeyError

    def __str__(self) -> str:
        output = ""
        for k, values in self._list:
            for value in values:
                output += f"{k}: {value}\r\n"
        return output + "\r\n"


class Message:
    body: str

    _headers: Headers

    @staticmethod
    def parse(data: str) -> Union["Request", "Response"]:
        """
        Parse the given string into a :class:`Request` or :class:`Response` instance.

        If parsing fails, a :class:`ValueError` is raised.
        """

        lines = data.split("\r\n")
        if len(lines) < 2:
            raise ValueError("SIP message has too few lines")

        # parse first line
        bits = lines.pop(0).split(" ", 2)
        message: Request | Response
        if len(bits) > 2 and bits[2] == "SIP/2.0":
            message = Request(method=bits[0], uri=URI.parse(bits[1]))
        elif len(bits) > 2 and bits[0] == "SIP/2.0":
            message = Response(code=int(bits[1]), phrase=bits[2])
        else:
            raise ValueError("SIP message is neither request nor response")

        while len(lines):
            line = lines.pop(0)
            if line == "":
                message.body = "\r\n".join(lines)
                break
            key, val = line.split(":", 1)
            message._headers.add(key, val.strip())

        return message

    @property
    def authorization(self) -> AuthCredentials | None:
        """
        The `Authorization` header value.

        :rfc:`3261#section-20.7`
        """
        return self._get_auth_credentials("Authorization")

    @authorization.setter
    def authorization(self, value: AuthCredentials | None) -> None:
        self._set_auth_credentials("Authorization", value)

    @property
    def call_id(self) -> str:
        """
        The `Call-ID` header value.

        :rfc:`3261#section-20.8`
        """
        return self._headers["Call-ID"]

    @call_id.setter
    def call_id(self, value: str) -> None:
        self._headers.set("Call-ID", value)

    @property
    def contact(self) -> list[Address]:
        """
        The `Contact` header values.

        :rfc:`3261#section-20.10`
        """
        return self._get_address_list("Contact")

    @contact.setter
    def contact(self, value: list[Address]) -> None:
        self._set_address_list("Contact", value)

    @property
    def content_length(self) -> int | None:
        """
        The `Content-Length` header value.

        :rfc:`3261#section-20.14`
        """
        return self._get_optional_int("Content-Length")

    @content_length.setter
    def content_length(self, value: int | None) -> None:
        self._set_optional_int("Content-Length", value)

    @property
    def content_type(self) -> str | None:
        """
        The `Content-Length` header value.

        :rfc:`3261#section-20.15`
        """
        return self._get_optional_str("Content-Type")

    @content_type.setter
    def content_type(self, value: str | None) -> None:
        self._set_optional_str("Content-Type", value)

    @property
    def cseq(self) -> CSeq:
        """
        The `CSeq` header value.

        :rfc:`3261#section-20.16`
        """
        return CSeq.parse(self._headers["CSeq"])

    @cseq.setter
    def cseq(self, value: CSeq) -> None:
        self._headers.set("CSeq", str(value))

    @property
    def from_address(self) -> Address:
        """
        The `From` header value.

        :rfc:`3261#section-20.20`
        """
        return Address.parse(self._headers["From"])

    @from_address.setter
    def from_address(self, value: Address) -> None:
        self._headers.set("From", str(value))

    @property
    def max_forwards(self) -> int | None:
        """
        The `Max-Forwards` header value.

        :rfc:`3261#section-20.22`
        """
        return self._get_optional_int("Max-Forwards")

    @max_forwards.setter
    def max_forwards(self, value: int | None) -> None:
        self._set_optional_int("Max-Forwards", value)

    @property
    def proxy_authenticate(self) -> AuthChallenge | None:
        """
        The `Proxy-Authenticate` header value.

        :rfc:`3261#section-20.27`
        """
        return self._get_auth_challenge("Proxy-Authenticate")

    @proxy_authenticate.setter
    def proxy_authenticate(self, value: AuthChallenge | None) -> None:
        self._set_auth_challenge("Proxy-Authenticate", value)

    @property
    def proxy_authorization(self) -> AuthCredentials | None:
        """
        The `Proxy-Authorization` header value.

        :rfc:`3261#section-20.28`
        """
        return self._get_auth_credentials("Proxy-Authorization")

    @proxy_authorization.setter
    def proxy_authorization(self, value: AuthCredentials | None) -> None:
        self._set_auth_credentials("Proxy-Authorization", value)

    @property
    def to_address(self) -> Address:
        """
        The `To` header value value.

        :rfc:`3261#section-20.39`
        """
        return Address.parse(self._headers["To"])

    @to_address.setter
    def to_address(self, value: Address) -> None:
        self._headers.set("To", str(value))

    @property
    def record_route(self) -> list[Address]:
        """
        The `Record-Route` header values.

        :rfc:`3261#section-20.30`
        """
        return self._get_address_list("Record-Route")

    @record_route.setter
    def record_route(self, value: list[Address]) -> None:
        self._set_address_list("Record-Route", value)

    @property
    def route(self) -> list[Address]:
        """
        The `Route` header values.

        :rfc:`3261#section-20.34`
        """
        return self._get_address_list("Route")

    @route.setter
    def route(self, value: list[Address]) -> None:
        self._set_address_list("Route", value)

    @property
    def user_agent(self) -> str | None:
        """
        The `User-Agent` header value.

        :rfc:`3261#section-20.41`
        """
        return self._get_optional_str("User-Agent")

    @user_agent.setter
    def user_agent(self, value: str | None) -> None:
        self._set_optional_str("User-Agent", value)

    @property
    def via(self) -> list[Via]:
        """
        The `Via` header values.

        :rfc:`3261#section-20.42`
        """
        headers: list[Via] = []
        for value in self._headers.getlist("Via"):
            headers += Via.parse_many(value)
        return headers

    @via.setter
    def via(self, value: list[Via]) -> None:
        self._headers.setlist("Via", [str(x) for x in value])

    @property
    def www_authenticate(self) -> AuthChallenge | None:
        """
        The `WWW-Authenticate` header values.

        :rfc:`3261#section-20.44`
        """
        return self._get_auth_challenge("WWW-Authenticate")

    @www_authenticate.setter
    def www_authenticate(self, value: AuthChallenge | None) -> None:
        self._set_auth_challenge("WWW-Authenticate", value)

    def _get_address_list(self, key: str) -> list[Address]:
        headers: list[Address] = []
        for value in self._headers.getlist(key):
            headers += Address.parse_many(value)
        return headers

    def _set_address_list(self, key: str, value: list[Address]) -> None:
        self._headers.setlist(key, [str(x) for x in value])

    def _get_auth_challenge(self, key: str) -> AuthChallenge | None:
        value = self._headers.get(key, None)
        if value is None:
            return None
        else:
            return AuthChallenge.parse(value)

    def _set_auth_challenge(self, key: str, value: AuthChallenge | None) -> None:
        if value is None:
            self._headers.remove(key)
        else:
            self._headers.set(key, str(value))

    def _get_auth_credentials(self, key: str) -> AuthCredentials | None:
        value = self._headers.get(key, None)
        if value is None:
            return None
        else:
            return AuthCredentials.parse(value)

    def _set_auth_credentials(self, key: str, value: AuthCredentials | None) -> None:
        if value is None:
            self._headers.remove(key)
        else:
            self._headers.set(key, str(value))

    def _get_optional_int(self, key: str) -> int | None:
        value = self._headers.get(key, None)
        if value is None:
            return None
        else:
            return int(value)

    def _set_optional_int(self, key: str, value: int | None) -> None:
        if value is None:
            self._headers.remove(key)
        else:
            self._headers.set(key, str(value))

    def _get_optional_str(self, key: str) -> str | None:
        return self._headers.get(key, None)

    def _set_optional_str(self, key: str, value: str | None) -> None:
        if value is None:
            self._headers.remove(key)
        else:
            self._headers.set(key, value)


@dataclasses.dataclass
class Request(Message):
    """
    A SIP request.
    """

    method: str
    "The request method."

    uri: URI
    "The request URI."

    body: str = ""
    "The request body."

    _headers: Headers = dataclasses.field(default_factory=Headers)

    def __str__(self) -> str:
        return "%s %s SIP/2.0\r\n%s%s" % (
            self.method,
            self.uri,
            self._headers,
            self.body,
        )


@dataclasses.dataclass
class Response(Message):
    """
    A SIP response.
    """

    code: int
    "The response code."

    phrase: str
    "The response phrase."

    body: str = ""
    "The response body."

    _headers: Headers = dataclasses.field(default_factory=Headers)

    def __str__(self) -> str:
        return "SIP/2.0 %s %s\r\n%s%s" % (
            self.code,
            self.phrase,
            self._headers,
            self.body,
        )
