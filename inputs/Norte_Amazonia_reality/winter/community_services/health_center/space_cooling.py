from ramp.core.core import User
import pandas as pd
import os

municipality = os.environ.get('RAMP_MUNICIPALITY')
season = os.environ.get('RAMP_SEASON')

if municipality and season:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "..", ".."))
    csv_path = os.path.join(project_root, "data", "thermal_comfort_lookup.csv")
    df = pd.read_csv(csv_path)
    row = df[(df['municipality'] == municipality) & (df['season'] == season)]
    if not row.empty:
        func_time = int(row['func_time'].iloc[0])
    else:
        print(f"Warning: No thermal comfort data for {municipality} {season}, using default 420")
        func_time = 420
else:
    func_time = 420

func_time_ac = func_time // 3

User_list = []

SC = User("Space Cooling", 1)
User_list.append(SC)

SC_Fan = SC.add_appliance(4, 30, 2, func_time, 0.27, 30)
SC_Fan.windows([480, 1260], [0, 0], 0.35)

SC_AC = SC.add_appliance(2, 1000, 2, func_time_ac, 0.2, 15)
SC_AC.windows([720, 900], [1020, 1260], 0.35)
