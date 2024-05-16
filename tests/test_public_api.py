#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import unittest

import sipmessage


class MetadataTests(unittest.TestCase):
    def test_version(self) -> None:
        version = sipmessage.__version__
        self.assertIn(".", version)
