#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

from urllib.parse import quote, unquote


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
        if val:
            for bit in val.split(";"):
                if "=" in bit:
                    k, v = bit.split("=", 1)
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
