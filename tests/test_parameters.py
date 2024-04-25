#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import unittest

from sipmessage.parameters import Parameters


class ParametersTest(unittest.TestCase):
    def test_empty(self) -> None:
        parameters = Parameters.parse("")
        self.assertEqual(parameters, {})
        self.assertEqual(str(parameters), "")

    def test_not_empty(self) -> None:
        parameters = Parameters.parse("foo=1;bar")
        self.assertEqual(parameters, {"foo": "1", "bar": None})
        self.assertEqual(str(parameters), "foo=1;bar")
