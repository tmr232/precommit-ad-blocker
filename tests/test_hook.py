import operator
import subprocess
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from precommit_ad_blocker.test_wrapper import (
    TEST_ENVVAR_CO_AUTHOR,
    TEST_ENVVAR_NO_DEFAULTS,
    TEST_ENVVAR_TRAILER,
)


@pytest.fixture
def commit_msg_with_ads(tmp_path: Path):
    msg_file = tmp_path / "commig_msg"
    msg_file.write_text(
        textwrap.dedent(
            """
            This is a commit message with ads.

            This is the core of the commit message.

            co-authored-by: Gemini <gemini@google.com>
            co-authored-by: Claude <claude@anthropic.com>
            """
        )
    )
    return msg_file


@dataclass(kw_only=True, frozen=True)
class HookTestCase:
    it: str
    no_defaults: bool = False
    extra_co_authors: list[str] = field(default_factory=list)
    extra_trailer_keys: list[str] = field(default_factory=list)

    expected_substrings: list[str] = field(default_factory=list)
    unexpected_substrings: list[str] = field(default_factory=list)

    @property
    def env_vars(self) -> dict[str, str]:
        env_vars = {}

        if self.no_defaults:
            env_vars[TEST_ENVVAR_NO_DEFAULTS] = "true"

        if self.extra_co_authors:
            env_vars[TEST_ENVVAR_CO_AUTHOR] = ",".join(self.extra_co_authors)

        if self.extra_trailer_keys:
            env_vars[TEST_ENVVAR_TRAILER] = ",".join(self.extra_trailer_keys)

        return env_vars


@pytest.mark.parametrize(
    "test_case",
    [
        HookTestCase(
            it="ensures default settings remove LLM co-authors",
            unexpected_substrings=["co-authored-by"],
        ),
        HookTestCase(
            it="ensures co-authors are not removed when defaults are disabled",
            no_defaults=True,
            expected_substrings=["co-authored-by"],
        ),
        HookTestCase(
            it="ensures providing custom co-author filter works",
            no_defaults=True,
            unexpected_substrings=["anthropic"],
            expected_substrings=["google"],
            extra_co_authors=["*@anthropic.com"],
        ),
    ],
    ids=operator.attrgetter("it"),
)
def test_hook(
    test_case: HookTestCase,
    commit_msg_with_ads: Path,
    tmp_path: Path,
    repo_root: Path,
    monkeypatch,
):
    temp_repo_path = tmp_path / "temp_repo"
    temp_repo_path.mkdir(exist_ok=False, parents=True)

    subprocess.check_call(["git", "-C", str(temp_repo_path), "init"])

    for key, value in test_case.env_vars.items():
        monkeypatch.setenv(key, value)

    output = subprocess.check_output(
        [
            "prek",
            "try-repo",
            "--no-progress",
            "--cd",
            str(temp_repo_path),
            "--verbose",
            str(repo_root.resolve()),
            "precommit-ad-blocker-for-internal-testing",
            "--stage",
            "commit-msg",
            "--commit-msg-filename",
            str(commit_msg_with_ads),
        ]
    )

    assert b"Ad-Blocker" in output

    filtered_commit_msg = commit_msg_with_ads.read_text()

    for expected_substring in test_case.expected_substrings:
        assert expected_substring in filtered_commit_msg

    for unexpected_substring in test_case.unexpected_substrings:
        assert unexpected_substring not in filtered_commit_msg
