#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import unittest

from sipmessage import Via


class ViaTest(unittest.TestCase):
    def test_empty(self) -> None:
        with self.assertRaises(ValueError) as cm:
            Via.parse("")
        self.assertEqual(str(cm.exception), "Malformed Via header")

    def test_parse(self) -> None:
        via = Via.parse(
            "SIP/2.0/WSS T8trJdbBz7r6.invalid;branch=z9hG4bKYJHC9fb;received=80.200.136.90;rport=49940"
        )

        self.assertEqual(via.transport, "WSS")
        self.assertEqual(via.address, "T8trJdbBz7r6.invalid")
        self.assertEqual(
            via.parameters,
            {
                "branch": "z9hG4bKYJHC9fb",
                "received": "80.200.136.90",
                "rport": "49940",
            },
        )

        self.assertEqual(
            str(via),
            "SIP/2.0/WSS T8trJdbBz7r6.invalid;branch=z9hG4bKYJHC9fb;received=80.200.136.90;rport=49940",
        )
