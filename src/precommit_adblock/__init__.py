from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self, Annotated
from itertools import filterfalse
import typer

app = typer.Typer()


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

        if key.lower() in self.blocked_trailer_keys:
            return True

        if key.lower() == "co-authored-by":
            if CoAuthoredBy.from_string(value).email in self.blocked_co_authors:
                return True

        return False


def remove_ads(commit_msg: str, is_ad: Callable[[str], bool]):
    return "\n".join(filterfalse(is_ad, commit_msg.splitlines()))


@app.command()
def main(
    commit_msg_file: Path,
    co_author: Annotated[
        list[str] | None, typer.Option(help="Co-authors to block.")
    ] = None,
    trailer: Annotated[
        list[str] | None, typer.Option(help="Trailer types to block.")
    ] = None,
) -> None:
    print(co_author, trailer, commit_msg_file)
    config = Config(
        blocked_trailer_keys=set(trailer) if trailer else set(),
        blocked_co_authors=set(co_author) if co_author else set(),
    )

    commit_msg_file.write_text(remove_ads(commit_msg_file.read_text(), config.is_ad))
