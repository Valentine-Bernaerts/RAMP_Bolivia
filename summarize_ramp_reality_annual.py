"""Summarize annual RAMP reality energy service curves for Norte Amazónia.

Reads each municipality's
output_norte_amazonia_reality/<municipality>/load_curve_energy_service_full_year_Norte_Amazonia_reality.csv
and computes annual GWh sums per service.

The output file is saved as
output_norte_amazonia_reality/ramp_reality_annual_summary.csv
"""

from pathlib import Path
import pandas as pd

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
OUTPUT_FILE = OUTPUT_DIR / 'ramp_reality_annual_summary.csv'
INPUT_FILENAME = 'load_curve_energy_service_full_year_Norte_Amazonia_reality.csv'


def summarize_municipality(folder: Path) -> dict:
    file_path = folder / INPUT_FILENAME
    if not file_path.exists():
        raise FileNotFoundError(f'Missing file for municipality {folder.name}: {file_path}')

    # Read CSV but only use columns that exist (ignore missing ones)
    df = pd.read_csv(file_path)
    available_cols = [col for col in SERVICE_COLUMNS if col in df.columns]
    
    if not available_cols:
        raise ValueError(f'No service columns found in {file_path}')
    
    df = df[available_cols]
    if df.empty:
        raise ValueError(f'No data read from {file_path}')

    annual_watts = df.sum(axis=0, numeric_only=True)
    annual_gwh = annual_watts / 60e9

    return {col: float(annual_gwh.get(col, 0.0)) for col in SERVICE_COLUMNS}


def build_summary():
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    municipalities = sorted(
        [p for p in OUTPUT_DIR.iterdir() if p.is_dir()],
        key=lambda p: p.name.lower()
    )

    rows = []
    for municipality_folder in municipalities:
        print(f'Processing {municipality_folder.name}...', end=' ')
        try:
            values = summarize_municipality(municipality_folder)
            print('OK')
        except FileNotFoundError as e:
            print(f'Warning: {e}')
            continue
        except Exception as e:
            print(f'ERROR: {e}')
            import traceback
            traceback.print_exc()
            continue

        values['municipality'] = municipality_folder.name
        values['TOTAL_GWh'] = sum(values[col] for col in SERVICE_COLUMNS)
        rows.append(values)

    if not rows:
        raise RuntimeError('No municipality summaries were generated.')

    summary_df = pd.DataFrame(rows)
    total_row = {
        'municipality': 'TOTAL',
        **{col: summary_df[col].sum() for col in SERVICE_COLUMNS},
        'TOTAL_GWh': summary_df['TOTAL_GWh'].sum(),
    }
    summary_df = pd.concat([summary_df, pd.DataFrame([total_row])], ignore_index=True)

    ordered_columns = ['municipality', 'TOTAL_GWh'] + SERVICE_COLUMNS
    summary_df = summary_df[ordered_columns]

    summary_df.to_csv(OUTPUT_FILE, index=False)
    print(f'SUCCESS: Saved summary to {OUTPUT_FILE}')


if __name__ == '__main__':
    build_summary()
