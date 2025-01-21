from unittest.mock import patch

from bs4 import BeautifulSoup
import pytest
import requests

from scraper.scraper import (
    WEBSITES,
    fetch_website
)


@patch('scraper.scraper.requests.get')
def test_fetch_website_success(mock_requests_get, default_hackernews_front_webpage):
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.text = default_hackernews_front_webpage

    parsed_website = fetch_website(WEBSITES[0])
    soup = BeautifulSoup(default_hackernews_front_webpage, 'html.parser')

    assert isinstance(parsed_website, BeautifulSoup)
    assert parsed_website == soup


@patch('scraper.scraper.requests.get')
def test_fetch_website_timout(mock_requests_get, capfd):
    mock_requests_get.side_effect = requests.exceptions.Timeout

    result = fetch_website(WEBSITES[0])

    mock_requests_get.assert_called_once_with(WEBSITES[0], timeout=5)
    assert result is None

    out, err = capfd.readouterr()
    assert "Error fetching the website" in out
    

@patch('scraper.scraper.requests.get')
def test_fetch_website_bad_response(mock_requests_get, capfd):
    mock_requests_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Error")
    mock_requests_get.return_value.text = "Not Found"

    result = fetch_website(WEBSITES[0])

    assert result is None
    
    out, err = capfd.readouterr()
    assert "Error fetching the website" in out


