# -*- coding: utf-8 -*-
"""
Per-Municipality RAMP Runner for Norte Amazónica
Runs RAMP simulations separately for each municipality using infrastructure counts from CSV.
"""
import yaml
import os
import importlib.util
from ramp import UseCase
import pandas as pd
from pathlib import Path
from collections import defaultdict
import time
import argparse

COLUMN_TO_SECTOR = {
    'non_elec_hh':            ('households', 'sufficiency'),
    'school':                 ('community_services', 'big_school'),
    'health_center':          ('community_services', 'health_center'),
    'public_lighting':        ('community_services', 'public_lighting'),
    'store':                  ('income_generating_activity', 'store'),
    'restaurant':             ('income_generating_activity', 'restaurant'),
    'workshop':               ('income_generating_activity', 'workshop'),
    'entertainment_business': ('income_generating_activity', 'entertainment_business'),
    'flour_processing':       ('income_generating_activity', 'flour_processing'),
}

def load_user_input(filepath):
    try:
        spec = importlib.util.spec_from_file_location("user_module", filepath)
        user_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_module)

        if hasattr(user_module, "User_list"):
            return user_module.User_list
        else:
            raise AttributeError(f"{filepath} does not contain a 'User_list'.")
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []

def get_simulation_dates(config, season=None):
    sim_settings = config['simulation_settings']
    mode = sim_settings.get('simulation_mode', 'seasonal')

    if mode == 'date_range': 
        date_start = pd.to_datetime(sim_settings['date_start'])
        date_end = pd.to_datetime(sim_settings['date_end'])
        days = (date_end - date_start).days + 1

    elif mode in ['seasonal', 'full_year']:
        if season is None:
            raise ValueError("Season must be provided in 'seasonal' or 'full_year' mode.")
        season_dates = sim_settings.get('season_dates', {})
        if season not in season_dates:
            raise ValueError(f"Start/end date for season '{season}' not defined in season_dates.")
        date_start = pd.to_datetime(season_dates[season]['start'])
        date_end = pd.to_datetime(season_dates[season]['end'])
        days = (date_end - date_start).days + 1

    else:
        raise ValueError(f"Unknown simulation mode: {mode}")

    return date_start, date_end, days

def collect_users(config, base_input_dir, season, counts=None):
    users_by_level = defaultdict(list)
    sim_settings = config['simulation_settings']

    region = sim_settings['regions'][0]  # Norte_Amazonia

    for sector, user_types in sim_settings['sectors'].items():
        for user_type, settings in user_types.items():
            count = counts.get((sector, user_type), settings.get('count', 1)) if counts else settings.get('count', 1)
            services = settings.get('energy_service', [])
            if count < 1 or not services:
                continue

            for service in services:
                path = os.path.join(base_input_dir, region, season, sector, user_type, f"{service}.py")
                if os.path.isfile(path):
                    User_list = load_user_input(path)
                    for user in User_list:
                        user.num_users = count
                        if 'energy_service' in sim_settings['simulation_levels']:
                            users_by_level[f"energy_service_{user_type}_{service}"].append(user)
                        if 'sector' in sim_settings['simulation_levels']:
                            users_by_level[f"sector_{sector}"].append(user)
                        if 'user_type' in sim_settings['simulation_levels']:
                            users_by_level[f"user_type_{user_type}"].append(user)
                        if 'community' in sim_settings['simulation_levels']:
                            users_by_level[f"community_{region}_{season}"].append(user)
                else:
                    print(f"Warning: File not found: {path}")

    return users_by_level

def run_simulations(config, base_input_dir, output_dir, counts=None):
    os.makedirs(output_dir, exist_ok=True)
    sim_settings = config['simulation_settings']
    simulation_mode = sim_settings.get('simulation_mode', 'seasonal')
    is_full_year = simulation_mode == 'full_year'

    region = sim_settings['regions'][0]

    for level in sim_settings['simulation_levels']:
        if is_full_year and level == 'energy_service':
            seasonal_outputs = defaultdict(list)

            for season in sim_settings['seasons']:
                date_start, date_end, _ = get_simulation_dates(config, season)
                users_by_level = collect_users(config, base_input_dir, season, counts)
                matching_keys = [k for k in users_by_level if k.startswith(level)]

                for key in matching_keys:
                    users = users_by_level[key]
                    use_case = UseCase(users=users, date_start=date_start, date_end=date_end)
                    result = use_case.generate_daily_load_profiles()
                    df = pd.DataFrame(result)
                    df.index.name = 'time'

                    label = key.replace('energy_service_', '')
                    if isinstance(df, pd.DataFrame) and df.shape[1] == 1:
                        df.columns = [label]
                    else:
                        df = df.sum(axis=1).to_frame(label)

                    seasonal_outputs[label].append(df)

            # Concatenate full year per service
            combined_full_year = []
            for label, seasonal_parts in seasonal_outputs.items():
                full_df = pd.concat(seasonal_parts, axis=0)
            
                # Set index to be continuous and name it 'time'
                full_df.index = range(len(full_df))
                full_df.index.name = 'time'
            
                combined_full_year.append(full_df)
            
            final_df = pd.concat(combined_full_year, axis=1)
            output_path = os.path.join(output_dir, f"load_curve_{level}_full_year_{region}.csv")
            final_df.to_csv(output_path)
            print(f"✅ Saved: {output_path}")

        else:
            for season in sim_settings['seasons']:
                date_start, date_end, _ = get_simulation_dates(config, season)
                users_by_level = collect_users(config, base_input_dir, season, counts)
                matching_keys = [k for k in users_by_level if k.startswith(level)]

                season_dfs = []
                for key in matching_keys:
                    users = users_by_level[key]
                    use_case = UseCase(users=users, date_start=date_start, date_end=date_end)
                    result = use_case.generate_daily_load_profiles()
                    df = pd.DataFrame(result)
                    df.index.name = 'time'

                    if level == 'energy_service':
                        label = key.replace('energy_service_', '')
                    elif level == 'sector':
                        label = key.replace('sector_', '')
                    elif level == 'user_type':
                        label = key.replace('user_type_', '')
                    elif level == 'community':
                        label = 'community'
                    else:
                        label = key

                    if isinstance(df, pd.DataFrame) and df.shape[1] == 1:
                        df.columns = [label]
                    else:
                        df = df.sum(axis=1).to_frame(label)

                    season_dfs.append(df)

                if season_dfs:
                    season_combined_df = pd.concat(season_dfs, axis=1)
                    suffix = f"{level}_{season}_{region}"
                    output_path = os.path.join(output_dir, f"load_curve_{suffix}.csv")
                    season_combined_df.to_csv(output_path)
                    print(f"✅ Saved: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Run RAMP simulations per municipality')
    parser.add_argument('--test', nargs='*', help='List of municipalities to test (optional)')
    args = parser.parse_args()

    # Load base config
    with open("config_norte_amazonia.yml", "r") as f:
        config = yaml.safe_load(f)

    # Read municipalities data
    df = pd.read_csv('municipalities_counts.csv')
    
    # Skip TOTAL row
    df = df[df['municipality'] != 'TOTAL']
    
    # Filter for test municipalities if provided
    if args.test:
        df = df[df['municipality'].isin(args.test)]
    
    total_munis = len(df)
    base_input_dir = "inputs"
    
    start_time = time.time()
    
    for idx, row in df.iterrows():
        municipality = row['municipality']
        hh_count = int(row['non_elec_hh'])
        print(f"Running {idx+1}/{total_munis}: {municipality} ({hh_count} HH)...")
        
        # Build counts dict from CSV
        counts = {}
        for col, (sector, user_type) in COLUMN_TO_SECTOR.items():
            counts[(sector, user_type)] = int(row[col])
        
        # Set output directory for this municipality
        output_dir = f"output_norte_amazonia/{municipality}"
        
        try:
            run_simulations(config, base_input_dir, output_dir, counts)
        except Exception as e:
            print(f"❌ Error in {municipality}: {e}")
            continue
    
    end_time = time.time()
    print(f"\n✅ Total execution time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    main()