#
# Copyright (C) Spacinov SAS
# Distributed under the 2-clause BSD license
#


class Parameters(dict[str, str | None]):
    @classmethod
    def parse(cls, val: str) -> "Parameters":
        p = cls()
        if val:
            for bit in val.split(";"):
                if "=" in bit:
                    k, v = bit.split("=", 1)
                else:
                    k, v = bit, None
                p[k] = v
        return p

    def __str__(self) -> str:
        return ";".join([k if v is None else (k + "=" + v) for k, v in self.items()])
