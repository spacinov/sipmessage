#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import re
from collections.abc import Iterator, Mapping
from urllib.parse import quote, unquote

from . import grammar

EQUAL_PATTERN = re.compile(grammar.EQUAL)
SEMI_PATTERN = re.compile(grammar.SEMI)


class Parameters(Mapping[str, str | None]):
    """
    A mapping of :class:`Address`, :class:`URI` or :class:`Via` parameters.
    """

    def __init__(self, **kwargs: str | None) -> None:
        self.__data = dict(kwargs)

    @classmethod
    def parse(cls, value: str) -> "Parameters":
        """
        Parse the given string into a :class:`Parameters` instance.

        If parsing fails, a :class:`ValueError` is raised.
        """
        value = grammar.simplify_whitespace(value)

        data: dict[str, str | None] = {}
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
                data[unquote(k)] = v
        return cls(**data)

    def replace(self, **changes: str | None) -> "Parameters":
        """
        Return a copy of the parameters, updated with the given `changes`.
        """
        data = {}
        data.update(self.__data)
        data.update(**changes)
        return Parameters(**data)

    def __getitem__(self, key: str) -> str | None:
        return self.__data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.__data)

    def __len__(self) -> int:
        return len(self.__data)

    def __repr__(self) -> str:
        data = ""
        for k, v in self.items():
            if data:
                data += ", "
            data += f"{k}={v!r}"
        return f"Parameters({data})"

    def __str__(self) -> str:
        output = ""
        for k, v in self.items():
            output += ";" + quote(k)
            if v is not None:
                output += "=" + quote(v)
        return output
