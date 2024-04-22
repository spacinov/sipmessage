import unittest

import sipmessage


class MetadataTests(unittest.TestCase):
    def test_version(self) -> None:
        version = sipmessage.__version__
        self.assertIn(".", version)
