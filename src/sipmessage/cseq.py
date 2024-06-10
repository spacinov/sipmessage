#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import dataclasses
import re

from . import grammar

CSEQ_PATTERN = re.compile(
    f"^(?P<sequence>{grammar.DIGIT}+){grammar.LWS}(?P<method>{grammar.TOKEN})$"
)


@dataclasses.dataclass
class CSeq:
    """
    A `CSeq` header, used to identity and order transactions.
    """

    sequence: int
    "The sequence number."

    method: str
    "The request method."

    @classmethod
    def parse(cls, value: str) -> "CSeq":
        """
        Parse the given string into an :class:`Address` instance.

        If parsing fails, a :class:`ValueError` is raised.
        """
        pass
        value = grammar.simplify_whitespace(value)

        m = CSEQ_PATTERN.match(value)
        if m is None:
            raise ValueError("CSeq is not valid")

        return cls(sequence=int(m.group("sequence")), method=m.group("method"))

    def __str__(self) -> str:
        return f"{self.sequence} {self.method}"
