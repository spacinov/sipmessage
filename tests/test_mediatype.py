#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import unittest

from sipmessage import MediaType, Parameters


class MediaTypeTest(unittest.TestCase):
    def test_empty(self) -> None:
        with self.assertRaises(ValueError) as cm:
            MediaType.parse("")
        self.assertEqual(str(cm.exception), "MediaType is not valid")

    def test_any(self) -> None:
        media_type = MediaType.parse("*/*")
        self.assertEqual(media_type, MediaType(mime_type="*/*"))
        self.assertEqual(str(media_type), "*/*")

    def test_any_subtype(self) -> None:
        media_type = MediaType.parse("image/*")
        self.assertEqual(media_type, MediaType(mime_type="image/*"))
        self.assertEqual(str(media_type), "image/*")

    def test_simple(self) -> None:
        media_type = MediaType.parse("application/sdp")
        self.assertEqual(media_type, MediaType(mime_type="application/sdp"))
        self.assertEqual(str(media_type), "application/sdp")

    def test_parameters(self) -> None:
        media_type = MediaType.parse("text/html; charset=utf-8")
        self.assertEqual(
            media_type,
            MediaType(mime_type="text/html", parameters=Parameters(charset="utf-8")),
        )
        self.assertEqual(str(media_type), "text/html;charset=utf-8")

    def test_trailing_comma(self) -> None:
        with self.assertRaises(ValueError) as cm:
            MediaType.parse("application/sdp,")
        self.assertEqual(str(cm.exception), "MediaType is not valid")


class MediaTypeParseManyTest(unittest.TestCase):
    def test_simple(self) -> None:
        media_types = MediaType.parse_many("application/sdp, foo/bar")
        self.assertEqual(
            media_types,
            [MediaType(mime_type="application/sdp"), MediaType(mime_type="foo/bar")],
        )
