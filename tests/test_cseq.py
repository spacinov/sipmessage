#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import unittest

from sipmessage import CSeq


class ViaTest(unittest.TestCase):
    def test_empty(self) -> None:
        with self.assertRaises(ValueError) as cm:
            CSeq.parse("")
        self.assertEqual(str(cm.exception), "CSeq is not valid")

    def test_valid(self) -> None:
        cseq = CSeq.parse("9 INVITE")
        self.assertEqual(cseq, CSeq(sequence=9, method="INVITE"))
        self.assertEqual(str(cseq), "9 INVITE")

    def test_rfc4475_wsinv(self) -> None:
        cseq = CSeq.parse("  0009\r\n  INVITE ")
        self.assertEqual(cseq, CSeq(sequence=9, method="INVITE"))
        self.assertEqual(str(cseq), "9 INVITE")
