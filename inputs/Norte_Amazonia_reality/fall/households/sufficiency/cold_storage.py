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

FRIDGE_FACTOR = 0.28  # MTF Tier 3 load; solar-only (Tier 2) can't run it

municipality = os.environ.get("RAMP_MUNICIPALITY", "")

def _load_fridge_rate(muni):
    row = _find_row(muni)
    if row is None:
        return 0.0
    # Col 73=Refrigerador Tiene, 74=No tiene (2024, Sin especificar excluded)
    return _rate(row[73], row[74])

_fridge_rate = _load_fridge_rate(municipality)

User_list = []
HCS = User("household cold storage", 1)
User_list.append(HCS)

# Fridge/freezer: census ownership rate x MTF blended factor (generator share only)
HCS_Freezer = HCS.add_appliance(1, 200, 1, 1440, 0, 30, "yes", 3,
                                occasional_use=_fridge_rate * FRIDGE_FACTOR)
HCS_Freezer.windows([0, 1440], [0, 0])
HCS_Freezer.specific_cycle_1(200, 20, 5, 10)  # intensivo
HCS_Freezer.specific_cycle_2(200, 15, 5, 15)  # intermedio
HCS_Freezer.specific_cycle_3(200, 10, 5, 20)  # standard
HCS_Freezer.cycle_behaviour([480, 1200], [0, 0], [300, 479], [0, 0], [0, 299], [1201, 1440])
