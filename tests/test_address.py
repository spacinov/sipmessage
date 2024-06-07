#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import unittest

from sipmessage import URI, Address, Parameters


class AddressTest(unittest.TestCase):
    def test_empty(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Address.parse("")
        self.assertEqual(str(cm.exception), "Address is not valid")

    def test_invalid_uri(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Address.parse("atlanta.com")
        self.assertEqual(str(cm.exception), "URI is not valid")

    def test_no_brackets(self) -> None:
        contact = Address.parse("sip:+12125551212@phone2net.com;tag=887s")
        self.assertEqual(
            contact,
            Address(
                uri=URI(
                    scheme="sip",
                    user="+12125551212",
                    host="phone2net.com",
                ),
                parameters=Parameters({"tag": "887s"}),
            ),
        )
        self.assertEqual(str(contact), "<sip:+12125551212@phone2net.com>;tag=887s")

    def test_display_name_no_quotes(self) -> None:
        contact = Address.parse(
            "Anonymous  User\t! <sip:c8oqz84zk7z@privacy.org>;tag=hyh8"
        )
        self.assertEqual(
            contact,
            Address(
                name="Anonymous User !",
                uri=URI(
                    scheme="sip",
                    user="c8oqz84zk7z",
                    host="privacy.org",
                ),
                parameters=Parameters({"tag": "hyh8"}),
            ),
        )
        self.assertEqual(
            str(contact), '"Anonymous User !" <sip:c8oqz84zk7z@privacy.org>;tag=hyh8'
        )

    def test_display_name_with_quotes(self) -> None:
        contact = Address.parse('"Bob" <sips:bob@biloxi.com> ;tag=a48s')
        self.assertEqual(
            contact,
            Address(
                name="Bob",
                uri=URI(
                    scheme="sips",
                    user="bob",
                    host="biloxi.com",
                ),
                parameters=Parameters({"tag": "a48s"}),
            ),
        )
        self.assertEqual(str(contact), '"Bob" <sips:bob@biloxi.com>;tag=a48s')

    def test_display_name_with_quotes_no_space(self) -> None:
        contact = Address.parse('"Bob"<sips:bob@biloxi.com>;tag=a48s')
        self.assertEqual(
            contact,
            Address(
                name="Bob",
                uri=URI(
                    scheme="sips",
                    user="bob",
                    host="biloxi.com",
                ),
                parameters=Parameters({"tag": "a48s"}),
            ),
        )
        self.assertEqual(str(contact), '"Bob" <sips:bob@biloxi.com>;tag=a48s')

    def test_display_name_with_quotes_escape(self) -> None:
        contact = Address.parse(
            '"Bob \\"foo\\" \\\\backslashes \\\\\\\\ <bar>" '
            "<sips:bob@biloxi.com> ;tag=a48s"
        )
        self.assertEqual(
            contact,
            Address(
                name='Bob "foo" \\backslashes \\\\ <bar>',
                uri=URI(
                    scheme="sips",
                    user="bob",
                    host="biloxi.com",
                ),
                parameters=Parameters({"tag": "a48s"}),
            ),
        )
        self.assertEqual(
            str(contact),
            '"Bob \\"foo\\" \\\\backslashes \\\\\\\\ <bar>" '
            "<sips:bob@biloxi.com>;tag=a48s",
        )

    def test_with_parameter_without_value(self) -> None:
        contact = Address.parse("<sip:1.2.3.4;lr>")
        self.assertEqual(
            contact,
            Address(
                uri=URI(
                    scheme="sip", host="1.2.3.4", parameters=Parameters({"lr": None})
                )
            ),
        )
        self.assertEqual(str(contact), "<sip:1.2.3.4;lr>")

    def test_rfc4475_badinv01_contact(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Address.parse('"Joe" <sip:joe@example.org>;;;;')
        self.assertEqual(str(cm.exception), "Address is not valid")

    def test_rfc4475_esc01_contact(self) -> None:
        contact = Address.parse(
            "<sip:cal%6Cer@host5.example.net;%6C%72;n%61me=v%61lue%25%34%31>"
        )
        self.assertEqual(
            contact,
            Address(
                uri=URI(
                    scheme="sip",
                    user="caller",
                    host="host5.example.net",
                    parameters=Parameters({"lr": None, "name": "value%41"}),
                ),
            ),
        )
        self.assertEqual(
            str(contact),
            "<sip:caller@host5.example.net;lr;name=value%2541>",
        )

    def test_rfc4475_esc02_from(self) -> None:
        contact = Address.parse('"%Z%45" <sip:resource@example.com>;tag=f232jadfj23')
        self.assertEqual(
            contact,
            Address(
                name="%Z%45",
                uri=URI(
                    scheme="sip",
                    user="resource",
                    host="example.com",
                ),
                parameters=Parameters({"tag": "f232jadfj23"}),
            ),
        )
        self.assertEqual(
            str(contact), '"%Z%45" <sip:resource@example.com>;tag=f232jadfj23'
        )

    def test_rfc4475_escnull_from(self) -> None:
        contact = Address.parse("sip:null-%00-null@example.com;tag=839923423")
        self.assertEqual(
            contact,
            Address(
                uri=URI(
                    scheme="sip",
                    host="example.com",
                    user="null-\x00-null",
                ),
                parameters=Parameters({"tag": "839923423"}),
            ),
        )
        self.assertEqual(str(contact), "<sip:null-%00-null@example.com>;tag=839923423")

    def test_rfc4475_intmeth_to(self) -> None:
        contact = Address.parse(
            '"BEL:\x07 NUL:\x00 DEL:\x7f" '
            "<sip:1_unusual.URI~(to-be!sure)&isn't+it$/crazy?,/;;*@example.com>"
        )
        self.assertEqual(
            contact,
            Address(
                name="BEL:\x07 NUL:\x00 DEL:\x7f",
                uri=URI(
                    scheme="sip",
                    user="1_unusual.URI~(to-be!sure)&isn't+it$/crazy?,/;;*",
                    host="example.com",
                ),
            ),
        )
        self.assertEqual(
            str(contact),
            '"BEL:\x07 NUL:\x00 DEL:\x7f" '
            "<sip:1_unusual.URI~(to-be!sure)&isn't+it$/crazy?,/;;*@example.com>",
        )

    def test_trailing_comma(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Address.parse("<sip:1.2.3.4;lr>,")
        self.assertEqual(str(cm.exception), "Address is not valid")


class AddressParseManyTest(unittest.TestCase):
    def test_simple(self) -> None:
        contacts = Address.parse_many(
            "<sip:alice@atlanta.com>, <sip:bob@biloxi.com>, <sip:carol@chicago.com>"
        )
        self.assertEqual(
            contacts,
            [
                Address(uri=URI(scheme="sip", host="atlanta.com", user="alice")),
                Address(uri=URI(scheme="sip", host="biloxi.com", user="bob")),
                Address(uri=URI(scheme="sip", host="chicago.com", user="carol")),
            ],
        )

    def test_trailing_garbage(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Address.parse_many("<sip:1.2.3.4;lr>$")
        self.assertEqual(str(cm.exception), "Address is not valid")

    def test_trailing_comma(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Address.parse_many("<sip:1.2.3.4;lr>,")
        self.assertEqual(str(cm.exception), "Address is not valid")
