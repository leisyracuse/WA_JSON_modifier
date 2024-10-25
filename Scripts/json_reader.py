"""
Copyright (c) 2024 Zhenlei Liu ORNL 
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation.
"""
import json
import os
import csv
from tqdm import tqdm
from typing import Dict, Optional

# def read_json(file_path: str, required_fields: List[str]) -> Optional[Dict]:
def read_json(file_path: str, config: dict) -> Optional[Dict]:
    """
    Read and extract specific fields from a JSON file.
    
    Args:
        file_path (str): Path to the JSON file
        config (dict): config dict to map JSON items with CSV header
        
    Returns:
        Optional[Dict]: Dictionary containing extracted data or None if error occurs
    """
    output = {}

    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            
            if data is None:
                return None
                
            for section, fields in config.items():
                if section in data:
                    section_data = data[section]

                    # Extract audit-related fields
                    if section == 'audit':
                        output.update({
                            header: section_data.get(item, 'N/A') for header, item in zip(fields['csv_headers'], fields['required_items'])
                        })
                    
                    # Extract fuel-related fields
                    elif section == 'fuel_costs':
                        output.update({
                            fields['csv_headers'][0]: len(section_data) / 2
                        })
                    
                    # Extract foundation-related fields
                    elif section == 'foundations':
                        print(section)
                        print(section_data)
                        output.update({
                            fields['csv_headers'][0]: len(section_data),
                            fields['csv_headers'][1]: section_data[0].get(fields['required_items'][0]) if len(section_data)==1 else None
                        })
            return output
            
    except Exception as err:
        print(f'Error reading {file_path}: {err}')
        return None

def process_json_to_csv(
    input_dir: str,
    output_file: str,
    config = dict,
    mode: str = 'a'
) -> None:
    """
    Process multiple JSON files and save their data to a CSV file.
    
    Args:
        input_dir (str): Directory containing JSON files
        output_file (str): Path to the output CSV file
        config (dict): config dict to map JSON items with CSV header
        mode (str): File opening mode ('w' for write, 'a' for append)
    """

    headers = [header for section in config.values() for header in section['csv_headers']]

    with open(output_file, mode=mode, newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        
        # Write header only if in write mode
        if mode == 'w':
            writer.writeheader()
            
        # Process each JSON file in the directory
        for filename in tqdm(os.listdir(input_dir)):
            if filename.endswith('.json'):
                file_path = os.path.join(input_dir, filename)
                data = read_json(file_path, config)
                
                if data is not None and data != {}:
                    print(f"Processing: {filename}")
                    writer.writerow(data)

def main():
    # Configuration
    json_dir = './JSON_files/'
    csv_file = './audit_data.csv'

    config = {
        "audit": {
            "csv_headers": [
                "Audit Number", 
                "Occupants", 
                "Conditioned Stories", 
                "Number of Bedrooms", 
                "Floor Area"
            ],
            "required_items": [
                "audit_number", 
                "avg_no_occupants", 
                "no_cond_stories", 
                "num_bedrooms", 
                "floor_area"
            ]
        },
        "fuel_costs": {
            "csv_headers": ["Number of fuels"],
            "required_items": []  
        },
        "foundations": {
            "csv_headers": ["Number of foundation types", "Foundation types"],
            "required_items": ["space_type"]  
        }
    }

    
    # Process the files
    process_json_to_csv(
        input_dir=json_dir,
        output_file=csv_file,
        config=config,
        mode='w'  # 'w' for write mode (overwrites existing file)
    )

if __name__ == "__main__":
    main()
