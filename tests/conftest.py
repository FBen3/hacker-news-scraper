import os

import pytest

from app import app as flask_app


@pytest.fixture(scope="session")
def app():
    """Flask app instance configured for testing.
    """
    flask_app.config.update(TESTING=True)  # disable error caching
    return flask_app


@pytest.fixture()
def client(app):
    """Flask test client for simulating requests.
    """
    return app.test_client()


@pytest.fixture(scope="session")
def default_hackernews_front_webpage():
    """Front page for HackerNews.
    """
    file_path = os.path.join(
        os.path.dirname(__file__), "fixtures", "hn_page_1.html"
    )

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


