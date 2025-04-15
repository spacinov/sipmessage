#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import unittest

from sipmessage import AuthChallenge, AuthCredentials, AuthParameters


class AuthChallengeTest(unittest.TestCase):
    def test_empty(self) -> None:
        with self.assertRaises(ValueError) as cm:
            AuthChallenge.parse("")
        self.assertEqual(str(cm.exception), "AuthChallenge is not valid")

    def test_bearer(self) -> None:
        auth = AuthChallenge.parse('Bearer realm="atlanta.com"')
        self.assertEqual(
            auth,
            AuthChallenge(
                scheme="Bearer", parameters=AuthParameters(realm="atlanta.com")
            ),
        )
        self.assertEqual(str(auth), 'Bearer realm="atlanta.com"')

    def test_digest(self) -> None:
        auth = AuthChallenge.parse(
            'Digest realm="atlanta.com", '
            'domain="sip:boxesbybob.com", qop="auth", '
            'nonce="f84f1cec41e6cbe5aea9c8e88d359", '
            'opaque="", stale=FALSE, algorithm=MD5'
        )
        self.assertEqual(
            auth,
            AuthChallenge(
                scheme="Digest",
                parameters=AuthParameters(
                    realm="atlanta.com",
                    domain="sip:boxesbybob.com",
                    qop="auth",
                    nonce="f84f1cec41e6cbe5aea9c8e88d359",
                    opaque="",
                    stale="FALSE",
                    algorithm="MD5",
                ),
            ),
        )
        self.assertEqual(
            str(auth),
            'Digest realm="atlanta.com", '
            'domain="sip:boxesbybob.com", qop="auth", '
            'nonce="f84f1cec41e6cbe5aea9c8e88d359", '
            'opaque="", stale=FALSE, algorithm=MD5',
        )


class AuthCredentialsTest(unittest.TestCase):
    def test_empty(self) -> None:
        with self.assertRaises(ValueError) as cm:
            AuthCredentials.parse("")
        self.assertEqual(str(cm.exception), "AuthCredentials are not valid")

    def test_bearer(self) -> None:
        auth = AuthCredentials.parse("Bearer sometoken")
        self.assertEqual(
            auth,
            AuthCredentials(scheme="Bearer", token="sometoken"),
        )
        self.assertEqual(str(auth), "Bearer sometoken")

    def test_digest(self) -> None:
        auth = AuthCredentials.parse(
            'Digest username="bob", '
            'realm="biloxi.com", '
            'nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093", '
            'uri="sip:bob@biloxi.com", '
            'qop="auth", '
            "nc=00000001, "
            'cnonce="0a4f113b", '
            'response="6629fae49393a05397450978507c4ef1", '
            'opaque="5ccc069c403ebaf9f0171e9517f40e41"'
        )
        self.assertEqual(
            auth,
            AuthCredentials(
                scheme="Digest",
                parameters=AuthParameters(
                    username="bob",
                    realm="biloxi.com",
                    nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",
                    uri="sip:bob@biloxi.com",
                    qop="auth",
                    nc="00000001",
                    cnonce="0a4f113b",
                    response="6629fae49393a05397450978507c4ef1",
                    opaque="5ccc069c403ebaf9f0171e9517f40e41",
                ),
            ),
        )
        self.assertEqual(
            str(auth),
            'Digest username="bob", '
            'realm="biloxi.com", '
            'nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093", '
            'uri="sip:bob@biloxi.com", '
            'qop="auth", '
            "nc=00000001, "
            'cnonce="0a4f113b", '
            'response="6629fae49393a05397450978507c4ef1", '
            'opaque="5ccc069c403ebaf9f0171e9517f40e41"',
        )

    def test_invalid_constructor(self) -> None:
        with self.assertRaises(ValueError) as cm:
            AuthCredentials(scheme="Digest")
        self.assertEqual(
            str(cm.exception),
            "Exactly one of `parameters` or `token` must be set.",
        )

        with self.assertRaises(ValueError) as cm:
            AuthCredentials(
                scheme="Digest",
                parameters=AuthParameters(realm="Some Realm"),
                token="sometoken",
            )
        self.assertEqual(
            str(cm.exception),
            "Exactly one of `parameters` or `token` must be set.",
        )


class AuthParametersTest(unittest.TestCase):
    def test_empty(self) -> None:
        parameters = AuthParameters.parse("")
        self.assertEqual(parameters, {})
        self.assertEqual(len(parameters), 0)
        self.assertEqual(repr(parameters), "AuthParameters()")
        self.assertEqual(str(parameters), "")

    def test_invalid(self) -> None:
        with self.assertRaises(ValueError) as cm:
            AuthParameters.parse("a")
        self.assertEqual(str(cm.exception), "AuthParameters are not valid")

    def test_replace(self) -> None:
        parameters1 = AuthParameters(foo="1", bar="2")
        parameters2 = parameters1.replace(tag="blah")

        self.assertEqual(str(parameters1), "foo=1, bar=2")
        self.assertEqual(str(parameters2), "foo=1, bar=2, tag=blah")

    def test_simple(self) -> None:
        parameters = AuthParameters.parse("foo=1,bar=2")
        self.assertEqual(parameters, {"foo": "1", "bar": "2"})
        self.assertEqual(len(parameters), 2)
        self.assertEqual(repr(parameters), "AuthParameters(foo='1', bar='2')")
        self.assertEqual(str(parameters), "foo=1, bar=2")

        # Check mapping access.
        self.assertTrue("foo" in parameters)
        self.assertTrue("bar" in parameters)
        self.assertFalse("baz" in parameters)

        self.assertEqual(parameters["foo"], "1")
        self.assertEqual(parameters["bar"], "2")
        with self.assertRaises(KeyError):
            parameters["baz"]

        self.assertEqual(parameters.get("foo"), "1")
        self.assertEqual(parameters.get("bar"), "2")
        self.assertEqual(parameters.get("baz"), None)

    def test_spaces(self) -> None:
        parameters = AuthParameters.parse(' foo   = " 1   ",  bar  =2')
        self.assertEqual(parameters, {"foo": " 1   ", "bar": "2"})
        self.assertEqual(str(parameters), 'foo=" 1   ", bar=2')
