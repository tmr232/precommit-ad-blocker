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
        return cls(name=name, email=email)

    def match(self, email: str) -> bool:
        return fnmatch.fnmatch(self.email, email)


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
            co_author = CoAuthoredBy.from_string(value)
            for blocked_co_author in self.blocked_co_authors:
                if co_author.match(blocked_co_author):
                    return True

        return False


@dataclass(kw_only=True, frozen=True)
class BlockerResult:
    clean: str
    blocked: list[str]


def remove_ads(commit_msg: str, is_ad: Callable[[str], bool]) -> BlockerResult:
    not_ads, ads = partition(is_ad, commit_msg.splitlines())
    clean = "\n".join(not_ads)
    blocked = list(ads)
    return BlockerResult(clean=clean, blocked=blocked)


def build_config(
    *,
    extra_co_authors: list[str] | None,
    extra_trailer_keys: list[str] | None,
    use_defaults: bool,
) -> Config:
    blocked_co_authors: set[str] = set()
    extra_trailer_keys: set[str] = set()
    if use_defaults:
        blocked_co_authors = DEFAULT_BLOCKED_CO_AUTHORS
        blocked_trailer_keys = DEFAULT_BLOCKED_TRAILER_KEYS

    if extra_co_authors:
        blocked_co_authors.update(extra_co_authors)

    if extra_trailer_keys:
        blocked_trailer_keys.update(extra_trailer_keys)

    return Config(
        blocked_trailer_keys=blocked_trailer_keys,
        blocked_co_authors=blocked_co_authors,
    )


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
    config = build_config(
        extra_co_authors=co_author,
        extra_trailer_keys=trailer,
        use_defaults=defaults,
    )

    block_result = remove_ads(commit_msg_file.read_text(), config.is_ad)

    commit_msg_file.write_text(block_result.clean)

    if verbose:
        for ad in block_result.blocked:
            print(f"Blocked: {ad}")
