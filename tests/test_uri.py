#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import unittest

from sipmessage import URI


class URITest(unittest.TestCase):
    def test_invalid_parameters(self) -> None:
        with self.assertRaises(ValueError) as cm:
            URI.parse("sip:atlanta.com;")
        self.assertEqual(str(cm.exception), "URI is not valid")

    def test_invalid_port(self) -> None:
        # No port.
        with self.assertRaises(ValueError) as cm:
            URI.parse("sip:atlanta.com:")
        self.assertEqual(str(cm.exception), "URI is not valid")

        # Invalid port.
        with self.assertRaises(ValueError) as cm:
            URI.parse("sip:atlanta.com:bob")
        self.assertEqual(str(cm.exception), "URI is not valid")

    def test_invalid_scheme(self) -> None:
        # No scheme.
        with self.assertRaises(ValueError) as cm:
            URI.parse("atlanta.com")
        self.assertEqual(str(cm.exception), "URI is not valid")

        # Invalid scheme.
        with self.assertRaises(ValueError) as cm:
            URI.parse("bogus:atlanta.com")
        self.assertEqual(str(cm.exception), "URI is not valid")

    def test_host(self) -> None:
        uri = URI.parse("sip:atlanta.com")

        self.assertEqual(uri.scheme, "sip")
        self.assertEqual(uri.host, "atlanta.com")
        self.assertEqual(uri.port, None)
        self.assertEqual(uri.user, None)
        self.assertEqual(uri.password, None)
        self.assertEqual(uri.parameters, {})

        self.assertEqual(uri.global_phone_number, None)
        self.assertEqual(str(uri), "sip:atlanta.com")

    def test_host_and_parameter_without_value(self) -> None:
        uri = URI.parse("sip:1.2.3.4;lr")

        self.assertEqual(uri.scheme, "sip")
        self.assertEqual(uri.host, "1.2.3.4")
        self.assertEqual(uri.port, None)
        self.assertEqual(uri.user, None)
        self.assertEqual(uri.password, None)
        self.assertEqual(
            uri.parameters,
            {"lr": None},
        )

        self.assertEqual(uri.global_phone_number, None)
        self.assertEqual(str(uri), "sip:1.2.3.4;lr")

    def test_user(self) -> None:
        uri = URI.parse("sip:alice@atlanta.com")

        self.assertEqual(uri.scheme, "sip")
        self.assertEqual(uri.host, "atlanta.com")
        self.assertEqual(uri.port, None)
        self.assertEqual(uri.user, "alice")
        self.assertEqual(uri.password, None)
        self.assertEqual(uri.parameters, {})

        self.assertEqual(uri.global_phone_number, None)
        self.assertEqual(str(uri), "sip:alice@atlanta.com")

    def test_user_escaped(self) -> None:
        uri = URI.parse("sip:sips%3Auser%40example.com@example.net")

        self.assertEqual(uri.scheme, "sip")
        self.assertEqual(uri.host, "example.net")
        self.assertEqual(uri.port, None)
        self.assertEqual(uri.user, "sips:user@example.com")
        self.assertEqual(uri.password, None)
        self.assertEqual(uri.parameters, {})

        self.assertEqual(str(uri), "sip:sips%3Auser%40example.com@example.net")

    def test_user_question_mark(self) -> None:
        uri = URI.parse("sip:alice?@atlanta.com")

        self.assertEqual(uri.scheme, "sip")
        self.assertEqual(uri.host, "atlanta.com")
        self.assertEqual(uri.port, None)
        self.assertEqual(uri.user, "alice?")
        self.assertEqual(uri.password, None)
        self.assertEqual(uri.parameters, {})

        self.assertEqual(uri.global_phone_number, None)
        self.assertEqual(str(uri), "sip:alice?@atlanta.com")

    def test_user_and_parameters(self) -> None:
        uri = URI.parse("sip:alice@atlanta.com;maddr=239.255.255.1;ttl=15")

        self.assertEqual(uri.scheme, "sip")
        self.assertEqual(uri.host, "atlanta.com")
        self.assertEqual(uri.port, None)
        self.assertEqual(uri.user, "alice")
        self.assertEqual(uri.password, None)
        self.assertEqual(
            uri.parameters,
            {
                "maddr": "239.255.255.1",
                "ttl": "15",
            },
        )

        self.assertEqual(uri.global_phone_number, None)
        self.assertEqual(str(uri), "sip:alice@atlanta.com;maddr=239.255.255.1;ttl=15")

    def test_phone_identity(self) -> None:
        uri = URI.parse("sips:+123456789@1.2.3.4")

        self.assertEqual(uri.scheme, "sips")
        self.assertEqual(uri.host, "1.2.3.4")
        self.assertEqual(uri.port, None)
        self.assertEqual(uri.user, "+123456789")
        self.assertEqual(uri.password, None)
        self.assertEqual(uri.parameters, {})

        self.assertEqual(uri.global_phone_number, "+123456789")
        self.assertEqual(str(uri), "sips:+123456789@1.2.3.4")

    def test_full(self) -> None:
        uri = URI.parse("sip:alice:secret@atlanta.com:5060;maddr=239.255.255.1;ttl=15")

        self.assertEqual(uri.scheme, "sip")
        self.assertEqual(uri.host, "atlanta.com")
        self.assertEqual(uri.port, 5060)
        self.assertEqual(uri.user, "alice")
        self.assertEqual(uri.password, "secret")
        self.assertEqual(
            uri.parameters,
            {
                "maddr": "239.255.255.1",
                "ttl": "15",
            },
        )

        self.assertEqual(uri.global_phone_number, None)
        self.assertEqual(
            str(uri), "sip:alice:secret@atlanta.com:5060;maddr=239.255.255.1;ttl=15"
        )

    def test_password(self) -> None:
        uri = URI.parse("sip:alice:secret@atlanta.com")

        self.assertEqual(uri.scheme, "sip")
        self.assertEqual(uri.host, "atlanta.com")
        self.assertEqual(uri.port, None)
        self.assertEqual(uri.user, "alice")
        self.assertEqual(uri.password, "secret")
        self.assertEqual(uri.parameters, {})

        self.assertEqual(str(uri), "sip:alice:secret@atlanta.com")

    def test_password_escaped(self) -> None:
        uri = URI.parse("sip:alice:sips%3Auser%40example.com@atlanta.com")

        self.assertEqual(uri.scheme, "sip")
        self.assertEqual(uri.host, "atlanta.com")
        self.assertEqual(uri.port, None)
        self.assertEqual(uri.user, "alice")
        self.assertEqual(uri.password, "sips:user@example.com")
        self.assertEqual(uri.parameters, {})

        self.assertEqual(str(uri), "sip:alice:sips%3Auser%40example.com@atlanta.com")

    def test_rfc4475_wide_range_of_valid_characters(self) -> None:
        uri = URI.parse(
            "sip:1_unusual.URI~(to-be!sure)&isn't+it$/crazy?,/;;*:&it+has=1,weird!*pas$wo~d_too.(doesn't-it)@example.com"
        )
        self.assertEqual(uri.host, "example.com")
        self.assertEqual(uri.port, None)
        self.assertEqual(uri.user, "1_unusual.URI~(to-be!sure)&isn't+it$/crazy?,/;;*")
        self.assertEqual(uri.password, "&it+has=1,weird!*pas$wo~d_too.(doesn't-it)")
        self.assertEqual(uri.parameters, {})
        self.assertEqual(
            str(uri),
            "sip:1_unusual.URI~(to-be!sure)&isn't+it$/crazy?,/;;*:&it+has=1,weird!*pas$wo~d_too.(doesn't-it)@example.com",
        )
