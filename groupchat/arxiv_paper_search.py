# filename: arxiv_paper_search.py
import xml.etree.ElementTree as ET

import requests

# Define the URL and parameters for the API request
url = "http://export.arxiv.org/api/query"
params = {
    "search_query": "all:GPT-4",
    "start": 0,
    "max_results": 1,
    "sortBy": "submittedDate",
    "sortOrder": "descending",
}


def fetch_latest_paper(url, params):
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}")
        return None

    return response.text


def parse_arxiv_response(xml_response):
    ns = {"arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(xml_response)
    entry = root.find("arxiv:entry", ns)

    if entry is None:
        print("No papers found.")
        return None

    paper_info = {
        "title": entry.find("arxiv:title", ns).text.strip(),
        "authors": [
            author.find("arxiv:name", ns).text
            for author in entry.findall("arxiv:author", ns)
        ],
        "summary": entry.find("arxiv:summary", ns).text.strip(),
        "published": entry.find("arxiv:published", ns).text.strip(),
    }

    return paper_info


def main():
    xml_response = fetch_latest_paper(url, params)

    if xml_response:
        paper_info = parse_arxiv_response(xml_response)
        if paper_info:
            print(f"Title: {paper_info['title']}")
            print(f"Authors: {', '.join(paper_info['authors'])}")
            print(f"Published Date: {paper_info['published']}")
            print("\nSummary:")
            print(paper_info["summary"])
        else:
            print("Failed to parse the paper information.")
    else:
        print("Failed to fetch the latest paper.")


if __name__ == "__main__":
    main()
