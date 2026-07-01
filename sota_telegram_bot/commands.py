from __future__ import annotations


def parse_filter_args(args: list[str]) -> tuple[str, str] | None:
    if not args:
        return None
    if len(args) == 1:
        return "association", args[0]
    return args[0].lower(), " ".join(args[1:])
