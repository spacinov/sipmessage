#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

"""
Collected rules from RFC 3261.
https://datatracker.ietf.org/doc/html/rfc3261
"""

from abnf.grammars import rfc3986
from abnf.grammars.misc import load_grammar_rules
from abnf.parser import Rule as _Rule


@load_grammar_rules(
    [
        ("absolute-URI", rfc3986.Rule("absolute-URI")),
        ("host", rfc3986.Rule("host")),
    ]
)
class Rule(_Rule):
    """Rules from RFC 3261."""

    grammar = [
        "alphanum           =  ALPHA / DIGIT",
        "LWS                =  [*WSP CRLF] 1*WSP ; linear whitespace",
        "SWS                =  [LWS] ; sep whitespace",
        "UTF8-NONASCII      =  %xC0-DF 1UTF8-CONT\
                               / %xE0-EF 2UTF8-CONT\
                               / %xF0-F7 3UTF8-CONT\
                               / %xF8-Fb 4UTF8-CONT\
                               / %xFC-FD 5UTF8-CONT",
        "UTF8-CONT          =  %x80-BF",
        'EQUAL              =  SWS "=" SWS ; equal',
        'RAQUOT             =  ">" SWS ; right angle quote',
        'LAQUOT             =  SWS "<"; left angle quote',
        'SEMI               =  SWS ";" SWS ; semicolon',
        'token              =  1*(alphanum / "-" / "." / "!" / "%" / "*"\
                               / "_" / "+" / "`" / "\'" / "~" )',
        "quoted-string      =  SWS DQUOTE *(qdtext / quoted-pair ) DQUOTE",
        "qdtext             =  LWS / %x21 / %x23-5B / %x5D-7E\
                               / UTF8-NONASCII",
        'quoted-pair        =  "\\" (%x00-09 / %x0B-0C / %x0E-7F)',
        "generic-param      =  token [ EQUAL gen-value ]",
        "gen-value          =  token / host / quoted-string",
        "contact-param      =  (name-addr / addr-spec) *(SEMI contact-params)",
        "name-addr          =  [ display-name ] LAQUOT addr-spec RAQUOT",
        # Not according to RFC, but good enough.
        "addr-spec          =  absolute-URI",
        "display-name       =  *(token LWS) / quoted-string",
        # Not according to RFC, but good enough.
        "contact-params     =  contact-extension",
        "contact-extension  =  generic-param",
    ]
