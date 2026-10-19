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
    norm_name = c_name.lower().replace(' ', '').replace('-', '').replace("'", "")
    s1_data[norm_name] = (r_idx, c_name, row)

for c in counties:
    code = c['code']
    name = c['name']
    norm = name.lower().replace(' ', '').replace('-', '').replace("'", "")
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

    r_idx, s1_name, s1_row = s1_data[norm]
    docx_row = r_idx + 1  # 1-based row in docx table
    data_row = r_idx - 1  # 1-based row in data rows (1..47)
    icu_total_str = s1_row[8].strip()
    icu_total = int(icu_total_str) if icu_total_str else 0

    if icu_total > 0:
        c['icu_beds_verified'] = icu_total
        c['icu_source'] = f"Barasa et al. (2020) PLOS ONE 15(7):e0236308, S1 Table, Fila {docx_row} (Dato #{data_row} {s1_name}), Columna 9 (ICU Beds Total). DOI: 10.1371/journal.pone.0236308.s001"
    else:
        c['icu_beds_verified'] = None
        c['icu_source'] = f"Barasa et al. (2020) PLOS ONE 15(7):e0236308, S1 Table, Fila {docx_row} (Dato #{data_row} {s1_name}) registra 0 camas; sin fuente verificable de camas UCI operativas (null). DOI: 10.1371/journal.pone.0236308.s001"
    c['poverty_quintiles'] = None
    c['quintiles_source'] = None
    c['data_quality_flags'] = [
        'verified_knbs_2019_census_table_2_2',
        'verified_barasa_2020_s1_icu_census',
        'no_county_poverty_quintiles_unverified_removed'
    ]

with open('backend/app/data/kenya_47_counties_verified.json', 'w', encoding='utf-8') as f:
    json.dump(counties, f, indent=2, ensure_ascii=False)

print('Updated kenya_47_counties_verified.json successfully!')
