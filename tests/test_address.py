#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import unittest

from sipmessage import Address


class AddressTest(unittest.TestCase):
    def test_empty(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Address.parse("")
        self.assertEqual(str(cm.exception), "Not a valid address")

    def test_no_brackets(self) -> None:
        contact = Address.parse("sip:+12125551212@phone2net.com;tag=887s")
        self.assertEqual(contact.name, "")
        self.assertEqual(str(contact.uri), "sip:+12125551212@phone2net.com")
        self.assertEqual(contact.parameters, {"tag": "887s"})
        self.assertEqual(str(contact), "<sip:+12125551212@phone2net.com>;tag=887s")

    def test_no_quotes(self) -> None:
        contact = Address.parse("Anonymous <sip:c8oqz84zk7z@privacy.org>;tag=hyh8")
        self.assertEqual(contact.name, "Anonymous")
        self.assertEqual(str(contact.uri), "sip:c8oqz84zk7z@privacy.org")
        self.assertEqual(contact.parameters, {"tag": "hyh8"})
        self.assertEqual(
            str(contact), '"Anonymous" <sip:c8oqz84zk7z@privacy.org>;tag=hyh8'
        )

    def test_with_parameter_without_value(self) -> None:
        contact = Address.parse("<sip:1.2.3.4;lr>")
        self.assertEqual(contact.name, "")
        self.assertEqual(str(contact.uri), "sip:1.2.3.4;lr")

    def test_with_quotes(self) -> None:
        contact = Address.parse('"Bob" <sips:bob@biloxi.com> ;tag=a48s')
        self.assertEqual(contact.name, "Bob")
        self.assertEqual(str(contact.uri), "sips:bob@biloxi.com")
        self.assertEqual(contact.parameters, {"tag": "a48s"})
        self.assertEqual(str(contact), '"Bob" <sips:bob@biloxi.com>;tag=a48s')
