"""Vercel Serverless API for YouTube SEO Tool"""
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.autocomplete import get_autocomplete_suggestions, expand_keyword
from src.core.analyzer import KeywordAnalyzer
from src.exporters.notion_export import NotionExporter

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
                from urllib.parse import unquote
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
            expand = data.get('expand', False)
            export_notion = data.get('export_notion', False)
            
            analyzer = KeywordAnalyzer(use_cache=False)
            results = []
            
            for kw in keywords[:10]:  # Limit to 10
                try:
                    analysis = analyzer.analyze_keyword(kw, expand=expand)
                    if analysis:
                        items = analysis if isinstance(analysis, list) else [analysis]
                        for a in items:
                            results.append({
                                "keyword": a.keyword,
                                "gap_score": round(a.gap_score, 1),
                                "rating": "excellent" if a.gap_score >= 7 else ("good" if a.gap_score >= 4 else "poor"),
                                "demand_score": round(a.demand.score, 1),
                                "supply_score": round(a.supply.score, 1),
                                "trend_direction": a.demand.trend_direction,
                                "videos_30d": a.supply.recent_videos_30d,
                                "avg_views": a.supply.avg_views,
                                "suggestions_count": a.demand.suggestion_count
                            })
                except Exception as e:
                    print(f"Error: {e}")
            
            # Export to Notion if requested
            exported = 0
            if export_notion and results:
                notion_key = os.getenv("NOTION_API_KEY")
                notion_db = os.getenv("NOTION_DATABASE_ID")
                if notion_key and notion_db:
                    try:
                        exporter = NotionExporter(notion_key, notion_db)
                        for kw in keywords[:10]:
                            analysis = analyzer.analyze_keyword(kw, expand=False)
                            if analysis:
                                items = analysis if isinstance(analysis, list) else [analysis]
                                for a in items:
                                    if exporter.export_analysis(a):
                                        exported += 1
                    except:
                        pass
            
            self.wfile.write(json.dumps({
                "results": results,
                "exported": exported,
                "quota_used": analyzer.api.quota_used if hasattr(analyzer, 'api') else 0
            }).encode())
        
        elif self.path == '/api/suggestions':
            keyword = data.get('keyword', '')
            suggestions = expand_keyword(keyword) if keyword else []
            self.wfile.write(json.dumps({"suggestions": suggestions}).encode())
        
        else:
            self.wfile.write(json.dumps({"error": "Unknown endpoint"}).encode())
