#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import string


def cset(chars: str) -> str:
    """
    Transform a collection of characters into a regular expression
    character set.
    """
    return "[" + chars.replace("-", "\\-").replace("[", "\\[").replace("]", "\\]") + "]"


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
HEXDIG = cset(string.hexdigits)
ESCAPED = f"%{HEXDIG}{{2}}"
QUOTED_STRING = '"(?:[^"]|\\")*"'

HEXSEQ = f"{HEXDIG}{{1,4}}(?::{HEXDIG}{{1,4}})*"
HEXPART = f"(?:{HEXSEQ}|{HEXSEQ}::(?:{HEXSEQ})?|::(?:{HEXSEQ})?)"
IPV4ADDRESS = "\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}"
IPV6ADDRESS = f"{HEXPART}(?::{IPV4ADDRESS})?"
IPV6REFERENCE = f"\\[{IPV6ADDRESS}\\]"

DOMAINLABEL = f"{ALPHANUM}+([\\-]+{ALPHANUM}+)*"
TOPLABEL = f"{ALPHA}+([\\-]+{ALPHANUM}+)*"
HOSTNAME = f"(?:{DOMAINLABEL}\\.)*{TOPLABEL}[\\.]?"

HOST = f"(?:{HOSTNAME}|{IPV4ADDRESS}|{IPV6REFERENCE})"
USER = f"(?:{cset(C_USER_SAFE)}|{ESCAPED})+"
PASSWORD = f"(?:{cset(C_PASSWORD_SAFE)}|{ESCAPED})+"
PORT = "\\d+"

URI_PARAMCHAR = f"(?:{cset(C_URI_PARAM_SAFE)}|{ESCAPED})"
URI_GENERIC_PARAM = f"{URI_PARAMCHAR}+(?:={URI_PARAMCHAR}+)?"
