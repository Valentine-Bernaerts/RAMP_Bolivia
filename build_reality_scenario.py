"""
Build Norte_Amazonia_reality input folder for RAMP.
Scenario: "Reality, Source B" - households off the public grid.
Run from the RAMP_Bolivia project root.
"""

import os
import shutil

ROOT    = os.path.dirname(os.path.abspath(__file__))
SRC     = os.path.join(ROOT, "inputs", "Norte_Amazonia")
DST     = os.path.join(ROOT, "inputs", "Norte_Amazonia_reality")
SEASONS = ["fall", "spring", "summer", "winter"]

# ESMAP Multi-Tier Framework (Bhatia & Angelou 2015, "Beyond Connections -
# Energy Access Redefined"), Table 2 service matrix and tier->source mapping:
#   - Solar home system (SHS) -> MTF Tier 2
#   - Generator / mini-grid   -> MTF Tier 3 (adds fridge-capable loads)
# Each factor below blends the Source B sub-source mix already computed
# upstream (~53% solar / 47% generator, "otra" split 50/50) into a single
# retention factor per appliance, applied once on the existing hh_sourceB
# user-type (sub-sources are NOT split into separate RAMP users).
#   tv:     Tier 2 explicitly lists TV as a served appliance -> full rate on
#           both sub-sources (1.00 solar, 1.00 generator) -> blended 1.00
#   fan:    Tier 2 explicitly lists "fan if needed" -> same as TV -> 1.00
#   laptop: medium-power appliance, partially served at Tier 2 -> 0.5 (solar)
#           / 0.8 (generator), blended 53/47 -> 0.65
#   fridge: Tier 3-only load; solar-only households (Tier 2) cannot run a
#           fridge, so the factor collapses toward the generator share only
#           -> 0.0 (solar) / 0.6 (generator), blended 53/47 -> 0.28
MTF_FACTOR = {
    "tv":     1.00,
    "fan":    1.00,
    "laptop": 0.65,
    "fridge": 0.28,
}

# Shared municipality-lookup helpers embedded in each file
MUNI_HELPERS = """\
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
"""

# NOTE on accent handling: CSV_final.csv stores "Exaltacion" (no accent, this
# is what appears after NFC normalisation of the actual cell value) for Beni
# municipalities. Verified by extract_rates.py - all 21 municipalities found.
# The RAMP_MUNICIPALITY env var uses the same unaccented convention.


def make_illumination(func_time_indoor, window_end_indoor):
    return (
        "from ramp.core.core import User\n\n"
        "User_list = []\n\n"
        'HI = User("household illumination", 1)\n'
        "User_list.append(HI)\n\n"
        "# occasional_use=1.0: illumination is universal for electrified households\n"
        f"HI_indoor_bulb = HI.add_appliance(4, 7, 2, {func_time_indoor}, 0.2, 10, occasional_use=1.0)\n"
        f"HI_indoor_bulb.windows([300, 480], [{window_end_indoor}, 1440], 0.35)\n\n"
        "HI_outdoor_bulb = HI.add_appliance(2, 14, 1, 180, 0.2, 10, occasional_use=1.0)\n"
        "HI_outdoor_bulb.windows([1140, 1380], [0, 0], 0.35)\n"
    )


def make_ict(tv_factor, laptop_factor):
    return (
        "from ramp.core.core import User\n"
        + MUNI_HELPERS + "\n"
        f"TV_FACTOR = {tv_factor}  # MTF Tier 2: solar home system includes TV\n"
        f"LAPTOP_FACTOR = {laptop_factor}  # MTF blended solar/generator retention (53/47)\n\n"
        'municipality = os.environ.get("RAMP_MUNICIPALITY", "")\n\n'
        "def _load_ict_rates(muni):\n"
        "    row = _find_row(muni)\n"
        "    if row is None:\n"
        '        return {"radio": 0.1, "tv": 0.1, "laptop": 0.3, "phone": 0.2}\n'
        "    # Column indices in CSV_final.csv (0-based, 2024, Sin especificar excluded)\n"
        "    # 107=Radio Tiene, 108=Radio NoTiene\n"
        "    # 110=TV Tiene,    111=TV NoTiene\n"
        "    # 113=Laptop Tiene,114=Laptop NoTiene\n"
        "    # 116=Phone Tiene, 117=Phone NoTiene\n"
        "    return {\n"
        '        "radio":  _rate(row[107], row[108]),\n'
        '        "tv":     _rate(row[110], row[111]),\n'
        '        "laptop": _rate(row[113], row[114]),\n'
        '        "phone":  _rate(row[116], row[117]),\n'
        "    }\n\n"
        "_rates = _load_ict_rates(municipality)\n\n"
        "User_list = []\n"
        'HICT = User("household ICT", 1)\n'
        "User_list.append(HICT)\n\n"
        "# TV: census ownership rate x MTF Tier 2 factor (SHS explicitly includes TV)\n"
        'HICT_TV = HICT.add_appliance(1, 30, 2, 120, 0.1, 5, occasional_use=_rates["tv"] * TV_FACTOR)\n'
        "HICT_TV.windows([1080, 1440], [0, 60], 0.35)\n\n"
        "# Radio: census ownership rate, no reduction (low-power, small-solar compatible)\n"
        'HICT_Radio = HICT.add_appliance(1, 3, 2, 120, 0.1, 5, occasional_use=_rates["radio"])\n'
        "HICT_Radio.windows([390, 450], [1082, 1260], 0.35)\n\n"
        "# Phone charger: census ownership rate, no reduction\n"
        'HICT_Phone_charger = HICT.add_appliance(4, 5, 2, 120, 0.2, 10, occasional_use=_rates["phone"])\n'
        "HICT_Phone_charger.windows([1020, 1440], [0, 300], 0.35)\n\n"
        "# Laptop: census ownership rate x MTF blended solar/generator factor\n"
        'HICT_Laptop = HICT.add_appliance(1, 70, 1, 90, 0.3, 30, occasional_use=_rates["laptop"] * LAPTOP_FACTOR)\n'
        "HICT_Laptop.windows([960, 1200], [0, 0], 0.35)\n"
    )


def make_cold_storage(fridge_factor):
    return (
        "from ramp.core.core import User\n"
        + MUNI_HELPERS + "\n"
        f"FRIDGE_FACTOR = {fridge_factor}  # MTF Tier 3 load; solar-only (Tier 2) can't run it\n\n"
        'municipality = os.environ.get("RAMP_MUNICIPALITY", "")\n\n'
        "def _load_fridge_rate(muni):\n"
        "    row = _find_row(muni)\n"
        "    if row is None:\n"
        "        return 0.0\n"
        "    # Col 73=Refrigerador Tiene, 74=No tiene (2024, Sin especificar excluded)\n"
        "    return _rate(row[73], row[74])\n\n"
        "_fridge_rate = _load_fridge_rate(municipality)\n\n"
        "User_list = []\n"
        'HCS = User("household cold storage", 1)\n'
        "User_list.append(HCS)\n\n"
        "# Fridge/freezer: census ownership rate x MTF blended factor (generator share only)\n"
        'HCS_Freezer = HCS.add_appliance(1, 200, 1, 1440, 0, 30, "yes", 3,\n'
        "                                occasional_use=_fridge_rate * FRIDGE_FACTOR)\n"
        "HCS_Freezer.windows([0, 1440], [0, 0])\n"
        "HCS_Freezer.specific_cycle_1(200, 20, 5, 10)  # intensivo\n"
        "HCS_Freezer.specific_cycle_2(200, 15, 5, 15)  # intermedio\n"
        "HCS_Freezer.specific_cycle_3(200, 10, 5, 20)  # standard\n"
        "HCS_Freezer.cycle_behaviour([480, 1200], [0, 0], [300, 479], [0, 0], [0, 299], [1201, 1440])\n"
    )


def make_thermal(fan_factor):
    return (
        "from ramp.core.core import User\n"
        "import pandas as pd\n"
        + MUNI_HELPERS + "\n"
        f"FAN_FACTOR = {fan_factor}  # MTF Tier 2: fan grouped with TV\n\n"
        "municipality = os.environ.get('RAMP_MUNICIPALITY', '')\n"
        "season = os.environ.get('RAMP_SEASON')\n\n"
        "# No dedicated census fan question; MTF groups the fan with TV at Tier 2,\n"
        "# so retention is indexed on TV ownership (cols 110/111). Fallback 0.1 only\n"
        "# applies when the municipality has no census row.\n"
        "_census_row = _find_row(municipality) if municipality else None\n"
        "tv_rate = _rate(_census_row[110], _census_row[111]) if _census_row is not None else 0.1\n\n"
        "if municipality and season:\n"
        "    current_dir = os.path.dirname(os.path.abspath(__file__))\n"
        "    project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..', '..'))\n"
        "    csv_path = os.path.join(project_root, 'data', 'thermal_comfort_lookup.csv')\n"
        "    df = pd.read_csv(csv_path)\n"
        "    row = df[(df['municipality'] == municipality) & (df['season'] == season)]\n"
        "    if not row.empty:\n"
        "        func_time = int(row['func_time'].iloc[0])\n"
        "    else:\n"
        "        print(f'Warning: No thermal comfort data for {municipality} {season}, using default 420')\n"
        "        func_time = 420\n"
        "else:\n"
        "    func_time = 420\n\n"
        "User_list = []\n"
        "HSC = User('household space cooling', 1)\n"
        "User_list.append(HSC)\n\n"
        "# Fan: no census fan ownership rate; indexed on TV ownership x MTF Tier 2 factor\n"
        "HSC_Fan = HSC.add_appliance(1, 30, 2, func_time, 0.27, 30, occasional_use=tv_rate * FAN_FACTOR)\n"
        "HSC_Fan.windows([480, 1260], [0, 0], 0.35)\n"
    )


def add_genset_comment(content):
    comment = "# off-grid, likely diesel-genset powered -- relevant for diesel accounting at the Demands/supply stage, not here.\n"
    if "off-grid, likely diesel-genset" in content:
        return content
    lines = content.splitlines(keepends=True)
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import ") or line.startswith("User_list"):
            insert_at = i
            break
    lines.insert(insert_at, comment)
    return "".join(lines)


ILLUMINATION_PARAMS = {
    "fall":   (360, 960),
    "spring": (360, 960),
    "summer": (270, 950),
    "winter": (400, 960),
}

# ── build ─────────────────────────────────────────────────────────────────────

changes = []

def log(msg):
    print(msg)
    changes.append(msg)


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


if os.path.exists(DST):
    shutil.rmtree(DST)
    log("REMOVED existing Norte_Amazonia_reality")

shutil.copytree(SRC, DST)
log("COPIED Norte_Amazonia to Norte_Amazonia_reality")

for dirpath, dirnames, filenames in os.walk(DST, topdown=False):
    if "__pycache__" in os.path.basename(dirpath):
        shutil.rmtree(dirpath)
        log(f"DELETED __pycache__: {os.path.relpath(dirpath, DST)}")

for season in SEASONS:
    hh_dir = os.path.join(DST, season, "households", "sufficiency")

    wh = os.path.join(hh_dir, "water_heating.py")
    if os.path.exists(wh):
        os.remove(wh)
        log(f"DELETED {season}/households/sufficiency/water_heating.py")

    ft, we = ILLUMINATION_PARAMS[season]
    write_file(os.path.join(hh_dir, "illumination.py"), make_illumination(ft, we))
    log(f"WRITTEN {season}/households/sufficiency/illumination.py  [occasional_use=1.0 keyword]")

    write_file(os.path.join(hh_dir, "ICT.py"), make_ict(MTF_FACTOR["tv"], MTF_FACTOR["laptop"]))
    log(f"WRITTEN {season}/households/sufficiency/ICT.py  [TV x{MTF_FACTOR['tv']}, Laptop x{MTF_FACTOR['laptop']}, Radio/Phone no reduction]")

    write_file(os.path.join(hh_dir, "cold_storage.py"), make_cold_storage(MTF_FACTOR["fridge"]))
    log(f"WRITTEN {season}/households/sufficiency/cold_storage.py  [fridge rate x{MTF_FACTOR['fridge']}]")

    write_file(os.path.join(hh_dir, "thermal_comfort.py"), make_thermal(MTF_FACTOR["fan"]))
    log(f"WRITTEN {season}/households/sufficiency/thermal_comfort.py  [fan = census TV rate x{MTF_FACTOR['fan']}]")

    for rel in [
        os.path.join(season, "income_generating_activity", "workshop", "machinery.py"),
        os.path.join(season, "income_generating_activity", "rice_processing", "rice_processing.py"),
    ]:
        abs_path = os.path.join(DST, rel)
        if os.path.exists(abs_path):
            with open(abs_path, encoding="utf-8") as f:
                original = f.read()
            updated = add_genset_comment(original)
            if updated != original:
                with open(abs_path, "w", encoding="utf-8") as f:
                    f.write(updated)
                log(f"UPDATED {rel}  [diesel-genset comment]")

print("\n" + "=" * 60)
print(f"Done. Total changes: {len(changes)}")
