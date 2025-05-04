#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#

import dataclasses
import re

from . import grammar, utils
from .parameters import Parameters

MEDIATYPE_EXCEPTION = ValueError("MediaType is not valid")
MEDIATYPE_PATTERN = re.compile(
    f"^(?P<mime_type>{grammar.TOKEN}/{grammar.TOKEN})"
    f"(?P<parameters>(?:{grammar.SEMI}{grammar.GENERIC_PARAM})*)"
)


@dataclasses.dataclass(frozen=True)
class MediaType:
    """
    A media type as used in `Accept` and `Content-Type` headers.
    """

    mime_type: str
    parameters: Parameters = dataclasses.field(default_factory=Parameters)

    @classmethod
    def parse(cls, value: str) -> "MediaType":
        """
        Parse the given string into a :class:`MediaType` instance.

        If parsing fails, a :class:`ValueError` is raised.
        """
        return utils.parse_single(cls._parse_one, MEDIATYPE_EXCEPTION, value)

    @classmethod
    def parse_many(cls, value: str) -> "list[MediaType]":
        """
        Parse the given string into a list of :class:`MediaType` instances.

        If parsing fails, a :class:`ValueError` is raised.
        """
        return utils.parse_many(cls._parse_one, MEDIATYPE_EXCEPTION, value)

    @classmethod
    def _parse_one(cls, value: str) -> "tuple[MediaType, str]":
        m = MEDIATYPE_PATTERN.match(value)
        if m:
            return (
                cls(
                    mime_type=m.group("mime_type"),
                    parameters=Parameters.parse(m.group("parameters")),
                ),
                value[m.end() :],
            )
        else:
            raise MEDIATYPE_EXCEPTION

    def __str__(self) -> str:
        s = self.mime_type
        s += str(self.parameters)
        return s
