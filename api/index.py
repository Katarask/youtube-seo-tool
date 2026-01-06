"""Vercel Serverless API for YouTube SEO Tool"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import re
import requests
from urllib.parse import unquote

# Simple autocomplete function (standalone, no dependencies)
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

            # For now, return mock results since full analyzer has complex dependencies
            results = []
            for kw in keywords[:10]:
                # Get suggestion count as a simple metric
                suggestions = get_autocomplete_suggestions(kw)
                suggestion_count = len(suggestions)

                # Simple scoring based on suggestion count
                demand_score = min(10, suggestion_count * 0.8)
                supply_score = 5.0  # Default
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

            self.wfile.write(json.dumps({
                "results": results,
                "exported": 0,
                "quota_used": 0
            }).encode())

        elif self.path == '/api/suggestions':
            keyword = data.get('keyword', '')
            suggestions = get_autocomplete_suggestions(keyword) if keyword else []
            self.wfile.write(json.dumps({"suggestions": suggestions}).encode())

        else:
            self.wfile.write(json.dumps({"error": "Unknown endpoint"}).encode())
