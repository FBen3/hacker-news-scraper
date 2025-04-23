from datetime import datetime
from unittest.mock import patch


def test_home_endpoint(client):
    resp = client.get("/")

    assert resp.status_code == 200
    assert resp.get_json() == {"message": "This is Ben's HackerNews custom scraper!"}


@patch("app.save_scraped_data")     # prevent real DB write
@patch("app.parse_pages")           # prevent real network hit
def test_scrape_endpoint(mock_parse_pages, mock_saved_data, client):
    mock_parse_pages.return_value = {"dummy": "payload"}

    resp = client.post("api/scrape")

    assert resp.status_code == 200
    assert resp.get_json() == {"status": "success"}

    mock_parse_pages.assert_called_once()
    mock_saved_data.assert_called_once_with({"dummy": "payload"})


@patch("app.fetch_saved_articles")
def test_articles_endpoint(mock_fetch_saved_articles, client):
    mock_fetch_saved_articles.return_value = [
        {"title": "Test_Article_1", "scrape_date": datetime(2025, 1, 1, 12, 0, 0)},
        {"title": "Test_Article_2", "scrape_date": datetime(2025, 1, 1, 13, 0, 0)},
    ]

    resp = client.get("api/articles")

    assert resp.status_code == 200
    # check datetimes have been auto‑ISO‑encoded by ISOJSONProvider
    assert resp.get_json() == [
        {"title": "Test_Article_1", "scrape_date": "2025-01-01T12:00:00"},
        {"title": "Test_Article_2", "scrape_date": "2025-01-01T13:00:00"},
    ]

    mock_fetch_saved_articles.assert_called_once_with(date=None)


@patch("app.update_keywords")
def test_update_keywords_endpoint(mock_update_keywords, client):
    payload = {"keywords": ["new_word_1", "new_word_2"]}
    resp = client.post("api/update_keywords", json=payload)

    assert resp.status_code == 200
    assert resp.get_json() == {"status": "success"}

    mock_update_keywords.asset_called_once_with(["new_word_1", "new_word_2"])
