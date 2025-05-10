sipmessage
==========

.. image:: https://img.shields.io/pypi/l/sipmessage.svg
   :target: https://pypi.python.org/pypi/sipmessage
   :alt: License

.. image:: https://img.shields.io/pypi/v/sipmessage.svg
   :target: https://pypi.python.org/pypi/sipmessage
   :alt: Version

.. image:: https://github.com/spacinov/sipmessage/workflows/tests/badge.svg
   :target: https://github.com/spacinov/sipmessage/actions
   :alt: Tests

.. image:: https://img.shields.io/codecov/c/github/spacinov/sipmessage.svg
   :target: https://codecov.io/gh/spacinov/sipmessage
   :alt: Coverage

The ``sipmessage`` project provides a set of Python helpers and structures
for parsing and serialising SIP messages. It can be used to manipulate either
either entire :doc:`requests and responses <messages>` or individual
:doc:`header values <headers>`.

Example
-------

.. code:: python

    from sipmessage import Message, Parameters, Request, Via

    request = Message.parse(
        b"REGISTER sip:atlanta.com SIP/2.0\r\n"
        b"Via: SIP/2.0/WSS mYn6S3lQaKjo.invalid;branch=z9hG4bKgD24yaj\r\n"
        b"Max-Forwards: 70\r\n"
        b"To: <sip:alice@atlanta.com>\r\n"
        b"From: <sip:alice@atlanta.com>;tag=69piINLbAb\r\n"
        b"Call-ID: t87Br1RHAoBz2FsrKKk6hV\r\n"
        b"CSeq: 1 REGISTER\r\n"
        b"Contact: <sip:Mk9sZp5Z@mYn6S3lQaKjo.invalid;transport=ws>;expires=300\r\n"
        b"User-Agent: Tester/0.1.0\r\n"
        b"Content-Length: 0\r\n\r\n"
    )
    assert isinstance(request, Request)
    assert request.via == [
        Via(
            transport="WSS",
            host="mYn6S3lQaKjo.invalid",
            port=None,
            parameters=Parameters(branch="z9hG4bKgD24yaj"),
        )
    ]


API Reference
-------------

.. toctree::
   :maxdepth: 2

   messages
   headers
   license
