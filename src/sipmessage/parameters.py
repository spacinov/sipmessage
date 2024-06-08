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
    def parse(cls, value: str) -> "Parameters":
        """
        Parse the given string into a :class:`Parameters` instance.

        If parsing fails, a :class:`ValueError` is raised.
        """
        value = grammar.simplify_whitespace(value)

        p = cls()
        if value:
            bits = SEMI_PATTERN.split(value)

            # The first "bit" must be empty, as the string must start
            # with a SEMI.
            if bits[0]:
                raise ValueError("Parameters are not valid")

            for bit in bits[1:]:
                # Empty parameters are not allowed.
                if not bit:
                    raise ValueError("Parameters are not valid")

                if "=" in bit:
                    k, v = EQUAL_PATTERN.split(bit, 1)
                    v = unquote(v)
                else:
                    k, v = bit, None
                p[unquote(k)] = v
        return p

    def __str__(self) -> str:
        output = ""
        for k, v in self.items():
            output += ";" + quote(k)
            if v is not None:
                output += "=" + quote(v)
        return output
