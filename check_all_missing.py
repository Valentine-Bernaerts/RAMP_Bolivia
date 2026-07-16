import pandas as pd
from pathlib import Path

SERVICE_COLUMNS = [
    'sufficiency_illumination',
    'sufficiency_ICT',
    'sufficiency_cold_storage',
    'sufficiency_thermal_comfort',
    'small_school_illumination',
    'small_school_ICT',
    'entertainment_business_illumination',
    'entertainment_business_ICT',
    'entertainment_business_cold_storage',
    'rice_processing_rice_processing',
    'restaurant_illumination',
    'restaurant_cold_storage',
    'restaurant_kitchen',
    'store_illumination',
    'store_ICT',
    'store_cold_storage',
    'workshop_illumination',
    'workshop_ICT',
    'workshop_machinery',
]

OUTPUT_DIR = Path('output_norte_amazonia_reality')
INPUT_FILENAME = 'load_curve_energy_service_full_year_Norte_Amazonia_reality.csv'

results = {}
for p in sorted([d for d in OUTPUT_DIR.iterdir() if d.is_dir()], key=lambda x: x.name):
    file_path = p / INPUT_FILENAME
    if not file_path.exists():
        results[p.name] = ['MISSING_FILE']
        continue
    try:
        df = pd.read_csv(file_path)
        missing = [c for c in SERVICE_COLUMNS if c not in df.columns]
        results[p.name] = missing
    except Exception as e:
        results[p.name] = [f'ERROR: {e}']

# Print summary
for name, missing in results.items():
    if not missing:
        print(f'{name}: OK')
    else:
        print(f'{name}: MISSING {missing}')

# Print municipalities missing any column
missing_any = {name: m for name, m in results.items() if m and m != ['MISSING_FILE']}
print('\nMunicipalities with missing columns:')
for name, m in missing_any.items():
    print(f'- {name}: {m}')
