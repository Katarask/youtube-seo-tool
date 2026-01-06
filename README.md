# 🎯 YouTube SEO Research Tool

Ein datengetriebenes Keyword-Research-Tool für YouTube, das **Nachfrage vs. Angebot** analysiert und die besten Content-Gelegenheiten identifiziert.

## 🚀 Features

- **YouTube Autocomplete Scraping** - Finde Long-Tail Keywords
- **Supply vs Demand Analysis** - Erkenne unterversorgte Nischen
- **Google Trends Integration** - YouTube-spezifische Trend-Daten
- **Gap Score Berechnung** - Automatische Opportunity-Bewertung
- **Notion Export** - Ergebnisse direkt in deine Notion-Datenbank

## 📊 Der Gap Score

```
Gap Score = (Demand / Supply) × Freshness Bonus × Small Channel Bonus

- Demand = Trend-Index × Durchschnitt-Views der Top 10
- Supply = Videos letzte 30 Tage × Ø Kanal-Größe
```

| Score | Bedeutung |
|-------|-----------|
| 🟢 > 7 | Goldene Gelegenheit |
| 🟡 4-7 | Solide Chance |
| 🔴 < 4 | Übersättigt |

## 🛠 Installation

```bash
# Repository klonen
git clone https://github.com/katarask/youtube-seo-tool.git
cd youtube-seo-tool

# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# Konfiguration
cp .env.example .env
# Füge deine API Keys in .env ein
```

## ⚙️ Konfiguration

Erstelle eine `.env` Datei:

```env
YOUTUBE_API_KEY=dein_youtube_api_key
NOTION_API_KEY=dein_notion_api_key
NOTION_DATABASE_ID=deine_database_id
```

## 📖 Verwendung

### Keyword Research

```bash
# Einzelnes Keyword analysieren
python -m src.cli analyze "guided meditation"

# Mehrere Keywords
python -m src.cli analyze "guided meditation" "sleep meditation" "meditation for anxiety"

# Mit Notion Export
python -m src.cli analyze "guided meditation" --notion

# Nur Autocomplete (ohne API Quota)
python -m src.cli autocomplete "meditation" --expand
```

### Beispiel Output

```
🎯 Keyword Analysis: "guided meditation for sleep"

📊 DEMAND METRICS
   Trend Index:        78/100
   Avg Views Top 10:   1,234,567
   Demand Score:       8.2/10

📦 SUPPLY METRICS  
   Videos (30 days):   127
   Avg Channel Size:   45,000 subs
   Supply Score:       5.4/10

🏆 GAP SCORE: 7.8/10 🟢
   → Gute Gelegenheit! Hohe Nachfrage, moderate Konkurrenz.

💡 INSIGHTS
   • Top 10 dominated by old videos (avg 2.3 years)
   • 3 small channels (<10k) in Top 10
   • Trend: ↗️ +15% vs last year
```

## 📁 Projektstruktur

```
youtube-seo-tool/
├── src/
│   ├── core/
│   │   ├── autocomplete.py    # YouTube Suggest Scraper
│   │   ├── youtube_api.py     # YouTube Data API Handler
│   │   ├── trends.py          # Google Trends Integration
│   │   └── analyzer.py        # Gap Score Berechnung
│   ├── data/
│   │   ├── cache.py           # SQLite Caching
│   │   └── models.py          # Data Classes
│   ├── exporters/
│   │   ├── notion.py          # Notion Integration
│   │   ├── csv_export.py      # CSV Export
│   │   └── json_export.py     # JSON Export
│   └── utils/
│       ├── config.py          # Konfiguration
│       └── rate_limiter.py    # Rate Limiting
├── tests/
├── docs/
├── .env.example
├── requirements.txt
└── README.md
```

## 🔑 API Limits

| API | Limit | Kosten |
|-----|-------|--------|
| YouTube Data API | 10,000 units/Tag | Search: 100 units |
| Google Trends | ~1,400 requests/Tag | Kostenlos |
| Notion API | 3 requests/sec | Kostenlos |

## 🤝 Contributing

Pull Requests sind willkommen! Für größere Änderungen bitte erst ein Issue erstellen.

## 📝 License

MIT License - siehe [LICENSE](LICENSE)

---

Built with ❤️ for YouTube Creators
