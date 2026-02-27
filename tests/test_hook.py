import subprocess
import textwrap
from pathlib import Path

import pytest


@pytest.fixture
def commit_msg_with_ads(tmp_path: Path):
    msg_file = tmp_path / "commig_msg"
    msg_file.write_text(
        textwrap.dedent(
            """This is a commit message with ads.

                           This is the core of the commit message.

                           co-authored-by: Gemini <gemini@google.com>
                           co-authored-by: Claude <claude@anthropic.com>
                           """
        )
    )
    return msg_file


def test_hook(commit_msg_with_ads: Path):
    output = subprocess.check_output(
        [
            "prek",
            "try-repo",
            "--no-progress",
            "--verbose",
            ".",
            "precommit-ad-blocker",
            "--stage",
            "commit-msg",
            "--commit-msg-filename",
            str(commit_msg_with_ads),
            "--",
            "--verbose",
        ]
    )
    print(output)
    assert b"Ad-Blocker" in output
    assert b"Blocked:" in output
