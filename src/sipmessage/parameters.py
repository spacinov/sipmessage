#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import re
from urllib.parse import quote, unquote

from . import grammar

EQUAL_PATTERN = re.compile(grammar.EQUAL)
SEMI_PATTERN = re.compile(grammar.SEMI)


class Parameters(dict[str, str | None]):
    """
    A dictionary of :class:`Address`, :class:`URI` or :class:`Via` parameters.
    """

    @classmethod
    def parse(cls, val: str) -> "Parameters":
        """
        Parse the given string into a :class:`Parameters` instance.
        """
        p = cls()
        for bit in SEMI_PATTERN.split(val):
            if bit:
                if "=" in bit:
                    k, v = EQUAL_PATTERN.split(bit, 1)
                    v = unquote(v)
                else:
                    k, v = bit, None
                p[unquote(k)] = v
        return p

    def __str__(self) -> str:
        return ";".join(
            [
                quote(k) if v is None else (quote(k) + "=" + quote(v))
                for k, v in self.items()
            ]
        )
