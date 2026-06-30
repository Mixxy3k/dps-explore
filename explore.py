"""
Explore KRDO dataset - find care homes suitable for autism / mental disability
"""
import csv
from collections import Counter

with open("krdo_dps_poland.csv", "r", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

print(f"Total records: {len(rows)}")
print()

# ============================================================
# 1. Specifically: intellectually disabled (niepełnosprawni intelektualnie)
# ============================================================
print("=" * 60)
print("=== DPS dla NIEPEŁNOSPRAWNYCH INTELEKTUALNIE ===")
print()

intel = [r for r in rows if "intelektualnie" in r["rodzaj_dzialalnosci"].lower()]
print(f"Total: {len(intel)}")

# Group by type
types = Counter()
for r in intel:
    types[r["rodzaj_dzialalnosci"]] += 1

print()
print("Categories:")
for t, c in types.most_common():
    clean = t.replace("\n", " ").replace("\t", " ").strip()
    print(f"  [{c}] {clean[:150]}")

print()
print("Sample places:")
for r in intel[:20]:
    adr = r["adres"].replace("\n", " ").replace("\t", " ").strip()
    rdz = r["rodzaj_dzialalnosci"].replace("\n", " ").replace("\t", " ").strip()
    print(f'  {r["nazwa_instytucji"]}')
    print(f'    Lok: {r["lokalizacja"]} | Adres: {adr}')
    print(f'    Typ: {rdz[:130]}')
    print(f'    Miejsc: {r["ilosc_miejsc"]} | Badges: {r["badges"]}')
    print()

# ============================================================
# 2. Also: mentally ill (przewlekle psychicznie chorych)
# ============================================================
print("=" * 60)
print("=== DPS dla PRZEWLEKLE PSYCHICZNIE CHORYCH ===")
print()

psych = [r for r in rows if "psychicznie" in r["rodzaj_dzialalnosci"].lower()]
combined = [r for r in psych if "intelektualnie" in r["rodzaj_dzialalnosci"].lower()]
print(f"Psychicznie chorych - total: {len(psych)}")
print(f"  w tym również z niepełnosprawnością intelektualną: {len(combined)}")
print()

# Group psych types
ptypes = Counter()
for r in psych:
    ptypes[r["rodzaj_dzialalnosci"]] += 1

print("Categories:")
for t, c in ptypes.most_common(15):
    clean = t.replace("\n", " ").replace("\t", " ").strip()
    print(f"  [{c}] {clean[:150]}")
print()

# ============================================================
# 3. Write a filtered CSV with just intellectually disabled places
# ============================================================
print("=" * 60)
print("=== Exporting filtered CSV ===")
print()

fieldnames = [
    "nazwa_instytucji", "badges", "lokalizacja", "adres",
    "rodzaj_dzialalnosci", "ilosc_miejsc", "wpis_krdo", "strona",
]

with open("krdo_intellectually_disabled.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(intel)

print(f"Saved {len(intel)} records to krdo_intellectually_disabled.csv")
print()

# ============================================================
# 4. Also export combined mentally ill + intellectually disabled
# ============================================================
with open("krdo_mental_health.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(psych)

print(f"Saved {len(psych)} records to krdo_mental_health.csv")
