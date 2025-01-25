"""Fetch and Scrape site

Attempts to get a response from specified
webpages, parses the webpage, and checks
for the presence of specied keywords.

"""
from datetime import datetime
import json
import re

from bs4 import BeautifulSoup
import requests


WEBSITES = [
    "https://news.ycombinator.com",
    "https://news.ycombinator.com/?p=2"
]

KEYWORDS = [
    "zork",
    "WAR",
    "BCI",
    "neuro"
]


def fetch_website(url: str) -> BeautifulSoup:
    try:
        response = requests.get(url, timeout=5)                 # send HTTP GET request
        response.raise_for_status()                             # raise HTTP Error for bad responses, e.g. (4XX, 5XX)

        soup = BeautifulSoup(response.text, 'html.parser')      # instantiate parsed object
        return soup

    except (requests.exceptions.RequestException, 
            requests.exceptions.Timeout) as e:
        print(f"Error fetching the website: {e}")
        return None


def add_meta_data(next_tr: BeautifulSoup) -> dict:
    """Extraction strategy.

    Each title <tr> has an id, which can 
    be tied to the corresponding metadata <tr>.
    
    By finding the next sibling <tr> of the 
    title's <tr>, I can extract the metadata.
    """
    meta_data = {
        "points": None,
        "post_date": None,
        "number_of_comments": None
    }

    score_span = next_tr.find('span', class_="score")           # extract points from <span class="score">
    if score_span:
        meta_data["points"] = int(re.search(r'\d+', score_span.get_text()).group())

    age_span = next_tr.find('span', class_="age")               # extract points from <span class="age">
    if age_span and ("title" in age_span.attrs):
        meta_data["post_date"] = age_span["title"]

    comment_link = next_tr.find('a', string=lambda text: 'comment' in text.lower())         # extract number of comments from <a> tag
    if comment_link:
        comment_count = comment_link.get_text().split()[0]
        if comment_count.isdigit():
            meta_data["number_of_comments"] = int(comment_count)

    return meta_data


def check_titles(parsed_site: BeautifulSoup) -> list:
    """Scraping strategy.

    Instead of hardcoding exact locations, I will rely 
    on class names and more general HTML structures to 
    find the titles. 
    
    Even if some minor changes occur, the scraper should still work.
    """
    results = []

    page_titles = parsed_site.find_all('tr', class_="athing")

    for page_title in page_titles:
        title = page_title.find('span', class_="titleline").find('a')
        if title:
            title_text = title.get_text().strip()
            title_url = title['href']
            post_id = page_title["id"]

            matched_keywords = []
            for keyword in KEYWORDS:
                if re.search(rf'\b{re.escape(keyword)}\b', title_text, re.IGNORECASE):
                    matched_keywords.append(keyword)

            if matched_keywords:
                next_tr = page_title.find_next_sibling('tr')

                main_data = {
                    "matched_keywords": matched_keywords,
                    "title": title_text,
                    "url": title_url
                }
                meta_data = add_meta_data(next_tr=next_tr)

                results.append(main_data | meta_data)

    return results


def parse_pages(websites: list[str]) -> dict:
    scrape_results = {
        "scrape_date": datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        "saves": []
    }

    for site in websites:
        parsed_site = fetch_website(site)
        matched_data = check_titles(parsed_site)
        if matched_data:
            scrape_results["saves"].extend(matched_data)

    return scrape_results


if __name__ == "__main__":
    test_output = parse_pages(WEBSITES)
    # print(test_output)
    # print(json.dumps(test_output, indent=4))
