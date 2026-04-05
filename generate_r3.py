import pandas as pd
import json

# Load all needed data
df = pd.read_excel('C:/Users/Administrator/gaza_vaccination/data/person_vaccine_tb_r3.xlsx', sheet_name='Export Worksheet')
df_phc = pd.read_excel('C:/Users/Administrator/gaza_vaccination/data/phc_center_tb.xlsx')
df_phc_upd = pd.read_excel('C:/Users/Administrator/gaza_vaccination/data/phc_center_updated.xlsx')
df_geo = pd.read_excel('C:/Users/Administrator/gaza_vaccination/data/geolocation_tb.xlsx', sheet_name='GEOLOCATION_TB')
df_loc = pd.read_csv('C:/Users/Administrator/gaza_vaccination/data/location_point_unified_corrected.csv')

with open('C:/Users/Administrator/gaza_vaccination/data/vaccination_individual_data.js', 'r', encoding='utf-8') as f:
    content = f.read()
json_str = content[len('var json_vaccination_individual_data = '):-1]
indiv_data = json.loads(json_str)

# Build facility map from individual data
indiv_facility_map = {}
for feat in indiv_data['features']:
    p = feat['properties']
    name_en = p.get('Health Facility', '')
    if name_en:
        indiv_facility_map[name_en] = {
            'ar': p.get('Health Facility AR', ''),
            'gov': p.get('Governorate', ''),
            'org': p.get('Organization', ''),
            'coords': feat['geometry']['coordinates']
        }

# Build location CSV map
loc_en_map = {}
for _, row in df_loc.iterrows():
    en = str(row['Medical Point - Health Facility Name in English']).strip()
    loc_en_map[en] = [float(row['Long']), float(row['Lat'])]

# Build PHC reference
df_phc_geo = df_phc[['PHC_CENTER_ID', 'NAME_AR', 'NAME_EN', 'GEOLOCATION_ID', 'PHC_TYPE_ID']].merge(
    df_geo[['GEOLOCATION_ID', 'NAME_EN', 'NAME_AR']].rename(columns={'NAME_EN': 'GEO_NAME_EN', 'NAME_AR': 'GEO_NAME_AR'}),
    on='GEOLOCATION_ID', how='left'
)
df_phc_geo = df_phc_geo.merge(
    df_phc_upd[['PHC_CENTER_ID', 'ar_name', 'en_name']],
    on='PHC_CENTER_ID', how='left'
)

gov_map = {
    'Gaza': 'Gaza',
    'Middle': 'Middle zone',
    'Khan younis': 'Khan Younis',
    'North Gaza': 'North Gaza',
    'Rafah': 'Rafah'
}

# Vaccine dose ID mapping
VACCINE_MAP = {
    1: 'BCG',
    2: 'HepB',
    3: 'IPV1',
    4: 'IPV2',
    5: 'bOPV1',
    6: 'bOPV2',
    7: 'bOPV3',
    8: 'bOPV4',
    9: 'Rota1',
    10: 'Rota2',
    11: 'Rota3',
    12: 'Penta1',
    13: 'Penta2',
    14: 'Penta3',
    15: 'PCV1',
    16: 'PCV2',
    17: 'PCV3',
    18: 'MMR1',
    19: 'MMR2',
    20: 'DTP',
    21: 'DTP',   # DT maps to DTP
    27: 'bOPV5',
    29: 'HepB',
    30: 'HepB',
    32: 'HepB',
}

# Manual overrides for facilities without en_name in phc_center_updated
manual_override = {
    43: {
        'en': 'Al-Sawarha (Al-Khawaldeh) Center',
        'ar': '\u0639\u064a\u0627\u062f\u0629 \u0627\u0644\u0633\u0648\u0627\u0631\u062d\u0629 \u0627\u0644\u062e\u0648\u0627\u0644\u062f\u0629',
        'gov': 'Middle zone',
        'org': 'Medecins du Monde',
        'coords': [34.3671, 31.438575]
    },
    290: {
        'en': 'Mobile Team - 1 - Deir al-Balah',
        'ar': '\u0627\u0644\u0641\u0631\u064a\u0642 \u0627\u0644\u0645\u062a\u0646\u0642\u0644 -1 - \u062f\u064a\u0631 \u0627\u0644\u0628\u0644\u062d',
        'gov': 'Middle zone',
        'org': 'IMC',
        'coords': [34.346268, 31.432989]
    },
    301: {
        'en': 'Al-Bahr Primary Health Care Center /MdM F',
        'ar': '\u0627\u0644\u0628\u062d\u0631 MDM',
        'gov': 'Middle zone',
        'org': 'Medecins du Monde',
        'coords': [34.320301, 31.408829]
    },
}

vaccine_cols = ['BCG', 'HepB', 'IPV1', 'IPV2', 'bOPV1', 'bOPV2', 'bOPV3', 'bOPV4', 'bOPV5',
                'Rota1', 'Rota2', 'Rota3', 'Penta1', 'Penta2', 'Penta3',
                'PCV1', 'PCV2', 'PCV3', 'MMR1', 'MMR2', 'DTP']

features = []
summary = {
    'TotalChildren': 0,
    'OnSchedule': 0,
    'Defaulter': 0,
    'ZeroDose': 0,
    'Age012': 0,
    'Age1224': 0,
    'Age24plus': 0,
    'TotalVaccinations': 0,
    'vaccines': {v: 0 for v in vaccine_cols}
}

for phc_id, group in df.groupby('PHC_ENTRY_ID'):
    phc_id = int(phc_id)

    if phc_id in manual_override:
        mo = manual_override[phc_id]
        en_name = mo['en']
        ar_name = mo['ar']
        gov = mo['gov']
        org = mo['org']
        coords = mo['coords']
    else:
        rows = df_phc_geo[df_phc_geo['PHC_CENTER_ID'] == phc_id]
        if len(rows) == 0:
            en_name = 'Unknown-{}'.format(phc_id)
            ar_name = ''
            gov = ''
            org = ''
            coords = [0.0, 0.0]
        else:
            row = rows.iloc[0]
            en_name_upd = row['en_name'] if pd.notna(row['en_name']) else None
            ar_name_upd = row['ar_name'] if pd.notna(row['ar_name']) else None
            ar_name_raw = row['NAME_AR'] if pd.notna(row['NAME_AR']) else ''
            ar_name = ar_name_upd if ar_name_upd else ar_name_raw
            geo_gov = row['GEO_NAME_EN'] if pd.notna(row['GEO_NAME_EN']) else ''
            gov = gov_map.get(geo_gov, geo_gov)

            if en_name_upd and en_name_upd in indiv_facility_map:
                d = indiv_facility_map[en_name_upd]
                en_name = en_name_upd
                coords = d['coords']
                org = d['org']
                gov = d['gov']
                if not ar_name:
                    ar_name = d['ar']
            elif en_name_upd and en_name_upd in loc_en_map:
                en_name = en_name_upd
                coords = loc_en_map[en_name_upd]
                org = ''
            else:
                en_name = en_name_upd if en_name_upd else 'Unknown-{}'.format(phc_id)
                org = ''
                coords = [0.0, 0.0]

    # Per-person aggregation
    person_data = group.groupby('PERSON_ID').agg(
        age_type=('CHILDREN_AGE_TYPE', 'first'),
        vax_status=('CHILD_VACCINATION_STATUS', 'first')
    ).reset_index()

    total_children = len(person_data)
    total_vaccinations = len(group)
    age_012 = int((person_data['age_type'] == 1).sum())
    age_1224 = int((person_data['age_type'] == 2).sum())
    age_24plus = int((person_data['age_type'] == 3).sum())
    on_schedule = int((person_data['vax_status'] == 2).sum())
    defaulter = int((person_data['vax_status'] == 3).sum())
    zero_dose = int((person_data['vax_status'] == 1).sum())

    # Per-vaccine counts
    vax_counts = {v: 0 for v in vaccine_cols}
    for _, vrow in group.iterrows():
        dose_id = int(vrow['VACCINE_DOSES_ID'])
        vax_name = VACCINE_MAP.get(dose_id)
        if vax_name and vax_name in vax_counts:
            vax_counts[vax_name] += 1

    props = {
        'Health Facility': en_name,
        'Health Facility AR': ar_name,
        'Governorate': gov,
        'Organization': org,
        'TotalChildren': total_children,
        'TotalVaccinations': total_vaccinations,
        'Age 0-12': age_012,
        'Age 12-24': age_1224,
        'Age 24+': age_24plus,
        'OnSchedule': on_schedule,
        'Defaulter': defaulter,
        'ZeroDose': zero_dose,
        'Round': 'Round 3'
    }
    props.update(vax_counts)

    feature = {
        'type': 'Feature',
        'properties': props,
        'geometry': {'type': 'Point', 'coordinates': coords}
    }
    features.append(feature)

    # Update summary
    summary['TotalChildren'] += total_children
    summary['OnSchedule'] += on_schedule
    summary['Defaulter'] += defaulter
    summary['ZeroDose'] += zero_dose
    summary['Age012'] += age_012
    summary['Age1224'] += age_1224
    summary['Age24plus'] += age_24plus
    summary['TotalVaccinations'] += total_vaccinations
    for v in vaccine_cols:
        summary['vaccines'][v] += vax_counts[v]

output = {
    'type': 'FeatureCollection',
    'features': features,
    'summary': summary
}

js_content = 'var json_vaccination_r3_data = ' + json.dumps(output, ensure_ascii=False) + ';'

with open('C:/Users/Administrator/gaza_vaccination/data/vaccination_r3_data.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print('Done! Written {} features.'.format(len(features)))
print('Summary:', json.dumps(summary, indent=2))
print()
print('Facility list:')
for feat in features:
    p = feat['properties']
    print('  PHC_ID check: {} | {} | {} | {} children | {}'.format(
        p['Health Facility'], p['Governorate'], p['Organization'],
        p['TotalChildren'], feat['geometry']['coordinates']
    ))
