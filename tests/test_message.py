#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import unittest

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


def dummy_message() -> Request:
    return Request("OPTIONS", URI(scheme="sip", host="example.com"))


def lf2crlf(x: str) -> str:
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

    def test_set(self) -> None:
        headers = Headers()

        headers.set("To", "Bob <sip:bob@biloxi.com>")
        self.assertEqual(
            str(headers),
            lf2crlf("""To: Bob <sip:bob@biloxi.com>

"""),
        )

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


class MessageTest(unittest.TestCase):
    maxDiff = None

    def assertMessageHeaders(self, request: Message, values: list[str]) -> None:
        self.assertEqual(str(request).split("\r\n")[1:-2], values)

    def test_request(self) -> None:
        message_str = lf2crlf(
            """REGISTER sip:atlanta.com SIP/2.0
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

        message = Message.parse(message_str)
        assert isinstance(message, Request)

        self.assertEqual(message.method, "REGISTER")
        self.assertEqual(message.uri, URI(scheme="sip", host="atlanta.com"))
        self.assertEqual(message.body, "")

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

        self.assertEqual(str(message), message_str)

    def test_response(self) -> None:
        message_str = lf2crlf(
            """SIP/2.0 200 OK
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

        message = Message.parse(message_str)
        assert isinstance(message, Response)

        self.assertEqual(message.code, 200)
        self.assertEqual(message.phrase, "OK")
        self.assertEqual(message.body, "")

        self.assertEqual(str(message), message_str)

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

    def test_too_few_lines(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Message.parse("SIP/2.0 200 OK")
        self.assertEqual(str(cm.exception), "SIP message has too few lines")

    def test_neither_request_nor_response(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Message.parse("SIP/3.0\r\n")
        self.assertEqual(
            str(cm.exception), "SIP message is neither request nor response"
        )
