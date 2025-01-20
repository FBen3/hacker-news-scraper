import os
import pytest


@pytest.fixture(scope="session")
def default_hackernews_front_webpage():
    hn_webpage = os.path.join(
        os.path.dirname(__file__), "fixtures", "index.html"
    )

    return hn_webpage


