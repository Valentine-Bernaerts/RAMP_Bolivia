from ramp.core.core import User
import pandas as pd
import os

municipality = os.environ.get('RAMP_MUNICIPALITY')

User_list = []

HCWH = User("Health Center Water Heating", 1)  # Create user with ID = 1
User_list.append(HCWH)

current_dir = os.path.dirname(__file__)  # /inputs/highlands/fall/households/sufficiency
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "..", ".."))  # RAMP_Bolivia
csv_path = os.path.join(project_root, "data", "water_heating_power_all_municipalities.csv")
power_profiles = pd.read_csv(csv_path)
power_profiles = power_profiles.drop(columns=['day'], errors='ignore').apply(pd.to_numeric, errors='coerce')
power_profiles = power_profiles.dropna().reset_index(drop=True)
municipality_columns = list(power_profiles.columns)

if municipality in power_profiles.columns:
	HCWH_shower_P = power_profiles[[municipality]]
else:
	print(f"Warning: Municipality '{municipality}' not found in water heating power profiles, using mean profile")
	HCWH_shower_P = power_profiles[municipality_columns].mean(axis=1).to_frame(name='mean_power')


WH_shower = HCWH.add_appliance(1,HCWH_shower_P,2,15,0.1,3, thermal_p_var = 0.2, occasional_use=0.33)
WH_shower.windows([360,540],[1080,1260],0.2)




