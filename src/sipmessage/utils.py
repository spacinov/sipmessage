import typing

from . import grammar

T = typing.TypeVar("T")


def parse_many(
    parser: typing.Callable[[str], tuple[T, str]],
    parser_exc: ValueError,
    value: str,
) -> list[T]:
    value = grammar.simplify_whitespace(value)

    items: list[T] = []
    while value:
        item, value = parser(value)
        items.append(item)

        if value.startswith(","):
            # We have a separator, check it is followed by data.
            value = value[1:].lstrip()
            if not value:
                raise parser_exc
        elif value:
            # We do not have a separator, this is invalid.
            raise parser_exc

    return items


def parse_single(
    parser: typing.Callable[[str], tuple[T, str]],
    parser_exc: ValueError,
    value: str,
) -> T:
    value = grammar.simplify_whitespace(value)

    item, value = parser(value)
    if value:
        raise parser_exc

    return item
