#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import unittest

from sipmessage.uri import URI


class URITest(unittest.TestCase):
    def test_host(self) -> None:
        uri = URI.parse("sip:atlanta.com")

        self.assertEqual(uri.host, "atlanta.com")
        self.assertEqual(uri.port, None)
        self.assertEqual(uri.user, None)
        self.assertEqual(uri.password, None)
        self.assertEqual(uri.parameters, {})

        self.assertEqual(uri.global_phone_number, None)
        self.assertEqual(str(uri), "sip:atlanta.com")

    def test_host_and_parameter_without_value(self) -> None:
        uri = URI.parse("sip:1.2.3.4;lr")

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

    def test_user_and_host(self) -> None:
        uri = URI.parse("sip:alice@atlanta.com")

        self.assertEqual(uri.host, "atlanta.com")
        self.assertEqual(uri.port, None)
        self.assertEqual(uri.user, "alice")
        self.assertEqual(uri.password, None)
        self.assertEqual(uri.parameters, {})

        self.assertEqual(uri.global_phone_number, None)
        self.assertEqual(str(uri), "sip:alice@atlanta.com")

    def test_user_and_host_and_parameters(self) -> None:
        uri = URI.parse("sip:alice@atlanta.com;maddr=239.255.255.1;ttl=15")

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
        uri = URI.parse("sip:+123456789@1.2.3.4")

        self.assertEqual(uri.host, "1.2.3.4")
        self.assertEqual(uri.port, None)
        self.assertEqual(uri.user, "+123456789")
        self.assertEqual(uri.password, None)
        self.assertEqual(uri.parameters, {})

        self.assertEqual(uri.global_phone_number, "+123456789")
        self.assertEqual(str(uri), "sip:+123456789@1.2.3.4")

    def test_full(self) -> None:
        uri = URI.parse("sip:alice:secret@atlanta.com:5060;maddr=239.255.255.1;ttl=15")

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
