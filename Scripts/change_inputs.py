"""
Copyright (c) 2024 Zhenlei Liu ORNL 
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation.
"""
import json
import os
import copy

def read_json(fn):
    try:
        with open(fn, 'r') as json_file:
            data = json.load(json_file)
            return data
    except Exception as err:
        print(f'Error reading {fn}: {err}')


def save_file(data, json_dir, sir_flag, sc_flag):
    """
    Save modified JSON data to specified directory based on SIR and SC flags.
    
    Args:
        data (dict): JSON data to be saved.
        json_dir (str): Directory path for saving JSON files.
        sir_flag (bool): If True, minimum SIR is set to 0.
        sc_flag (bool): If True, applies specific fuel cost adjustments for SC-GHG.
    """
    # Create a deep copy of data to avoid modifying the original
    data = copy.deepcopy(data)
    
    # Define fuel cost modifiers for SC adjustments
    fuel_modifiers = {
        'electric': 0.1055,
        'natural_gas': 1.414 * 10.36,
        'propane': 1.506,
        'oil': 2.709
    }
    
    # Determine file suffix and modifications based on flags
    if not sir_flag and not sc_flag:
        file_suffix = "SIR1"
    elif sir_flag and sc_flag:
        file_suffix = "SIR0_SC"
    elif sir_flag:
        file_suffix = "SIR0"
    else:  # sc_flag only
        file_suffix = "SIR1_SC"
    
    # Apply SIR modification if sir_flag is True
    if sir_flag and data['key_parameters'].get('minimum_acceptable_sir') == 1:
        data['key_parameters']['minimum_acceptable_sir'] = 0
    
    # Apply fuel cost modifications if sc_flag is True
    if sc_flag:
        for fuel_type, modifier in fuel_modifiers.items():
            if fuel_type in data['fuel_costs']:
                data['fuel_costs'][fuel_type] += modifier
    
    # Construct file path and save the modified data to JSON
    audit_number = data['audit']['audit_number']
    file_path = os.path.join(json_dir, 'Outputs', f'Audit_{audit_number}_{file_suffix}.json')
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


       
if __name__ == "__main__":
    json_dir = './JSON_files/'
    for fn in os.listdir(json_dir):
        if fn.endswith('.json'):
            json_path = os.path.join(json_dir,fn)
            raw_data = read_json(json_path)
            save_file(raw_data, json_dir, sir_flag=False, sc_flag=False)
            save_file(raw_data, json_dir, sir_flag=True, sc_flag=False)
            save_file(raw_data, json_dir, sir_flag=False, sc_flag=True)
            save_file(raw_data, json_dir, sir_flag=True, sc_flag=True)