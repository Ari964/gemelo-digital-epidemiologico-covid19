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

lines = []
lines.append("| Código | Condado (KNBS 2019) | Fila en `S1 Table` (Docx) | Nombre en `S1 Table` | Columna en `S1 Table` | Camas UCI Oficiales (Total) | Desglose por Sector en S1 Table |")
lines.append("| :---: | :--- | :---: | :--- | :---: | :---: | :--- |")

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
    docx_row = r_idx + 1
    data_row = r_idx - 1
    pub = s1_row[5] if s1_row[5] else '0'
    priv = s1_row[6] if s1_row[6] else '0'
    fbo = s1_row[7] if s1_row[7] else '0'
    tot = s1_row[8] if s1_row[8] else '0'
    lines.append(f"| **{code}** | {name} | Fila {docx_row} (Dato #{data_row}) | *{s1_name}* | Col. 9 (*ICU Beds Total*) | **{tot}** | Pública: {pub}, Privada: {priv}, FBO: {fbo} |")

out_table = "\n".join(lines)
with open('scripts/county_audit_table.md', 'w', encoding='utf-8') as f:
    f.write(out_table)

print(f"Generated {len(lines)-2} county rows in scripts/county_audit_table.md")
