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

# Check Santa_Rosa_Pando
file_pando = Path('output_norte_amazonia_reality/Santa_Rosa_Pando/load_curve_energy_service_full_year_Norte_Amazonia_reality.csv')
file_beni = Path('output_norte_amazonia_reality/Santa_Rosa_Beni/load_curve_energy_service_full_year_Norte_Amazonia_reality.csv')

for name, file_path in [("Pando", file_pando), ("Beni", file_beni)]:
    print(f"\n{name}:")
    try:
        df = pd.read_csv(file_path)
        print(f"  Columns in CSV: {list(df.columns)}")
        missing = [col for col in SERVICE_COLUMNS if col not in df.columns]
        if missing:
            print(f"  MISSING COLUMNS: {missing}")
        else:
            print(f"  All columns present!")
    except Exception as e:
        print(f"  ERROR: {e}")
