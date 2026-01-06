"""Vercel Serverless API for YouTube SEO Tool"""
from http.server import BaseHTTPRequestHandler
import json
import os
import re
import requests
from urllib.parse import unquote
from datetime import datetime


def get_autocomplete_suggestions(query: str) -> list[str]:
    """Fetch suggestions from YouTube autocomplete API."""
    url = "https://suggestqueries-clients6.youtube.com/complete/search"
    params = {
        "client": "youtube",
        "ds": "yt",
        "q": query,
        "hl": "en",
        "gl": "us",
    }

    try:
        response = requests.get(url, params=params, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        response.raise_for_status()

        text = response.text
        match = re.search(r'\[.*\]', text)
        if not match:
            return []

        data = json.loads(match.group())

        if len(data) > 1 and isinstance(data[1], list):
            return [item[0] for item in data[1] if item]

        return []
    except Exception as e:
        print(f"Autocomplete error: {e}")
        return []


def export_to_notion(keyword: str, gap_score: float, demand_score: float, supply_score: float, suggestion_count: int) -> bool:
    """Export a keyword analysis to Notion database."""
    notion_key = os.getenv("NOTION_API_KEY")
    notion_db = os.getenv("NOTION_DATABASE_ID")

    print(f"Notion key present: {bool(notion_key)}, DB present: {bool(notion_db)}")

    if not notion_key or not notion_db:
        print("Missing Notion credentials")
        return False

    # Determine rating (matching existing database options)
    if gap_score >= 7:
        rating = "🟢 Excellent"
        icon = "🟢"
    elif gap_score >= 4:
        rating = "🟡 Good"
        icon = "🟡"
    else:
        rating = "🔴 Poor"
        icon = "🔴"

    try:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers={
                "Authorization": f"Bearer {notion_key}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            },
            json={
                "parent": {"database_id": notion_db},
                "icon": {"type": "emoji", "emoji": icon},
                "properties": {
                    "Keyword": {"title": [{"text": {"content": keyword}}]},
                    "Gap Score": {"number": gap_score},
                    "Demand Score": {"number": demand_score},
                    "Supply Score": {"number": supply_score},
                    "Suggestions Count": {"number": suggestion_count},
                    "Rating": {"select": {"name": rating}},
                    "Analyzed At": {"date": {"start": datetime.now().isoformat()}}
                }
            },
            timeout=10
        )
        # Notion returns 200 for success
        success = response.status_code == 200
        print(f"Notion response: {response.status_code} - success: {success}")
        return success
    except Exception as e:
        print(f"Notion error: {e}")
        return False


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if self.path.startswith('/api/autocomplete'):
            query = self.path.split('q=')[-1].split('&')[0] if 'q=' in self.path else ''
            if query:
                query = unquote(query)
                suggestions = get_autocomplete_suggestions(query)
                self.wfile.write(json.dumps({"suggestions": suggestions}).encode())
            else:
                self.wfile.write(json.dumps({"suggestions": []}).encode())
        elif self.path == '/api/debug':
            # Debug endpoint to check env vars
            self.wfile.write(json.dumps({
                "notion_key_set": bool(os.getenv("NOTION_API_KEY")),
                "notion_db_set": bool(os.getenv("NOTION_DATABASE_ID")),
                "youtube_key_set": bool(os.getenv("YOUTUBE_API_KEY"))
            }).encode())
        else:
            self.wfile.write(json.dumps({"status": "ok", "message": "YouTube SEO API"}).encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if self.path == '/api/analyze':
            keywords = data.get('keywords', [])
            export_notion = data.get('export_notion', False)

            print(f"Analyze request: keywords={keywords}, export_notion={export_notion}")

            results = []
            exported = 0

            for kw in keywords[:10]:
                suggestions = get_autocomplete_suggestions(kw)
                suggestion_count = len(suggestions)

                demand_score = min(10, suggestion_count * 0.8)
                supply_score = 5.0
                gap_score = round(demand_score / max(supply_score, 1) * 5, 1)

                results.append({
                    "keyword": kw,
                    "gap_score": gap_score,
                    "rating": "excellent" if gap_score >= 7 else ("good" if gap_score >= 4 else "poor"),
                    "demand_score": round(demand_score, 1),
                    "supply_score": supply_score,
                    "trend_direction": "stable",
                    "videos_30d": 0,
                    "avg_views": 0,
                    "suggestions_count": suggestion_count
                })

                # Export to Notion if requested
                if export_notion:
                    print(f"Exporting {kw} to Notion...")
                    if export_to_notion(kw, gap_score, demand_score, supply_score, suggestion_count):
                        exported += 1
                        print(f"Exported {kw} successfully")

            self.wfile.write(json.dumps({
                "results": results,
                "exported": exported,
                "quota_used": 0
            }).encode())

        elif self.path == '/api/suggestions':
            keyword = data.get('keyword', '')
            suggestions = get_autocomplete_suggestions(keyword) if keyword else []
            self.wfile.write(json.dumps({"suggestions": suggestions}).encode())

        else:
            self.wfile.write(json.dumps({"error": "Unknown endpoint"}).encode())
