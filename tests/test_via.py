#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import unittest

from sipmessage import Parameters, Via


class ViaTest(unittest.TestCase):
    def test_empty(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Via.parse("")
        self.assertEqual(str(cm.exception), "Via is not valid")

    def test_hostname(self) -> None:
        via = Via.parse(
            "SIP/2.0/WSS T8trJdbBz7r6.invalid;branch=z9hG4bKYJHC9fb;"
            "received=80.200.136.90;rport=49940"
        )
        self.assertEqual(
            via,
            Via(
                transport="WSS",
                host="T8trJdbBz7r6.invalid",
                parameters=Parameters(
                    branch="z9hG4bKYJHC9fb",
                    received="80.200.136.90",
                    rport="49940",
                ),
            ),
        )
        self.assertEqual(
            str(via),
            "SIP/2.0/WSS T8trJdbBz7r6.invalid;branch=z9hG4bKYJHC9fb;"
            "received=80.200.136.90;rport=49940",
        )

    def test_hostname_and_port(self) -> None:
        via = Via.parse(
            "SIP/2.0/WSS T8trJdbBz7r6.invalid:5060;branch=z9hG4bKYJHC9fb;"
            "received=80.200.136.90;rport=49940"
        )
        self.assertEqual(
            via,
            Via(
                transport="WSS",
                host="T8trJdbBz7r6.invalid",
                port=5060,
                parameters=Parameters(
                    branch="z9hG4bKYJHC9fb",
                    received="80.200.136.90",
                    rport="49940",
                ),
            ),
        )
        self.assertEqual(
            str(via),
            "SIP/2.0/WSS T8trJdbBz7r6.invalid:5060;branch=z9hG4bKYJHC9fb;"
            "received=80.200.136.90;rport=49940",
        )

    def test_ipv4(self) -> None:
        via = Via.parse(
            "SIP/2.0/WSS 1.2.3.4;branch=z9hG4bKYJHC9fb;"
            "received=80.200.136.90;rport=49940"
        )
        self.assertEqual(
            via,
            Via(
                transport="WSS",
                host="1.2.3.4",
                parameters=Parameters(
                    branch="z9hG4bKYJHC9fb",
                    received="80.200.136.90",
                    rport="49940",
                ),
            ),
        )
        self.assertEqual(
            str(via),
            "SIP/2.0/WSS 1.2.3.4;branch=z9hG4bKYJHC9fb;"
            "received=80.200.136.90;rport=49940",
        )

    def test_rfc4475_badinv01(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Via.parse("SIP/2.0/UDP 192.0.2.15;;")
        self.assertEqual(str(cm.exception), "Via is not valid")

    def test_rfc4475_intmeth(self) -> None:
        via = Via.parse("SIP/2.0/TCP host1.example.com;branch=z9hG4bK-.!%66*_+`'~")
        self.assertEqual(
            via,
            Via(
                transport="TCP",
                host="host1.example.com",
                parameters=Parameters(branch="z9hG4bK-.!f*_+`'~"),
            ),
        )
        # FIXME: this is unnecessarily quoted
        self.assertEqual(
            str(via), "SIP/2.0/TCP host1.example.com;branch=z9hG4bK-.%21f%2A_%2B%60%27~"
        )

    def test_rfc4475_wsinv(self) -> None:
        via = Via.parse(
            "SIP  /    2.0   / UDP  192.168.255.111   ; branch = z9hG4bK30239"
        )
        self.assertEqual(
            via,
            Via(
                transport="UDP",
                host="192.168.255.111",
                parameters=Parameters(branch="z9hG4bK30239"),
            ),
        )

    def test_trailing_comma(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Via.parse("SIP/2.0/UDP 192.0.2.15,")
        self.assertEqual(str(cm.exception), "Via is not valid")


class ViaParseManyTest(unittest.TestCase):
    def test_simple(self) -> None:
        vias = Via.parse_many(
            "SIP/2.0/UDP 192.168.255.111;branch=z9hG4bK30239, "
            "SIP/2.0/WSS T8trJdbBz7r6.invalid;branch=z9hG4bKYJHC9fb"
        )
        self.assertEqual(
            vias,
            [
                Via(
                    transport="UDP",
                    host="192.168.255.111",
                    parameters=Parameters(branch="z9hG4bK30239"),
                ),
                Via(
                    transport="WSS",
                    host="T8trJdbBz7r6.invalid",
                    parameters=Parameters(branch="z9hG4bKYJHC9fb"),
                ),
            ],
        )

    def test_trailing_garbage(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Via.parse_many("SIP/2.0/UDP 192.0.2.15$")
        self.assertEqual(str(cm.exception), "Via is not valid")

    def test_trailing_comma(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Via.parse_many("SIP/2.0/UDP 192.0.2.15,")
        self.assertEqual(str(cm.exception), "Via is not valid")
