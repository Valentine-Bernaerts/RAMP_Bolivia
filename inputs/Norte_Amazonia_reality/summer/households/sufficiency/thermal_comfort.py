from ramp.core.core import User
import pandas as pd
import csv, os, unicodedata

# Maps RAMP_MUNICIPALITY env var -> (CSV MUNICIPIO name, CSV DEPARTAMENTO)
_MUNI_MAP = {
    "Exaltacion":            ("Exaltación",         "Beni"),
    "Guayaramerin":          ("Guayaramerín",        "Beni"),
    "Reyes":                 ("Reyes",                  "Beni"),
    "Riberalta":             ("Riberalta",              "Beni"),
    "Santa_Rosa_Beni":       ("Santa Rosa",             "Beni"),
    "Ixiamas":               ("Ixiamas",                "La Paz"),
    "Bella_Flor":            ("Bella Flor",             "Pando"),
    "Bolpebra":              ("Bolpebra",               "Pando"),
    "Cobija":                ("Cobija",                 "Pando"),
    "Filadelfia":            ("Filadelfia",             "Pando"),
    "Ingavi":                ("Ingavi",                 "Pando"),
    "Nueva_Esperanza":       ("Nueva Esperanza",        "Pando"),
    "Porvenir":              ("Porvenir",               "Pando"),
    "Puerto_Gonzalo_Moreno": ("Puerto Gonzalo Moreno",  "Pando"),
    "Puerto_Rico":           ("Puerto Rico",            "Pando"),
    "San_Lorenzo":           ("San Lorenzo",            "Pando"),
    "San_Pedro":             ("San Pedro",              "Pando"),
    "Santa_Rosa_Pando":      ("Santa Rosa",             "Pando"),
    "Santos_Mercado":        ("Santos Mercado",         "Pando"),
    "Sena":                  ("Sena",                   "Pando"),
    "Villa_Nueva":           ("Villa Nueva",            "Pando"),
}

def _csv_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "..", ".."))
    return os.path.join(project_root, "data", "CSV_final.csv")

def _nfc(s):
    return unicodedata.normalize("NFC", s.strip())

def _rate(t, n):
    t, n = float(t or 0), float(n or 0)
    return t / (t + n) if (t + n) > 0 else 0.0

def _find_row(municipality):
    if municipality not in _MUNI_MAP:
        return None
    csv_muni, csv_dep = _MUNI_MAP[municipality]
    with open(_csv_path(), encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if _nfc(row[1]) == csv_dep and _nfc(row[3]) == csv_muni:
                return row
    return None

FAN_FACTOR = 1.0  # MTF Tier 2: fan grouped with TV

municipality = os.environ.get('RAMP_MUNICIPALITY', '')
season = os.environ.get('RAMP_SEASON')

# No dedicated census fan question; MTF groups the fan with TV at Tier 2,
# so retention is indexed on TV ownership (cols 110/111). Fallback 0.1 only
# applies when the municipality has no census row.
_census_row = _find_row(municipality) if municipality else None
tv_rate = _rate(_census_row[110], _census_row[111]) if _census_row is not None else 0.1

if municipality and season:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..', '..'))
    csv_path = os.path.join(project_root, 'data', 'thermal_comfort_lookup.csv')
    df = pd.read_csv(csv_path)
    row = df[(df['municipality'] == municipality) & (df['season'] == season)]
    if not row.empty:
        func_time = int(row['func_time'].iloc[0])
    else:
        print(f'Warning: No thermal comfort data for {municipality} {season}, using default 420')
        func_time = 420
else:
    func_time = 420

User_list = []
HSC = User('household space cooling', 1)
User_list.append(HSC)

# Fan: no census fan ownership rate; indexed on TV ownership x MTF Tier 2 factor
HSC_Fan = HSC.add_appliance(1, 30, 2, func_time, 0.27, 30, occasional_use=tv_rate * FAN_FACTOR)
HSC_Fan.windows([480, 1260], [0, 0], 0.35)
