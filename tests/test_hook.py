import subprocess
import textwrap
from pathlib import Path

import pytest


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


def test_hook(commit_msg_with_ads: Path, tmp_path: Path, repo_root: Path):
    temp_repo_path = tmp_path / "temp_repo"
    temp_repo_path.mkdir(exist_ok=False, parents=True)

    subprocess.check_call(["git", "-C", str(temp_repo_path), "init"])

    output = subprocess.check_output(
        [
            "prek",
            "try-repo",
            "--no-progress",
            "--cd",
            str(temp_repo_path),
            "--verbose",
            str(repo_root.resolve()),
            "precommit-ad-blocker",
            "--stage",
            "commit-msg",
            "--commit-msg-filename",
            str(commit_msg_with_ads),
        ]
    )

    assert b"Ad-Blocker" in output

    assert "co-authored-by" not in commit_msg_with_ads.read_text()
