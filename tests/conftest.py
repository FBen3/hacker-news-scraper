import os
import pytest


@pytest.fixture(scope="session")
def default_hackernews_front_webpage():
    file_path = os.path.join(
        os.path.dirname(__file__), "fixtures", "hn_page_1.html"
    )

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


