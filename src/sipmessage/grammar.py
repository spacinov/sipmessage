#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import re
import string


def cset(chars: str) -> str:
    """
    Transform a collection of characters into a regular expression
    character set.
    """
    return "[" + chars.replace("-", "\\-").replace("[", "\\[").replace("]", "\\]") + "]"


def simplify_whitespace(value: str) -> str:
    """
    Replace any whitespace by a single space.

    According to RFC 3261, all linear white space, including folding,
    has the same semantics as SP.
    """
    return re.sub(r"\s+", " ", value).strip()


# Character collections.
C_ALPHA = string.ascii_letters
C_ALPHANUM = string.ascii_letters + string.digits
C_MARK = "-_.!~*/'()"
C_TOKEN = C_ALPHANUM + "-.!%*_+`'~"
C_UNRESERVED = C_ALPHANUM + C_MARK
C_PASSWORD_SAFE = C_UNRESERVED + "&=+$,"
C_USER_SAFE = C_UNRESERVED + "&=+$,;?/"
C_URI_PARAM_SAFE = C_UNRESERVED + "[]/:&+$"

# Regular expression fragments.
ALPHA = cset(C_ALPHA)
ALPHANUM = cset(C_ALPHANUM)
DIGIT = "\\d"
HEXDIG = cset(string.hexdigits)
ESCAPED = f"%{HEXDIG}{{2}}"
LWS = "[ ]+"
SWS = "[ ]*"
TOKEN = f"{cset(C_TOKEN)}+"
QUOTED_STRING = '"(?:[^"]|\\")*"'

EQUAL = f"{SWS}={SWS}"
SEMI = f"{SWS};{SWS}"
SLASH = f"{SWS}/{SWS}"

HEXSEQ = f"{HEXDIG}{{1,4}}(?::{HEXDIG}{{1,4}})*"
HEXPART = f"(?:{HEXSEQ}|{HEXSEQ}::(?:{HEXSEQ})?|::(?:{HEXSEQ})?)"
IPV4ADDRESS = f"{DIGIT}{{1,3}}\\.{DIGIT}{{1,3}}\\.{DIGIT}{{1,3}}\\.{DIGIT}{{1,3}}"
IPV6ADDRESS = f"{HEXPART}(?::{IPV4ADDRESS})?"
IPV6REFERENCE = f"\\[{IPV6ADDRESS}\\]"

DOMAINLABEL = f"{ALPHANUM}+([\\-]+{ALPHANUM}+)*"
TOPLABEL = f"{ALPHA}+([\\-]+{ALPHANUM}+)*"
HOSTNAME = f"(?:{DOMAINLABEL}\\.)*{TOPLABEL}[\\.]?"

HOST = f"(?:{HOSTNAME}|{IPV4ADDRESS}|{IPV6REFERENCE})"
USER = f"(?:{cset(C_USER_SAFE)}|{ESCAPED})+"
PASSWORD = f"(?:{cset(C_PASSWORD_SAFE)}|{ESCAPED})+"
PORT = f"{DIGIT}+"

URI_PARAMCHAR = f"(?:{cset(C_URI_PARAM_SAFE)}|{ESCAPED})"
URI_PARAM = f"{URI_PARAMCHAR}+(?:={URI_PARAMCHAR}+)?"

GENERIC_VALUE = f"(?:{TOKEN}|{HOST}|{QUOTED_STRING})"
GENERIC_PARAM = f"{TOKEN}(?:{EQUAL}{GENERIC_VALUE})?"
