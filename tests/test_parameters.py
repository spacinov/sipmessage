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
        self.assertEqual(len(parameters), 0)
        self.assertEqual(repr(parameters), "Parameters()")
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

    def test_replace(self) -> None:
        parameters1 = Parameters(foo="1", bar=None)
        parameters2 = parameters1.replace(tag="blah")

        self.assertEqual(str(parameters1), ";foo=1;bar")
        self.assertEqual(str(parameters2), ";foo=1;bar;tag=blah")

    def test_simple(self) -> None:
        parameters = Parameters.parse(";foo=1;bar")
        self.assertEqual(parameters, {"foo": "1", "bar": None})
        self.assertEqual(len(parameters), 2)
        self.assertEqual(repr(parameters), "Parameters(foo='1', bar=None)")
        self.assertEqual(str(parameters), ";foo=1;bar")

        # Check mapping access.
        self.assertTrue("foo" in parameters)
        self.assertTrue("bar" in parameters)
        self.assertFalse("baz" in parameters)

        self.assertEqual(parameters["foo"], "1")
        self.assertEqual(parameters["bar"], None)
        with self.assertRaises(KeyError):
            parameters["baz"]

        self.assertEqual(parameters.get("foo"), "1")
        self.assertEqual(parameters.get("bar"), None)
        self.assertEqual(parameters.get("baz"), None)

    def test_spaces(self) -> None:
        parameters = Parameters.parse(" ; foo  =  1  ;  bar ")
        self.assertEqual(parameters, {"foo": "1", "bar": None})
        self.assertEqual(str(parameters), ";foo=1;bar")
