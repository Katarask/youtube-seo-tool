"""Setup script to create Notion database for YouTube SEO Tool."""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")

if not NOTION_API_KEY:
    print("Error: NOTION_API_KEY not found in .env file")
    exit(1)

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def search_pages():
    """Search for pages the integration has access to."""
    url = "https://api.notion.com/v1/search"
    data = {
        "filter": {"value": "page", "property": "object"},
        "page_size": 10
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def create_database(parent_page_id: str, title: str = "YouTube Keyword Research"):
    """Create the keyword research database."""
    url = "https://api.notion.com/v1/databases"
    
    data = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": title}}],
        "icon": {"type": "emoji", "emoji": "🎯"},
        "properties": {
            "Keyword": {"title": {}},
            "Gap Score": {"number": {"format": "number"}},
            "Rating": {
                "select": {
                    "options": [
                        {"name": "🟢 Excellent", "color": "green"},
                        {"name": "🟡 Good", "color": "yellow"},
                        {"name": "🔴 Poor", "color": "red"},
                    ]
                }
            },
            "Demand Score": {"number": {"format": "number"}},
            "Supply Score": {"number": {"format": "number"}},
            "Trend Index": {"number": {"format": "number"}},
            "Trend Direction": {"rich_text": {}},
            "Avg Views (Top 10)": {"number": {"format": "number"}},
            "Videos (30 days)": {"number": {"format": "number"}},
            "Avg Channel Size": {"number": {"format": "number"}},
            "Small Channels in Top 10": {"number": {"format": "number"}},
            "Avg Video Age (days)": {"number": {"format": "number"}},
            "Suggestions Count": {"number": {"format": "number"}},
            "Analyzed At": {"date": {}},
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

if __name__ == "__main__":
    print("Searching for accessible pages...")
    pages = search_pages()
    
    if "results" in pages and pages["results"]:
        print(f"\nFound {len(pages['results'])} accessible pages:")
        for i, page in enumerate(pages["results"]):
            title = page.get("properties", {}).get("title", {})
            if isinstance(title, dict) and "title" in title:
                name = title["title"][0]["plain_text"] if title["title"] else "Untitled"
            else:
                name = "Untitled"
            print(f"  {i+1}. {name} (ID: {page['id']})")
        
        print("\nTo create a database, run:")
        print('  python -c "from setup_notion import create_database; print(create_database(\'PAGE_ID\'))"')
    else:
        print("No pages found. Make sure the integration is connected to a page.")
        print(f"Response: {pages}")
