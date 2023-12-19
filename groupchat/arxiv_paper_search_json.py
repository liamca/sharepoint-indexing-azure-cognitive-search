# filename: arxiv_paper_search_json.py

import requests

# Define the URL for the API request and the headers for accepting JSON
url = "http://export.arxiv.org/api/query"
headers = {"Accept": "application/json"}
params = {
    "search_query": 'all:"GPT-4" OR title:"GPT-4" OR abstract:"GPT-4"',
    "start": 0,
    "max_results": 1,
    "sortBy": "submittedDate",
    "sortOrder": "descending",
}


def fetch_latest_paper(url, headers, params):
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}")
        return None
    return response.json()


def parse_arxiv_response(json_response):
    entries = json_response.get("entries")
    if not entries:
        print("No papers found.")
        return None

    latest_paper = entries[0]
    paper_info = {
        "title": latest_paper["title"],
        "authors": [author["name"] for author in latest_paper["authors"]],
        "summary": latest_paper["summary"],
        "published": latest_paper["published"],
    }
    return paper_info


def main():
    json_response = fetch_latest_paper(url, headers, params)
    if json_response:
        paper_info = parse_arxiv_response(json_response)
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
