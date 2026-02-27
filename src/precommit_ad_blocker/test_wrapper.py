import os
from pathlib import Path

import typer

from precommit_ad_blocker.ad_blocker import main

test_wrapper_app = typer.Typer()

TEST_ENVVAR_CO_AUTHOR = "PRE_COMMIT_AD_BLOCKER_CO_AUTHORS"
TEST_ENVVAR_TRAILER = "PRE_COMMIT_AD_BLOCKER_TRAILER_KEYS"
TEST_ENVVAR_NO_DEFAULTS = "PRE_COMMIT_AD_BLOCKER_DISABLE_DEFAULTS"


@test_wrapper_app.command()
def test_wrapper_main(commit_msg_file: Path):
    co_authors = os.environ.get(TEST_ENVVAR_CO_AUTHOR, "").split(",")
    trailer_keys = os.environ.get(TEST_ENVVAR_TRAILER, "").split(",")
    enable_defaults = not bool(os.environ.get(TEST_ENVVAR_NO_DEFAULTS, ""))

    main(
        commit_msg_file=commit_msg_file,
        co_author=co_authors,
        trailer=trailer_keys,
        defaults=enable_defaults,
    )
