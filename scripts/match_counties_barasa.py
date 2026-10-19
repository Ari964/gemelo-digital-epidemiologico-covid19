import json
import csv

with open('backend/app/data/kenya_47_counties_verified.json', encoding='utf-8') as f:
    counties = json.load(f)

with open('data/raw/barasa_2020_surge_capacity_s1_table.csv', encoding='utf-8') as f:
    reader = list(csv.reader(f))

s1_data = {}
for r_idx in range(2, len(reader)):
    row = reader[r_idx]
    c_name = row[0].strip()
    norm_name = c_name.lower().replace(' ', '').replace('-', '').replace("'", '')
    s1_data[norm_name] = (r_idx, c_name, row)

print(f'Counties in JSON: {len(counties)}, Counties in S1: {len(s1_data)}')

matches = []
for c in counties:
    code = c['code']
    name = c['name']
    norm = name.lower().replace(' ', '').replace('-', '').replace("'", '')
    if 'nairobi' in norm:
        norm = 'nairobi'
    if 'elgeyo' in norm:
        norm = 'elgeyomarakwet'
    if 'tharaka' in norm:
        norm = 'tharakanithi'
    if 'taita' in norm:
        norm = 'taitataveta'
    if 'transnzoia' in norm:
        norm = 'transnzoia'
    if 'westpokot' in norm:
        norm = 'westpokot'
    if 'homabay' in norm:
        norm = 'homabay'

    if norm in s1_data:
        r_idx, s1_name, s1_row = s1_data[norm]
        icu_total_str = s1_row[8].strip()
        icu_total = int(icu_total_str) if icu_total_str else 0
        matches.append((code, name, r_idx, s1_name, icu_total, s1_row))
    else:
        print(f'NO MATCH for {name} (code {code})')

print(f'Successfully matched {len(matches)} out of {len(counties)} counties!')

# Print summary table sorted by county code
matches.sort(key=lambda x: x[0])
print(f"{'Code':<5} {'County Name':<20} {'S1 Row (docx)':<15} {'S1 County':<20} {'ICU Total (Col 9)':<18}")
print("-" * 80)
for code, name, r_idx, s1_name, icu_total, s1_row in matches:
    # Note: in docx table, row 0 is header block 1, row 1 is header block 2.
    # So r_idx 2 is row 1 of counties, or row 3 in 1-based table indexing.
    # In S1 Table (excluding headers): r_idx - 1 is the 1-based county row (1 to 47).
    county_row_num = r_idx - 1
    print(f"{code:<5} {name:<20} Fila {county_row_num:<10} {s1_name:<20} {icu_total:<18}")
