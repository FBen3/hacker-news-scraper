from unittest.mock import patch

from bs4 import BeautifulSoup
import pytest

from scraper.scraper import (
    WEBSITES,
    fetch_website
)


@patch('scraper.scraper.requests.get')
def test_fetch_website_success(mock_request_get, default_hackernews_front_webpage):
    mock_request_get.return_value.status_code = 200
    mock_request_get.return_value.text = default_hackernews_front_webpage

    parsed_website = fetch_website(WEBSITES[0])
    soup = BeautifulSoup(default_hackernews_front_webpage, 'html.parser')

    assert isinstance(parsed_website, BeautifulSoup)
    assert parsed_website == soup


def test_fetch_website_timout():
    # TODO: this
    pass


# def test_fetch_website_bad_response():
#     pass


