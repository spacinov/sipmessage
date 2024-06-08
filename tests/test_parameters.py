#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import unittest

from sipmessage import Parameters


class ParametersTest(unittest.TestCase):
    def test_empty(self) -> None:
        parameters = Parameters.parse("")
        self.assertEqual(parameters, {})
        self.assertEqual(str(parameters), "")

    def test_escaped(self) -> None:
        parameters = Parameters.parse(";%6C%72;n%61me=v%61lue%25%34%31")
        self.assertEqual(parameters, {"lr": None, "name": "value%41"})
        self.assertEqual(str(parameters), ";lr;name=value%2541")

    def test_invalid(self) -> None:
        for s in ["a", ";", " ; ", ";;;", " ; ; ;"]:
            with self.assertRaises(ValueError) as cm:
                Parameters.parse(s)
            self.assertEqual(str(cm.exception), "Parameters are not valid")

    def test_simple(self) -> None:
        parameters = Parameters.parse(";foo=1;bar")
        self.assertEqual(parameters, {"foo": "1", "bar": None})
        self.assertEqual(str(parameters), ";foo=1;bar")

    def test_spaces(self) -> None:
        parameters = Parameters.parse(" ; foo  =  1  ;  bar ")
        self.assertEqual(parameters, {"foo": "1", "bar": None})
        self.assertEqual(str(parameters), ";foo=1;bar")
