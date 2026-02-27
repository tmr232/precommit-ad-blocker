from dataclasses import dataclass, field

import pytest

from precommit_ad_blocker.ad_blocker import CoAuthoredBy, Config, remove_ads


@dataclass(kw_only=True)
class CoAuthorTestCase:
    co_authored_by: str
    pattern: str
    should_match: bool


@pytest.mark.parametrize(
    "test_case",
    [
        CoAuthorTestCase(
            co_authored_by="name <email@domain.com>",
            pattern="email@domain.com",
            should_match=True,
        ),
        CoAuthorTestCase(
            co_authored_by="email@domain.com",
            pattern="email@domain.com",
            should_match=True,
        ),
        CoAuthorTestCase(
            co_authored_by="name <email@domain.com>",
            pattern="*@domain.com",
            should_match=True,
        ),
        CoAuthorTestCase(
            co_authored_by="name <email@other-domain.com>",
            pattern="*@domain.com",
            should_match=False,
        ),
        CoAuthorTestCase(
            co_authored_by="email@domain.com <email@other-domain.com>",
            pattern="*@domain.com",
            should_match=False,
        ),
    ],
)
def test_co_author(test_case: CoAuthorTestCase):
    assert (
        CoAuthoredBy.from_string(test_case.co_authored_by).match(test_case.pattern)
        == test_case.should_match
    )


@dataclass(kw_only=True)
class RemoveAdsTestCase:
    commit_msg: str
    blocked_authors: set[str]
    blocked_trailers: set[str]
    clean: str
    blocked: list[str]
    config: Config = field(init=False)

    def __post_init__(self):
        self.config = Config(
            blocked_co_authors=self.blocked_authors,
            blocked_trailer_keys=self.blocked_trailers,
        )

    @property
    def is_ad(self):
        return self.config.is_ad


REMOVE_ADS_COMMIT_MESSAGE = """Test commit message

This is a commit message used for testing.
It is not very interesting.

ad-trailer: This is an ad!
non-ad-trailer: This is not an ad!
co-authored-by: ad <ad@example.com>
co-authored-by: person <person@example.com>"""

CO_AUTHOR_CLEAN_COMMIT_MESSAGE = """Test commit message

This is a commit message used for testing.
It is not very interesting.

ad-trailer: This is an ad!
non-ad-trailer: This is not an ad!
co-authored-by: person <person@example.com>"""

FULLY_CLEAN_COMMIT_MESSAGE = """Test commit message

This is a commit message used for testing.
It is not very interesting.

non-ad-trailer: This is not an ad!
co-authored-by: person <person@example.com>"""


@pytest.mark.parametrize(
    "test_case",
    [
        RemoveAdsTestCase(
            commit_msg=REMOVE_ADS_COMMIT_MESSAGE,
            blocked_authors=set(),
            blocked_trailers=set(),
            clean=REMOVE_ADS_COMMIT_MESSAGE,
            blocked=[],
        ),
        RemoveAdsTestCase(
            commit_msg=REMOVE_ADS_COMMIT_MESSAGE,
            blocked_authors={"ad@example.com"},
            blocked_trailers=set(),
            clean=CO_AUTHOR_CLEAN_COMMIT_MESSAGE,
            blocked=["co-authored-by: ad <ad@example.com>"],
        ),
        RemoveAdsTestCase(
            commit_msg=REMOVE_ADS_COMMIT_MESSAGE,
            blocked_authors={"ad@example.com"},
            blocked_trailers={"ad-trailer"},
            clean=FULLY_CLEAN_COMMIT_MESSAGE,
            blocked=[
                "ad-trailer: This is an ad!",
                "co-authored-by: ad <ad@example.com>",
            ],
        ),
    ],
)
def test_remove_ads(test_case: RemoveAdsTestCase):
    blocker_result = remove_ads(test_case.commit_msg, test_case.is_ad)
    assert blocker_result.clean == test_case.clean
    assert blocker_result.blocked == test_case.blocked
