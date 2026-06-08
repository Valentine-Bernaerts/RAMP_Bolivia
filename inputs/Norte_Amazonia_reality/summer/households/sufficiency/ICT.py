from ramp.core.core import User
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

REDUCTION_FACTOR = 0.7  # off-grid capacity constraint

municipality = os.environ.get("RAMP_MUNICIPALITY", "")

def _load_ict_rates(muni):
    row = _find_row(muni)
    if row is None:
        return {"radio": 0.1, "tv": 0.1, "laptop": 0.3, "phone": 0.2}
    # Column indices in CSV_final.csv (0-based, 2024, Sin especificar excluded)
    # 107=Radio Tiene, 108=Radio NoTiene
    # 110=TV Tiene,    111=TV NoTiene
    # 113=Laptop Tiene,114=Laptop NoTiene
    # 116=Phone Tiene, 117=Phone NoTiene
    return {
        "radio":  _rate(row[107], row[108]),
        "tv":     _rate(row[110], row[111]),
        "laptop": _rate(row[113], row[114]),
        "phone":  _rate(row[116], row[117]),
    }

_rates = _load_ict_rates(municipality)

User_list = []
HICT = User("household ICT", 1)
User_list.append(HICT)

# TV: census ownership rate x REDUCTION_FACTOR (off-grid capacity constraint)
HICT_TV = HICT.add_appliance(1, 30, 2, 120, 0.1, 5, occasional_use=_rates["tv"] * REDUCTION_FACTOR)
HICT_TV.windows([1080, 1440], [0, 60], 0.35)

# Radio: census ownership rate, no reduction (low-power, small-solar compatible)
HICT_Radio = HICT.add_appliance(1, 3, 2, 120, 0.1, 5, occasional_use=_rates["radio"])
HICT_Radio.windows([390, 450], [1082, 1260], 0.35)

# Phone charger: census ownership rate, no reduction
HICT_Phone_charger = HICT.add_appliance(4, 5, 2, 120, 0.2, 10, occasional_use=_rates["phone"])
HICT_Phone_charger.windows([1020, 1440], [0, 300], 0.35)

# Laptop: census ownership rate x REDUCTION_FACTOR
HICT_Laptop = HICT.add_appliance(1, 70, 1, 90, 0.3, 30, occasional_use=_rates["laptop"] * REDUCTION_FACTOR)
HICT_Laptop.windows([960, 1200], [0, 0], 0.35)
