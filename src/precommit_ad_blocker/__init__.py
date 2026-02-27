import fnmatch
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Final, Self

import typer
from more_itertools import partition

app = typer.Typer()

DEFAULT_BLOCKED_CO_AUTHORS: Final = {
    "*@ampcode.com",
    "*@anthropic.com",
    "*@cursor.com",
    "*@google.com",
    "*@openai.com",
}
DEFAULT_BLOCKED_TRAILER_KEYS: Final = {key.casefold() for key in ["Amp-Thread-ID"]}


@dataclass(kw_only=True, frozen=True)
class CoAuthoredBy:
    name: str | None
    email: str

    @classmethod
    def from_string(cls, value: str) -> Self:
        name_part, _, email_part = value.rpartition("<")
        name = name_part.strip()
        email = email_part.strip().rstrip(">")
        return CoAuthoredBy(name=name, email=email)


@dataclass(kw_only=True, frozen=True)
class Config:
    blocked_trailer_keys: set[str] = field(default_factory=set)
    blocked_co_authors: set[str] = field(default_factory=set)

    def is_ad(self, line: str):
        key, _, value = line.partition(":")
        key = key.casefold()

        if key in self.blocked_trailer_keys:
            return True

        if key == "co-authored-by".casefold():
            email = CoAuthoredBy.from_string(value).email
            for blocked_co_author in self.blocked_co_authors:
                if fnmatch.fnmatch(email, blocked_co_author):
                    return True

        return False


def remove_ads(commit_msg: str, is_ad: Callable[[str], bool], *, verbose: bool = False):
    not_ads, ads = partition(is_ad, commit_msg.splitlines())
    if verbose:
        for ad in ads:
            print(f"Blocked: {ad}")
    return "\n".join(not_ads)


@app.command()
def main(
    commit_msg_file: Path,
    co_author: Annotated[
        list[str] | None,
        typer.Option(help="Co-authors to block. Uses glob patterns."),
    ] = None,
    trailer: Annotated[
        list[str] | None,
        typer.Option(help="Trailer types to block."),
    ] = None,
    *,
    defaults: Annotated[bool, typer.Option(help="Include default blocklists.")] = True,
    verbose: Annotated[bool, typer.Option(help="Show removed lines.")] = False,
) -> None:
    blocked_co_authors = set()
    blocked_trailer_keys = set()
    if defaults:
        blocked_co_authors = DEFAULT_BLOCKED_CO_AUTHORS
        blocked_trailer_keys = DEFAULT_BLOCKED_TRAILER_KEYS

    if co_author:
        blocked_co_authors.update(co_author)

    if trailer:
        blocked_trailer_keys.update(trailer)

    config = Config(
        blocked_trailer_keys=blocked_trailer_keys,
        blocked_co_authors=blocked_co_authors,
    )

    commit_msg_file.write_text(
        remove_ads(
            commit_msg_file.read_text(),
            config.is_ad,
            verbose=verbose,
        ),
    )
