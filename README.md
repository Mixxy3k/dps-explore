# 🏠 KRDO Explorer — Krajowy Rejestr Domów Opieki

> **Interactive data explorer for 3,475+ care facilities across Poland.**  
> A solo full-stack data project: web scraping → geocoding pipeline → interactive SPA.

---

## 📌 Overview

**KRDO Explorer** is a client-side single-page application that lets users browse, filter, sort, and save care homes from Poland's National Register of Care Facilities (KRDO). Built for a real-world need — helping a family member find an appropriate long-term care placement.

**Live demo:** → _[github pages link here after deploy]_

---

## ✨ Features

| Feature | Detail |
|---------|--------|
| 🔍 **Full-text search** | Search by name, location, address, or care type |
| 🎯 **One-click presets** | "Intellectually disabled", "Public only", "KIDO recommended", "Nearby (50 km)" |
| 📏 **Distance calculation** | Haversine formula — enter any city, default Elbląg |
| ⭐ **Favorites basket** | Persisted in `localStorage`, survives page refreshes |
| 📱 **Responsive design** | Card layout on mobile, table view on desktop (auto-switch at 900px) |
| 🗺️ **Geo-enriched** | All 405 unique locations geocoded via OpenStreetMap Nominatim |
| 📊 **Live statistics** | Real-time counts: total places, public/private split, recommended badges |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Vanilla HTML/CSS/JS — zero dependencies, one file |
| **CSV parsing** | [PapaParse](https://www.papaparse.com/) (CDN) |
| **Geocoding** | OpenStreetMap Nominatim API + Python batch script |
| **Distance** | Haversine formula (client-side) |
| **Persistence** | Browser `localStorage` for favorites |
| **Data source** | [krdo.pl](https://krdo.pl/) — scraped with Python + BeautifulSoup |
| **Deployment** | GitHub Pages |

---

## 📁 Repository Structure

```
├── index.html                 # Main application (SPA)
├── krdo_dps_poland.csv        # Full dataset (3,475 records)
├── locations_geo.json         # Pre-geocoded coordinates (405 locations)
├── scrape_krdo.py             # Web scraper (Python + BeautifulSoup)
├── geocode_locations.py       # Geocoding pipeline (Python + Nominatim)
├── explore.py                 # Data analysis script
└── README.md
```

---

## 🔧 Data Pipeline

```
krdo.pl (website)
    ↓  scrape_krdo.py (requests + BeautifulSoup, 387 pages, 1.5s delay)
krdo_dps_poland.csv (3,475 records, 714 KB)
    ↓  geocode_locations.py (Nominatim API, 1.1s/req, 405 unique locations)
locations_geo.json (405 geocoded locations, 100% success rate)
    ↓  index.html loads both files
Interactive web app
```

- **Scraper:** Paginates through all 387 pages with polite delays, parses HTML tables, extracts badges (KIDO recommendations), and saves UTF-8-BOM CSV for Excel compatibility.
- **Geocoding:** Extracts 405 unique location strings (powiats, cities), geocodes via OpenStreetMap with smart query fallback, caches to JSON, periodic saves every 20 locations.
- **App:** Loads CSV via File API + PapaParse, loads geo JSON via fetch, computes Haversine distances on-the-fly.

---

## 🚀 Getting Started

### Local development
```bash
python -m http.server 8080
# Open http://localhost:8080
# Click "Wybierz plik" and load krdo_dps_poland.csv
```

### Production (GitHub Pages)
1. Push this repo to GitHub
2. Settings → Pages → deploy from `main` branch `/ (root)`
3. Done — fully client-side, no backend needed

---

## 📊 Dataset Stats

| Metric | Value |
|--------|-------|
| Total facilities | 3,475 |
| Total bed capacity | ~192,600 |
| Public facilities | 919 |
| Private facilities | 818 |
| KIDO Recommended | 318 |
| Intellectually disabled | 253 |

---

## 📄 License

Data sourced from [Krajowy Rejestr Domów Opieki (KRDO)](https://krdo.pl/).  
This project is for educational and personal use.

---

*Built with ❤️ for Babcia*
