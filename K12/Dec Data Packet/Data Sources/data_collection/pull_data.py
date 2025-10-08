import os, sys, json, datetime, re  # Provides OS-dependent functionality, system-specific parameters, JSON handling, and date/time manipulation
import pandas as pd             # Provides data structures and data analysis tools
import numpy as np              # Supports large, multi-dimensional arrays and matrices
import requests
import time
from tqdm import tqdm
import glob as glob

#thi data contants
from cprl_functions.defined_functions import *
from cprl_functions.state_capture import *
from cprl_functions.text_printing import bordered
from cprl_functions.data_packet_defs import *

from pathlib import Path


data_directory = Path(r'C:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data Packets\k12\data')

def get_data_files():
    file_dict = {}
    for file in data_directory.iterdir():
        # print(file.name)
        if 'naep' in file.name.lower():
            naep_file = data_directory / file.name
            file_dict['naep'] = naep_file
        elif 'data_collection' in file.name.lower():
            data_collection_file = data_directory / file.name
            file_dict['data_collection'] = data_collection_file

    return file_dict


def merge_split_state_names(df):
    df = df.copy()
    i = 0
    
    while i < len(df):
        # Check if this row has a state name but no numeric data
        if not pd.isna(df.iloc[i, 0]) and pd.isna(df.iloc[i, 1]):
            state_parts = [df.iloc[i, 0]]
            j = i + 1
            
            # Collect all parts of the state name
            while j < len(df) and not pd.isna(df.iloc[j, 0]) and pd.isna(df.iloc[j, 1]):
                state_parts.append(df.iloc[j, 0])
                j += 1
            
            # Find the row with numeric data
            if j < len(df) and pd.isna(df.iloc[j, 0]):
                # Combine state name
                full_state_name = ' '.join(state_parts)
                
                # Assign combined name and numeric data
                df.iloc[i, 0] = full_state_name
                df.iloc[i, 1:] = df.iloc[j, 1:].values
                
                # Drop the intermediate rows
                df = df.drop(df.index[i+1:j+1]).reset_index(drop=True)
        
        i += 1
    
    return df


def get_act_data():
    import tabula
    act_pdf = r"C:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data Packets\k12\data\2024-Average-ACT-Scores-by-State-Percent-Meeting-Benchmarks.pdf"

    # Loop through pages with different settings
    page_configs = {
        1: {'area': [300, 20, 750, 888], 'columns': [130,150, 280, 350, 450,525, 770]},
        2: {'area': [125, 20, 600, 888], 'columns': [130,150, 280, 350, 450,525, 770]},
    }

    #pull all the info and put into a list
    results = []
    for page, config in page_configs.items():
        # print(page)

        #read in with tabula
        df = tabula.read_pdf(
            act_pdf,
            pages=page,
            area=config['area'],
            columns=config.get('columns'),
            multiple_tables=False,
            pandas_options={'header': None}
        )


        if page==2:
            result = merge_split_state_names(df[0])
        else:
            result = df[0]
        
        results.append(result)

    # Combine both pages if needed
    columns = [
            'state',
            'est_percent_grads_tested',
            'avg_composite_score',
            'eng_benchmark_percent',
            'math_benchmark_percent',
            'reading_benchmark_percent',
            'sci_benchmark_percent'
        ]

    df_combined = pd.concat(results, ignore_index=True)
    df_combined.columns = columns
    output = df_combined.sort_values(by='state')
    return output


if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
    print('Ran in file')
    # print('nothing')



        



# with open(data_directory / naep_file, 'r') as file:
#     excel_file = pd.ExcelFile(file,engine='calamine')
#     for sheet in excel_file.sheet_names:
#         if '- 2024' in sheet:
#             print(sheet) 

# excel_file = pd.ExcelFile(data_directory / data_collection_file, engine='calamine')
# for sheet in excel_file.sheet_names:
#     print(sheet)
#     if 'merge' in sheet.lower():
#         merge_tags = excel_file.parse(sheet_name=sheet)
#         break

# print(merge_tags.to_string())
if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
   print('nothing')


# glob_pat = os.path.join(filepath, 'NAEP*.xlsx')
# files = glob.glob(glob_pat)
# print(merge_tags)
# for file in filepath:
# pd.ExcelFile()