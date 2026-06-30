"""
Scraper for Krajowy Rejestr Domów Opieki (KRDO)
Fetches all care homes (DPS) in Poland from krdo.pl
"""

import requests
from bs4 import BeautifulSoup, Tag
import csv
import time
import os

BASE_URL = "https://krdo.pl/rejestr/wszystkie-wojewodztwa/wszystkie-powiaty/wszystkie/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
OUTPUT_FILE = "krdo_dps_poland.csv"
TOTAL_PAGES = 387  # Based on "Liczba wyników: 3475"


def parse_name_cell(cell: Tag):
    """
    Parse the first column containing the facility name and badges.
    Returns (facility_name, badges_comma_separated).
    """
    # Extract badges from inner spans that have CSS classes (recommended-badge, registered-badge)
    badges = []
    for span in cell.find_all("span", class_=True):
        badge_text = span.get_text(strip=True)
        if badge_text and badge_text not in badges:
            badges.append(badge_text)

    # The facility name is the last text node in the cell
    all_texts = [t.strip() for t in cell.find_all(string=True, recursive=True) if t.strip()]
    facility_name = all_texts[-1] if all_texts else ""

    return facility_name, ", ".join(badges)


def parse_page(page_num: int) -> list[dict]:
    """Parse a single page and return a list of records."""
    if page_num == 1:
        url = BASE_URL
    else:
        url = f"{BASE_URL}page/{page_num}/"

    print(f"Fetching page {page_num}/{TOTAL_PAGES}")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  ERROR fetching page {page_num}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    records = []

    # Find the main results table (first table with expected header)
    table = None
    for t in soup.find_all("table"):
        header_row = t.find("tr")
        if header_row and "Nazwa Instytucji Opiekuńczej" in header_row.get_text():
            table = t
            break

    if not table:
        print(f"  WARNING: No results table found on page {page_num}")
        return []

    rows = table.find_all("tr")
    data_rows = rows[1:]  # Skip header row

    for row in data_rows:
        cells = row.find_all("td")
        if len(cells) < 6:
            continue

        facility_name, badges = parse_name_cell(cells[0])
        location = cells[1].get_text(strip=True) if len(cells) > 1 else ""
        address = cells[2].get_text(" ", strip=True) if len(cells) > 2 else ""
        activity_type = cells[3].get_text(" ", strip=True) if len(cells) > 3 else ""
        places = cells[4].get_text(strip=True) if len(cells) > 4 else ""
        krdo_entry = cells[5].get_text(strip=True) if len(cells) > 5 else ""

        records.append({
            "nazwa_instytucji": facility_name,
            "badges": badges,
            "lokalizacja": location,
            "adres": address,
            "rodzaj_dzialalnosci": activity_type,
            "ilosc_miejsc": places,
            "wpis_krdo": krdo_entry,
            "strona": page_num,
        })

    print(f"  -> {len(records)} records found")
    return records


def save_csv(records: list[dict], filepath: str):
    """Save records to CSV with UTF-8 BOM for Excel compatibility."""
    fieldnames = [
        "nazwa_instytucji", "badges", "lokalizacja", "adres",
        "rodzaj_dzialalnosci", "ilosc_miejsc", "wpis_krdo", "strona"
    ]
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    print(f"  Saved {len(records)} records to {filepath}")


def scrape_all():
    """Scrape all pages and save to CSV."""
    all_records = []

    for page in range(1, TOTAL_PAGES + 1):
        records = parse_page(page)
        all_records.extend(records)

        # Polite delay between requests
        if page < TOTAL_PAGES:
            time.sleep(0.2)  # 20ms delay

        # Interim save every 20 pages
        if page % 20 == 0:
            print(f"\n=== Progress: {page}/{TOTAL_PAGES} pages, {len(all_records)} records ===\n")
            save_csv(all_records, OUTPUT_FILE)

    # Final save
    save_csv(all_records, OUTPUT_FILE)
    print(f"\n{'='*60}")
    print(f"COMPLETE! Total records: {len(all_records)}")
    print(f"Saved to: {os.path.abspath(OUTPUT_FILE)}")
    print(f"{'='*60}")
    return all_records


if __name__ == "__main__":
    scrape_all()
