#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import datetime
import typing
import unittest
import zoneinfo

from sipmessage import (
    URI,
    Address,
    AuthChallenge,
    AuthCredentials,
    AuthParameters,
    CSeq,
    Message,
    Parameters,
    Request,
    Response,
    Via,
)
from sipmessage.message import Headers

ADDRESS = Address(uri=URI(scheme="sip", host="example.com"))
AUTHENTICATE = AuthChallenge(
    "Digest",
    parameters=AuthParameters(
        realm="atlanta.com",
        domain="sip:boxesbybob.com",
        qop="auth",
        nonce="f84f1cec41e6cbe5aea9c8e88d359",
        opaque="",
        stale="FALSE",
        algorithm="MD5",
    ),
)
AUTHORIZATION = AuthCredentials(
    "Digest",
    parameters=AuthParameters(
        username="Alice",
        realm="atlanta.com",
        nonce="84a4cc6f3082121f32b42a2187831a9e",
        response="7587245234b3434cc3412213e5f113a5432",
    ),
)
CSEQ = CSeq(sequence=1, method="OPTIONS")
VIA = Via(
    transport="WSS",
    host="mYn6S3lQaKjo.invalid",
    parameters=Parameters(branch="z9hG4bKgD24yaj"),
)

T = typing.TypeVar("T", bytes, str)


def dummy_message() -> Request:
    return Request("OPTIONS", URI(scheme="sip", host="example.com"))


def lf2crlf(x: T) -> T:
    if isinstance(x, bytes):
        return x.replace(b"\n", b"\r\n")
    else:
        return x.replace("\n", "\r\n")


class HeadersTest(unittest.TestCase):
    def test_add(self) -> None:
        headers = Headers()

        headers.add(
            "Via", "SIP/2.0/UDP bigbox3.site3.atlanta.com;branch=z9hG4bK77ef4c2312983.1"
        )
        self.assertEqual(
            str(headers),
            lf2crlf("""Via: SIP/2.0/UDP bigbox3.site3.atlanta.com;branch=z9hG4bK77ef4c2312983.1

"""),
        )
        self.assertEqual(headers.keys(), ["Via"])

        headers.add(
            "Via",
            "SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bKnashds8;received=192.0.2.1",
        )
        self.assertEqual(
            str(headers),
            lf2crlf("""Via: SIP/2.0/UDP bigbox3.site3.atlanta.com;branch=z9hG4bK77ef4c2312983.1
Via: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bKnashds8;received=192.0.2.1

"""),
        )

        headers.add("From", "<sip:alice@atlanta.com>")
        self.assertEqual(
            str(headers),
            lf2crlf("""Via: SIP/2.0/UDP bigbox3.site3.atlanta.com;branch=z9hG4bK77ef4c2312983.1
Via: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bKnashds8;received=192.0.2.1
From: <sip:alice@atlanta.com>

"""),
        )
        self.assertEqual(headers.keys(), ["Via", "From"])

    def test_set(self) -> None:
        headers = Headers()

        headers.set("To", "Bob <sip:bob@biloxi.com>")
        self.assertEqual(
            str(headers),
            lf2crlf("""To: Bob <sip:bob@biloxi.com>

"""),
        )
        self.assertEqual(headers.keys(), ["To"])

        headers.set("To", "Alice <sip:alice@biloxi.com>")
        self.assertEqual(
            str(headers),
            lf2crlf("""To: Alice <sip:alice@biloxi.com>

"""),
        )

    def test_setlist(self) -> None:
        headers = Headers()

        headers.setlist(
            "Via",
            ["SIP/2.0/UDP bigbox3.site3.atlanta.com;branch=z9hG4bK77ef4c2312983.1"],
        )
        self.assertEqual(
            str(headers),
            lf2crlf("""Via: SIP/2.0/UDP bigbox3.site3.atlanta.com;branch=z9hG4bK77ef4c2312983.1

"""),
        )
        self.assertEqual(headers.keys(), ["Via"])

        headers.setlist(
            "Via",
            [
                "SIP/2.0/UDP bigbox3.site3.atlanta.com;branch=z9hG4bK77ef4c2312983.1",
                "SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bKnashds8;received=192.0.2.1",
            ],
        )
        self.assertEqual(
            str(headers),
            lf2crlf("""Via: SIP/2.0/UDP bigbox3.site3.atlanta.com;branch=z9hG4bK77ef4c2312983.1
Via: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bKnashds8;received=192.0.2.1

"""),
        )
        self.assertEqual(headers.keys(), ["Via"])


class MessageTest(unittest.TestCase):
    maxDiff = None

    REQUEST_COMPACT_BYTES = lf2crlf(
        b"""REGISTER sip:atlanta.com SIP/2.0
v: SIP/2.0/WSS mYn6S3lQaKjo.invalid;branch=z9hG4bKgD24yaj
Max-Forwards: 70
t: <sip:alice@atlanta.com>
f: <sip:alice@atlanta.com>;tag=69piINLbAb
i: t87Br1RHAoBz2FsrKKk6hV
CSeq: 1 REGISTER
m: <sip:Mk9sZp5Z@mYn6S3lQaKjo.invalid;transport=ws>;expires=300
User-Agent: Tester/0.1.0
l: 0

"""
    )
    REQUEST_FULL_BYTES = lf2crlf(
        b"""REGISTER sip:atlanta.com SIP/2.0
Via: SIP/2.0/WSS mYn6S3lQaKjo.invalid;branch=z9hG4bKgD24yaj
Max-Forwards: 70
To: <sip:alice@atlanta.com>
From: <sip:alice@atlanta.com>;tag=69piINLbAb
Call-ID: t87Br1RHAoBz2FsrKKk6hV
CSeq: 1 REGISTER
Contact: <sip:Mk9sZp5Z@mYn6S3lQaKjo.invalid;transport=ws>;expires=300
User-Agent: Tester/0.1.0
Content-Length: 0

"""
    )

    def assertMessageHeaders(self, request: Message, values: list[str]) -> None:
        self.assertEqual(str(request.headers).split("\r\n")[:-2], values)

    def _test_request(self, message_bytes: bytes) -> None:
        message = Message.parse(message_bytes)
        assert isinstance(message, Request)

        self.assertEqual(message.method, "REGISTER")
        self.assertEqual(message.uri, URI(scheme="sip", host="atlanta.com"))
        self.assertEqual(message.body, b"")

        # Check headers.
        self.assertEqual(message.call_id, "t87Br1RHAoBz2FsrKKk6hV")
        self.assertEqual(message.content_type, None)
        self.assertEqual(message.content_length, 0)
        self.assertEqual(message.cseq, CSeq(sequence=1, method="REGISTER"))
        self.assertEqual(
            message.contact,
            [
                Address(
                    uri=URI(
                        scheme="sip",
                        host="mYn6S3lQaKjo.invalid",
                        user="Mk9sZp5Z",
                        parameters=Parameters(transport="ws"),
                    ),
                    parameters=Parameters(expires="300"),
                )
            ],
        )
        self.assertEqual(
            message.from_address,
            Address(
                uri=URI(scheme="sip", host="atlanta.com", user="alice"),
                parameters=Parameters(tag="69piINLbAb"),
            ),
        )
        self.assertEqual(message.max_forwards, 70)
        self.assertEqual(
            message.to_address,
            Address(uri=URI(scheme="sip", host="atlanta.com", user="alice")),
        )
        self.assertEqual(message.proxy_authenticate, None)
        self.assertEqual(message.user_agent, "Tester/0.1.0")
        self.assertEqual(
            message.via,
            [
                Via(
                    transport="WSS",
                    host="mYn6S3lQaKjo.invalid",
                    parameters=Parameters(branch="z9hG4bKgD24yaj"),
                )
            ],
        )
        self.assertEqual(message.www_authenticate, None)

        self.assertEqual(bytes(message), self.REQUEST_FULL_BYTES)

    def test_request_compact_form(self) -> None:
        self._test_request(self.REQUEST_COMPACT_BYTES)

    def test_request_full_form(self) -> None:
        self._test_request(self.REQUEST_FULL_BYTES)

    def test_response(self) -> None:
        message_bytes = lf2crlf(
            b"""SIP/2.0 200 OK
Via: SIP/2.0/WSS K1IXduq1pcuX.invalid;branch=z9hG4bKAVaf5Tk;received=80.200.136.90;rport=54087
From: <sip:alice@atlanta.com>;tag=8hZmsuF0Kb
To: <sip:alice@atlanta.com>;tag=Bg8X3vvKyrmKH
Call-ID: t87Br1RHAoBz2FsrKKk6hV
CSeq: 1 REGISTER
Date: Thu, 01 Feb 2018 11:29:53 GMT
User-Agent: FreeSWITCH-mod_sofia/1.6.20-37-987c9b9~64bit
Allow: INVITE, ACK, BYE, CANCEL, OPTIONS, MESSAGE, INFO, UPDATE, REGISTER, REFER, NOTIFY, PUBLISH, SUBSCRIBE
Supported: timer, path, replaces
Content-Length: 0

"""
        )

        message = Message.parse(message_bytes)
        assert isinstance(message, Response)

        self.assertEqual(message.code, 200)
        self.assertEqual(message.phrase, "OK")
        self.assertEqual(message.body, b"")

        self.assertEqual(bytes(message), message_bytes)

    def test_header_authorization(self) -> None:
        request = dummy_message()

        request.authorization = AUTHORIZATION
        self.assertEqual(request.authorization, AUTHORIZATION)
        self.assertMessageHeaders(
            request,
            [
                'Authorization: Digest username="Alice", realm="atlanta.com", '
                'nonce="84a4cc6f3082121f32b42a2187831a9e", '
                'response="7587245234b3434cc3412213e5f113a5432"'
            ],
        )

        request.authorization = None
        self.assertEqual(request.authorization, None)
        self.assertMessageHeaders(request, [])

    def test_header_call_id(self) -> None:
        request = dummy_message()

        with self.assertRaises(KeyError):
            request.call_id

        request.call_id = "abc"
        self.assertEqual(request.call_id, "abc")
        self.assertMessageHeaders(request, ["Call-ID: abc"])

    def test_header_contact(self) -> None:
        request = dummy_message()

        self.assertEqual(request.contact, [])
        request.contact = [ADDRESS]
        self.assertEqual(request.contact, [ADDRESS])
        self.assertMessageHeaders(request, ["Contact: <sip:example.com>"])

    def test_header_content_length(self) -> None:
        request = dummy_message()

        request.content_length = 10
        self.assertEqual(request.content_length, 10)
        self.assertMessageHeaders(request, ["Content-Length: 10"])

        request.content_length = None
        self.assertEqual(request.content_length, None)
        self.assertMessageHeaders(request, [])

    def test_header_content_type(self) -> None:
        request = dummy_message()

        request.content_type = "application/sdp"
        self.assertEqual(request.content_type, "application/sdp")
        self.assertMessageHeaders(request, ["Content-Type: application/sdp"])

        request.content_type = None
        self.assertEqual(request.content_type, None)
        self.assertMessageHeaders(request, [])

    def test_header_cseq(self) -> None:
        request = dummy_message()

        with self.assertRaises(KeyError):
            request.cseq

        request.cseq = CSEQ
        self.assertEqual(request.cseq, CSEQ)
        self.assertMessageHeaders(request, ["CSeq: 1 OPTIONS"])

    def test_header_date(self) -> None:
        request = dummy_message()

        self.assertEqual(request.date, None)

        request.date = datetime.datetime(
            2010, 11, 14, 0, 29, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")
        )
        self.assertEqual(
            request.date,
            datetime.datetime(2010, 11, 13, 23, 29, tzinfo=datetime.timezone.utc),
        )
        self.assertMessageHeaders(request, ["Date: Sat, 13 Nov 2010 23:29:00 GMT"])

        request.date = None
        self.assertEqual(request.date, None)
        self.assertMessageHeaders(request, [])

    def test_header_from_address(self) -> None:
        request = dummy_message()

        with self.assertRaises(KeyError):
            request.from_address

        request.from_address = ADDRESS
        self.assertEqual(request.from_address, ADDRESS)
        self.assertMessageHeaders(request, ["From: <sip:example.com>"])

    def test_header_max_forwards(self) -> None:
        request = dummy_message()

        self.assertEqual(request.max_forwards, None)

        request.max_forwards = 1
        self.assertEqual(request.max_forwards, 1)
        self.assertMessageHeaders(request, ["Max-Forwards: 1"])

    def test_header_proxy_authenticate(self) -> None:
        request = dummy_message()

        request.proxy_authenticate = AUTHENTICATE
        self.assertEqual(request.proxy_authenticate, AUTHENTICATE)
        self.assertMessageHeaders(
            request,
            [
                'Proxy-Authenticate: Digest realm="atlanta.com", domain="sip:boxesbybob.com", '
                'qop="auth", nonce="f84f1cec41e6cbe5aea9c8e88d359", opaque="", stale=FALSE, '
                "algorithm=MD5"
            ],
        )

        request.proxy_authenticate = None
        self.assertEqual(request.proxy_authenticate, None)
        self.assertMessageHeaders(request, [])

    def test_header_proxy_authorization(self) -> None:
        request = dummy_message()

        request.proxy_authorization = AUTHORIZATION
        self.assertEqual(request.proxy_authorization, AUTHORIZATION)
        self.assertMessageHeaders(
            request,
            [
                'Proxy-Authorization: Digest username="Alice", realm="atlanta.com", '
                'nonce="84a4cc6f3082121f32b42a2187831a9e", '
                'response="7587245234b3434cc3412213e5f113a5432"'
            ],
        )

        request.proxy_authorization = None
        self.assertEqual(request.proxy_authorization, None)
        self.assertMessageHeaders(request, [])

    def test_header_record_route(self) -> None:
        request = dummy_message()

        self.assertEqual(request.record_route, [])

        request.record_route = [ADDRESS]
        self.assertEqual(request.record_route, [ADDRESS])
        self.assertMessageHeaders(request, ["Record-Route: <sip:example.com>"])

    def test_header_route(self) -> None:
        request = dummy_message()

        self.assertEqual(request.route, [])

        request.route = [ADDRESS]
        self.assertEqual(request.route, [ADDRESS])
        self.assertMessageHeaders(request, ["Route: <sip:example.com>"])

    def test_header_server(self) -> None:
        request = dummy_message()

        self.assertEqual(request.server, None)

        request.server = "HomeServer v2"
        self.assertEqual(request.server, "HomeServer v2")
        self.assertMessageHeaders(request, ["Server: HomeServer v2"])

    def test_header_subject(self) -> None:
        request = dummy_message()

        self.assertEqual(request.subject, None)

        request.subject = "Need more boxes"
        self.assertEqual(request.subject, "Need more boxes")
        self.assertMessageHeaders(request, ["Subject: Need more boxes"])

    def test_header_to_address(self) -> None:
        request = dummy_message()

        with self.assertRaises(KeyError):
            request.to_address

        request.to_address = ADDRESS
        self.assertEqual(request.to_address, ADDRESS)
        self.assertMessageHeaders(request, ["To: <sip:example.com>"])

    def test_header_user_agent(self) -> None:
        request = dummy_message()

        self.assertEqual(request.user_agent, None)

        request.user_agent = "Tester/0.1.0"
        self.assertEqual(request.user_agent, "Tester/0.1.0")
        self.assertMessageHeaders(request, ["User-Agent: Tester/0.1.0"])

        request.user_agent = None
        self.assertEqual(request.user_agent, None)
        self.assertMessageHeaders(request, [])

    def test_header_via(self) -> None:
        request = dummy_message()

        self.assertEqual(request.via, [])

        request.via = [VIA]
        self.assertEqual(request.via, [VIA])
        self.assertMessageHeaders(
            request, ["Via: SIP/2.0/WSS mYn6S3lQaKjo.invalid;branch=z9hG4bKgD24yaj"]
        )

    def test_header_www_authenticate(self) -> None:
        request = dummy_message()

        request.www_authenticate = AUTHENTICATE
        self.assertEqual(request.www_authenticate, AUTHENTICATE)
        self.assertMessageHeaders(
            request,
            [
                'WWW-Authenticate: Digest realm="atlanta.com", domain="sip:boxesbybob.com", '
                'qop="auth", nonce="f84f1cec41e6cbe5aea9c8e88d359", opaque="", stale=FALSE, '
                "algorithm=MD5"
            ],
        )

        request.www_authenticate = None
        self.assertEqual(request.www_authenticate, None)
        self.assertMessageHeaders(request, [])

    def test_not_bytes(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Message.parse("SIP/2.0 200 OK")  # type: ignore
        self.assertEqual(str(cm.exception), "SIP message must be passed as bytes")

    def test_too_few_lines(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Message.parse(b"SIP/2.0 200 OK")
        self.assertEqual(str(cm.exception), "SIP message has too few lines")

    def test_neither_request_nor_response(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Message.parse(b"SIP/3.0\r\n\r\n")
        self.assertEqual(
            str(cm.exception), "SIP message is neither request nor response"
        )
