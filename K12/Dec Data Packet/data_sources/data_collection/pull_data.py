
# %%
import os, sys, json, datetime, re  # Provides OS-dependent functionality, system-specific parameters, JSON handling, and date/time manipulation
import pandas as pd             # Provides data structures and data analysis tools
import numpy as np              # Supports large, multi-dimensional arrays and matrices
import requests
import time
from tqdm import tqdm
import glob as glob
import chardet
#thi data contants
from cprl_functions.defined_functions import *
from cprl_functions.state_capture import *
from cprl_functions.text_printing import bordered
from cprl_functions.data_packet_defs import *

from pathlib import Path



# %% Helper functions

def get_intitials(x):
    try:
        result = state_ref.get(x.strip())
    except:
        print(f'trouble child: {x}')
        return None
    if result is None:
        if 'national' in str(x).lower():
            return "US"
    else:
        return result
#set_up
data_directory = Path(r'C:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data\Data Packets\K-12\data')


# %% 
# ####################
"""
Common core of data
"""
def get_ccd_file(type):
    
    if type == 'enrollment':
        
        file = r"C:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data\Data Packets\K-12\data\nces\CCD\enrollment_query_tool_result.csv"
    elif type == 'counts':
        file = r'c:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data\Data Packets\K-12\data\nces\CCD\ccd_table_2_2324.xlsx'

    return file

def get_state_abv(x):
    if 'district of columbia' in str(x).lower():
        return "DC"
    
    results = state_ref.get(x)
    return results

def enrollment_data_cleaned(**kwargs):
    debug = kwargs.get('debug', False)
    #get file and make df
    ccd_file = get_ccd_file('enrollment')
    ccd_df = pd.read_csv(ccd_file)

    if debug==True:
        print(ccd_df.head().to_string())

    #clean

    #cut off footer
    for i,j in enumerate(ccd_df['State Name']):
        if 'Data Source' in str(j):
            if debug==True:
                print(str(j))
            break_i = i 
            break
    ccd_df = ccd_df.iloc[:i,:].reset_index(drop=True)
    ccd_df = ccd_df.dropna(axis=0, how='all')

    # ccd_df.columns = ccd_df.iloc[0,:]
    # ccd_df = ccd_df.iloc[1:,:].reset_index(drop=True)
    # ccd_df.columns = [str(x).lower().strip().replace('\n','').replace(' ','_') for x in ccd_df.columns]


    # Define the columns we want to keep for each year
    years = ['2023-24', '2022-23', '2021-22', '2020-21', '2019-20', '2018-19', '2017-18']


    # Create list to store transformed data
    transformed_data = []

    for year in years:
        year_data = pd.DataFrame()
        year_data['state'] = ccd_df['State Name'].str.title()
        year_data['year'] = year
        year_data['total_enrollment'] = ccd_df[f'Total Enrollment (Exclude AE) for SY 2014-15 onward [State] {year}']
        year_data['american_indian_alaska_native'] = ccd_df[f'American Indian/Alaska Native Students [State] {year}']
        year_data['asian_pacific_islander'] = ccd_df[f'Asian or Asian/Pacific Islander Students [State] {year}']
        year_data['hispanic'] = ccd_df[f'Hispanic Students [State] {year}']
        year_data['black'] = ccd_df[f'Black or African American Students [State] {year}']
        year_data['white'] = ccd_df[f'White Students [State] {year}']
        year_data['nat_hawaiian_pacific_islander'] = ccd_df[f'Nat. Hawaiian or Other Pacific Isl. Students [State] {year}']
        year_data['two_or_more'] = ccd_df[f'Two or More Races Students [State] {year}']
        
        transformed_data.append(year_data)

    # Combine all years
    ccd_results = pd.concat(transformed_data, ignore_index=True)

    if debug==True:
        print(ccd_results)

    # Sort by state and year
    ccd_results = ccd_results.sort_values(['state', 'year']).reset_index(drop=True)
    ccd_results['state_abrv'] = ccd_results['state'].apply(lambda x: get_state_abv(x))
    abv_popped = ccd_results.pop('state_abrv')
    ccd_results.insert(0,'state_abrv',abv_popped)
    ccd_results = ccd_results.dropna(axis=1, how='all')
    ccd_results = ccd_results.reset_index(drop=True)
    # ccd_results.loc['Column_Total']= df.sum(numeric_only=True, axis=0)
    #Add us

    # import pandas as pd

    # List of columns that should be numeric
    numeric_cols = ['total_enrollment', 'american_indian_alaska_native', 
                    'asian_pacific_islander', 'hispanic', 'black', 'white', 
                    'nat_hawaiian_pacific_islander', 'two_or_more']

    # Convert columns to numeric, coercing errors to NaN
    for col in numeric_cols:
        ccd_results[col] = pd.to_numeric(ccd_results[col], errors='coerce')

    # Group by year and sum all numeric columns automatically
    us_rows = ccd_results.groupby('year', as_index=False).sum(numeric_only=True)

    # Add non-numeric columns
    us_rows.insert(0, 'state_abrv', 'US')
    us_rows.insert(1, 'state', 'United States')

    # Append to original dataframe
    ccd_results = pd.concat([ccd_results, us_rows], ignore_index=True)
    ccd_results['fy'] = ccd_results['year'].str.split('-').str[-1].str.strip().apply(pd.to_numeric, errors='coerce')
    fy_pop = ccd_results.pop('fy')
    ccd_results.insert(2,'fy', fy_pop)


    return ccd_results
def int_or_none(x):
    try:
        return int(x)
    except:
        return 0
def ccd_counts_cleaned(**kwargs):
    debug = kwargs.get('debug', False)
    #get file and make df
    ccd_file = get_ccd_file('counts')
    print(ccd_file)
    ccd_df = pd.read_excel(ccd_file, engine='openpyxl')
    
    ccd_df = ccd_df.iloc[1:63,:].reset_index(drop=True)
    ccd_df = ccd_df.dropna(axis=1, how='all')
    
    ccd_columns = ['state', 'num_schools', 'num_districts', 'students','teachers', 'student_teacher_ratio']
    ccd_df.columns = ccd_columns
    # ccd_df = ccd_df.iloc[1:,:].reset_index(drop=True)
    if debug==True:
        print(ccd_df.head().to_string())


    ccd_df = ccd_df.dropna(axis=0, how='all')

    ccd_df.columns = [str(x).lower().strip().replace('\n','').replace(' ','_') for x in ccd_df.columns]
    ccd_df['state'] = ccd_df['state'].apply(lambda x: re.sub(r'\d$', "", str(x)))
    ccd_df['state_abrv'] = ccd_df['state'].apply(lambda x: state_ref.get(x))
    popped_state_initials = ccd_df.pop('state_abrv')
    ccd_df.insert(0,'state_abrv', popped_state_initials)

    if debug==True:
        print(ccd_df.to_string())

    return ccd_df    

def total_enroll_data_clean():
    # for total enrollment
    ccd_results = enrollment_data_cleaned()
    ccd_results_total = ccd_results.loc[:,'state_abrv':'total_enrollment']
    ccd_results_total = ccd_results_total.drop(columns=['state'])

    #merging collected and current records

    #get collected data from data collection sheet
    collected_enrollment = get_collected_data(metric = 'total_enroll_k12')
    collected_enrollment.columns = collected_enrollment.iloc[0,:]
    collected_enrollment = collected_enrollment.iloc[1:,:]
    collected_enrollment = collected_enrollment.loc[:,['state','updated data year', 'updated data']]
    collected_enrollment.columns = ['state_abrv','year','total_enrollment']
    collected_enrollment['year'] = collected_enrollment['year'].str.replace(r'(\d{4})-(\d{4})', lambda m: f"{m.group(1)}-{m.group(2)[-2:]}", regex=True)
    collected_enrollment['fy'] = (pd.to_numeric(collected_enrollment['year'].str[-2:], errors='coerce')).astype('Int64')
    # print(collected_enrollment.to_string())
    #Identify rows NOT already in current_records
    existing_pairs = set(zip(ccd_results_total['state_abrv'], ccd_results_total['fy']))
    updated_data_filtered = collected_enrollment[~collected_enrollment.apply(lambda row: (row['state_abrv'], row['fy']) in existing_pairs, axis=1)]

    #Add missing columns to updated_data so it matches current_records
    # updated_data_filtered['fy'] = updated_data_filtered['year'].str[:4].astype(int) - 2000  # e.g. 2023-24 → fy = 23
    updated_data_filtered = updated_data_filtered[ccd_results_total.columns]  # Reorder columns to match
    # print(updated_data_filtered.to_string())
    # print(ccd_results_total.to_string())

    #Merge (append)
    merged_df = pd.concat([ccd_results_total, updated_data_filtered], ignore_index=True)
    enrollment_merged_df = merged_df.sort_values(by=['state_abrv','year'])
    # print(enrollment_merged_df.to_string())
    return enrollment_merged_df
    # collected_df = data_pull.get_collected_data('')

def re_enroll_data_clean(total_enroll_df):
    # for enrollment by race and ethnicity
    ccd_results = enrollment_data_cleaned()
    ccd_results = ccd_results.drop(columns=['state'])
    ccd_results['asian_pacific_islander_combined'] = ccd_results['asian_pacific_islander'].apply(int_or_none)+ccd_results['nat_hawaiian_pacific_islander'].apply(int_or_none)
    ccd_results = ccd_results.drop(columns=['asian_pacific_islander', 'nat_hawaiian_pacific_islander'])
    ccd_results = ccd_results.rename(columns={'asian_pacific_islander_combined':'asian_pacific_islander'})
    print(ccd_results.columns)
    ccd_results['fy'] = ccd_results['fy'].astype('Int64')
    ccd_results = ccd_results.loc[:,['state_abrv','year', 'fy', 'total_enrollment', 'american_indian_alaska_native', 'asian_pacific_islander','hispanic', 'black', 'white', 'two_or_more']]
    # print(ccd_results.head().to_string())


    #merging collected and current records

    #get collected data from data collection sheet
    collected_enr_re = get_collected_data(metric = 'enroll_race_ethnicity')
    collected_enr_re.columns = collected_enr_re.iloc[0,:]
    collected_enr_re = collected_enr_re.iloc[1:,:]
    collected_enr_re.columns = [x.strip().replace('\n','_').lower().replace(' ','_').replace('/','') for x in collected_enr_re.columns]
    collected_enr_re['asian_pacific_islander_combined'] = collected_enr_re['asian'].apply(int_or_none)+collected_enr_re['native_hawaiianpacific_islander'].apply(int_or_none)
    popping_col = collected_enr_re.pop('asian_pacific_islander_combined')
    collected_enr_re.insert(3,'asian_pacific_islander_combined', popping_col)
    collected_enr_re = collected_enr_re.rename(columns={'asian_pacific_islander_combined':'asian_pacific_islander','updated_source_year':'year','state':'state_abrv'})

    collected_enr_re = collected_enr_re.drop(columns=['previous_source_link','previous_source_year','updated_source_link','asian','native_hawaiianpacific_islander'])
    collected_enr_re = collected_enr_re.loc[:,:'two_or_more']
    # collected_enr_re['total_enrollment'] = 
    collected_enr_re = collected_enr_re.loc[:,['state_abrv', 'year', 'american_indian_alaska_native', 'asian_pacific_islander','hispanic', 'black', 'white', 'two_or_more']]
    collected_enr_re['fy'] = (
        pd.to_numeric(collected_enr_re['year'].str[-4:], errors='coerce') - 2000
    ).astype('Int64')
    collected_enr_re = collected_enr_re[collected_enr_re['year'].isnull()==False]
    collected_enr_re = collected_enr_re[collected_enr_re['fy']==25]

    # print(collected_enr_re.head().to_string(max_colwidth=20))



    #Identify rows NOT already in current_records
    existing_pairs = set(zip(ccd_results['state_abrv'], ccd_results['fy']))
    updated_data_filtered = collected_enr_re[~collected_enr_re.apply(lambda row: (row['state_abrv'], row['fy']) in existing_pairs, axis=1)]
    # print(updated_data_filtered.to_string())


    #Add missing columns to updated_data so it matches current_records
    # updated_data_filtered['fy'] = (pd.to_numeric(updated_data_filtered['year'].str[:4], errors='coerce') - 2000).astype('Int64')
    columns_order = ccd_results.columns.to_list()
    columns_order.remove('total_enrollment')
    # print(columns_order)
    # print('updated data filtered column')
    # print(updated_data_filtered.columns)

    # print("\nExpected columns (columns_order):")
    # print(columns_order)

    # print("\nActual columns in updated_data_filtered:")
    # print(updated_data_filtered.columns.tolist())
    updated_data_filtered = updated_data_filtered[columns_order]  # Reorder columns to match

    #Merge (append)
    merged_df = pd.concat([ccd_results, updated_data_filtered], ignore_index=True)
    enrollment_merged_df_re = merged_df.sort_values(by=['state_abrv','year'])
    enrollment_merged_df_re = enrollment_merged_df_re.loc[enrollment_merged_df_re.groupby('state_abrv')['fy'].idxmax()].reset_index(drop=True)

    updated_data = total_enroll_df[total_enroll_df['fy']==25]
    # print(updated_data.to_string())
    update_dict = dict(zip(updated_data['state_abrv'],updated_data['total_enrollment']))

    for row in enrollment_merged_df_re.itertuples(index=True):
        if str(row.total_enrollment).lower() == 'nan' and isinstance(row.total_enrollment, float):
            result = update_dict.get(row.state_abrv)
            # print(result)
            if row.fy == 25:
                enrollment_merged_df_re.loc[row.Index,'total_enrollment'] = result
    # print(enrollment_merged_df_re.to_string())
    # collected_df = data_pull.get_collected_data('')
    return enrollment_merged_df_re

# %%
##########################
"""NAEP DATA"""
def get_naep_files(total = True):
    naep_dir = Path(r'C:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data\Data Packets\K-12\data\nces\NAEP')
    total_list = []
    r_and_e_list = []
    for file in naep_dir.iterdir():
        if 'ethinicity' in str(file):
            r_and_e_list.append(file)
        elif 'All students' in str(file):
            total_list.append(file)
    if total==False:
        return r_and_e_list
    else:
        return total_list


def get_naep_data_long():
    
    
    folder = r'C:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data\Data Packets\K-12\data\nces\NAEP\longitudinal'
    file_list = glob.glob(os.path.join(folder,'*'))
    dfs = []
    for file in file_list:
        filename = str(file).split('\\')[-1]
        df = pd.read_excel(file, header=None)
        
        if 'Grade 4' in str(filename):
            grade = 4
        else:
            grade = 8

        if 'Reading' in str(filename):
            subject = 'reading'
            print(f'reading from {str(filename)}')
        else:
            subject = 'math'
            print(f'math from {str(filename)}')
        

        for i,j in enumerate(df[0]):
            if 'year' in str(j).lower():
                start = i
            elif 'note' in str(j).lower():
                stop = i


        df.columns = df.iloc[start,:]
        # print(df.to_string())
        df.columns = [x.strip().lower().replace(' ', '_') for x in df.columns]
        df = df.iloc[start+1:stop,:].dropna(subset='year').reset_index()
        df['grade'] = grade
        df['subject'] = subject
        df['state_abrv'] = df['jurisdiction'].apply(get_intitials)
        df = df.loc[:,['state_abrv','jurisdiction', 'year','grade','subject','at_or_above_proficient']]
        dfs.append(df)
    export = pd.concat(dfs)
    export = export[export['state_abrv'].notna()]
    export = export.reset_index(drop=True)
    return export
        
def get_naep_data():
    
    
    file_list = get_naep_files()
    dfs = []
    for file in file_list:
        filename = str(file).split('\\')[-1]
        df = pd.read_excel(file, header=None)
        
        if 'Grade 4' in str(filename):
            grade = 4
        else:
            grade = 8

        if 'Reading' in str(filename):
            subject = 'reading'
            print(f'reading from {str(filename)}')
        else:
            subject = 'math'
            print(f'math from {str(filename)}')
        

        for i,j in enumerate(df[0]):
            if 'year' in str(j).lower():
                start = i
            elif 'note' in str(j).lower():
                stop = i


        df.columns = df.iloc[start,:]
        # print(df.to_string())
        df.columns = [x.strip().lower().replace(' ', '_') for x in df.columns]
        df = df.iloc[start+1:stop,:].dropna(subset='year').reset_index()
        df['grade'] = grade
        df['subject'] = subject
        df['state_abrv'] = df['jurisdiction'].apply(get_intitials)
        df = df.loc[:,['state_abrv','jurisdiction', 'year','grade','subject','at_or_above_proficient']]
        dfs.append(df)
    export = pd.concat(dfs)
    export = export[export['state_abrv'].notna()]
    export = export.reset_index(drop=True)
    return export
        









    # # excel_file = pd.ExcelFile(get_naep_file)
    # for sheet in excel_file.sheet_names:
    #     if '2011 - 2024_States':
    #         df = excel_file.parse(sheet_name=sheet, header=None)
    #         for i,j in enumerate(df[0]):
    #             if re.search(r'[Ss]tate', str(j)):
    #                 df.columns = df.iloc[i]
    #                 df = df.iloc[i+1:,:]
# %%

def get_naep_workbook_data(**kwargs):
    option = kwargs.get('option',False)
    
    naep_graphics_file = r"c:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data\Data Packets\K-12\data\nces\NAEP\archive\SL_NAEP Graphics_2025.xlsm"
    excel_file = pd.ExcelFile(naep_graphics_file)
    
    if option == 'frl':
        df = excel_file.parse(sheet_name='NAEP by FRL', header = None)    
    elif option == 'ell':
        df = excel_file.parse(sheet_name='NAEP by ELL', header = None)
    elif option == 'swd':
        df = excel_file.parse(sheet_name='NAEP by SWD', header = None)
    elif option == 'state cut':
        df = excel_file.parse(sheet_name='NAEP vs State Cut Score', header = None)
    else:
        df = excel_file.parse(sheet_name='NAEP by R&E | 2011 - 2024', header = None)
    return df



# %%
##########################
"""Perkins Data"""
def get_cte_data():
    data_dir = r'C:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data\Data Packets\K-12\data\perkins'
    
    files = glob.glob(os.path.join(data_dir,'*'))
    for file in files:
        filename = file.split('\\')[-1]
    
        if 'cte' not in filename:
            print('nope')
        else:
            return file
        

def get_clean_23_enrollment(input_file):
    import csv
    import pandas as pd
    
    # Read and process the CSV file
    output_data = []
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
       
        # Find the header line (starts with "State Abbr")
        header_start = None
        for i, line in enumerate(lines):
            if 'State Abbr' in line and 'State Name' in line:
                header_start = i
                break
       
        # Extract header and data rows
        if header_start is not None:
            csv_content = lines[header_start:]
           
            reader = csv.DictReader(csv_content)
           
            for row in reader:
                # Get the actual column names from the row
                state_abbr_key = [k for k in row.keys() if 'State Abbr' in k][0] if any('State Abbr' in k for k in row.keys()) else None
                state_name_key = [k for k in row.keys() if k == 'State Name'][0] if 'State Name' in row.keys() else None
                
                if not state_abbr_key or not state_name_key:
                    continue
                
                state_abbr = row[state_abbr_key]
                state_name = row[state_name_key]
                
                # Handle None values
                if state_abbr is None or state_name is None:
                    continue
                    
                state_abbr = state_abbr.strip()
                state_name = state_name.strip()
               
                # Stop processing if we hit the metadata footer or empty rows
                if not state_abbr or not state_name or state_abbr.startswith('Data Source:') or state_abbr.startswith('†') or state_abbr.startswith('–') or state_abbr.startswith('‡'):
                    break
               
                # Clean the data - start with state abbreviation and name
                cleaned_row = {
                    'State Abbr': state_abbr,
                    'State Name': state_name
                }
               
                for key, value in row.items():
                    if key not in [state_abbr_key, state_name_key]:
                        # Extract column name
                        if '[State] 2022-23' in key:
                            col_name = key.replace(' [State] 2022-23', '').strip()
                        elif 'for SY 2014-15 onward [State] 2022-23' in key:
                            col_name = 'Total Enrollment'
                        else:
                            col_name = key
                       
                        # Handle special characters (†, –, ‡) and None
                        if value is None:
                            cleaned_row[col_name] = None
                        else:
                            cleaned_value = value.strip()
                            if cleaned_value in ['†', '–', '‡', '']:
                                cleaned_row[col_name] = None
                            else:
                                # Remove commas and convert to integer
                                try:
                                    cleaned_row[col_name] = int(cleaned_value.replace(',', ''))
                                except:
                                    cleaned_row[col_name] = cleaned_value
               
                output_data.append(cleaned_row)
    
    # Create DataFrame
    output_df = pd.DataFrame(output_data).reset_index(drop=True)
    output_df.columns = [x.replace('.','').strip().lower().replace(' ','_').replace('(','').replace(')','') for x in output_df.columns]
    
    # Reorder columns to have state_abbr first, then state_name
    cols = output_df.columns.tolist()
    cols.remove('state_abbr')
    cols.remove('state_name')
    output_df = output_df[['state_abbr', 'state_name'] + cols]

    #combine for asian/pacific islander
    output_df['asian/pacific_islander'] = output_df['asian_or_asian/pacific_islander_students']+output_df['nat_hawaiian_or_other_pacific_isl_students']
    output_df = output_df.drop(columns=['asian_or_asian/pacific_islander_students','nat_hawaiian_or_other_pacific_isl_students'])

    #rename total column and drop merged cols
    output_df = output_df.rename(columns={'grand_total':'total'})
    # print('current cols:')
    # print(output_df.to_string())
    #rename columns
    column_names = ['state_abrv', 'state', 'total', 'nat_am_or_ak', 'black', 'hispanic','white', 'two_or_more','asian_pacific_islander']
    
    output_df.columns = column_names
    # column
    return output_df

def clean_cte_data():
    df = pd.read_excel(get_cte_data())
    df.columns = [x.split('(', maxsplit=1)[0].strip().replace(' ','_').lower() for x in df.columns]
    df = df.rename(columns={'state/territory_name': 'state'})



    df['state_abrv'] = df['state'].apply(lambda x: state_ref_lower.get(x.lower()))
    state_abrv_pop = df.pop('state_abrv')
    df.insert(0,'state_abrv', state_abrv_pop)
    df = df[df['state_abrv'].isnull()==False].reset_index(drop=True)
    df= df.sort_values(by='state')

    df = df.drop(columns=['enrollment_type','education_level', 'program_year','unknown', 'individuals_with_disabilities', 'individuals_from_economically_disadvantaged_families', 'english_learners'])
    

    df = df.rename(columns={'grand_total':'total'})

    df['native_hawaiian_or_other_pacific_islander'] = pd.to_numeric(df['native_hawaiian_or_other_pacific_islander'], errors='coerce')
    df['asian'] = pd.to_numeric(df['asian'], errors='coerce')

    df['asian/pacific_islander'] = df['native_hawaiian_or_other_pacific_islander']+df['asian']
    # print(df.columns.to_list())

    df = df.drop(columns=['native_hawaiian_or_other_pacific_islander','asian'])

    column_names = ['state_abrv', 'state', 'total', 'nat_am_or_ak', 'black', 'hispanic','white', 'two_or_more','asian_pacific_islander']
    df.columns = column_names
    
    return df


def cte_calculated():
    cte_data = clean_cte_data()


    cte_enrollment_23_file = r'c:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data\Data Packets\K-12\data\perkins\ELSI_csv_export_6389613776445034225316.csv'
    enrollment_data = get_clean_23_enrollment(cte_enrollment_23_file)
    # print(enrollment_data.to_string())
    # dfs = {'cte':cte_data,'enrollment':enrollment_data}



    concat_dfs = []
    # grand_total
    for state in state_abbreviations:
        # print(state)
        state_dfs = {}
        # for k,df in dfs.items():

        result = cte_data[cte_data['state_abrv']==state]
        # rows = []

        for row in result.itertuples():
            row_dict = row._asdict()
            # rows.append(row_dict)
        
            total = row_dict.get('total')
            
            for col_name, value in row_dict.items():
                # print(f'value: {value}')
                skip = ['Index','total', 'state', 'state_abrv']
                

                if any(elem in col_name for elem in skip):
                    continue
                else:  # Skip the index
                    # print(value, total)
                    try:
                        if isinstance(value, float) and 'nan' in str(value).lower():
                            perc_o_cte = "N/A"    
                            # print(bordered(col_name))
                            # print(f'number in cat: {value}')

                            # print(f'total cte participants num: {total}')
                            # print("perc_o_total:{0:.2%}".format(perc_o_cte))
                        else:
                            perc_o_cte = int(value)/int(total)
                    except:
                        print(f'{col_name} is trouble')
                        print(result.to_string())
                        print(value)
                        print('-----------')
                        print(total)
                        break


                    
                    
                    # by enrollment
                    enroll_denom = enrollment_data[enrollment_data['state_abrv']==state].reset_index(drop=True)
                    # print(enroll_denom)
                    denominator = enroll_denom.loc[0,col_name]
                    if isinstance(denominator, float) and 'nan' in str(denominator).lower():
                        # print('the enrollment is na for this state')
                        perc_o_enr = 'N/A'
                    elif isinstance(value, float) and 'nan' in str(value).lower():
                        perc_o_enr = 'N/A'
                    else:
                        perc_o_enr = int(value)/int(denominator)
                        # print(f'enrollment denominator: {denominator}')
                        # print("perc_o_enr:{0:.2%}".format(perc_o_enr))

                    # result['formatted_pct'] = result['at_or_above_proficient'].apply(lambda x: f"{(x/100):.0%}")

                    df = pd.DataFrame({'state':[state],'group':[col_name], 'perc_o_cte':[perc_o_cte], 'perc_o_enr':[perc_o_enr]})
                    concat_dfs.append(df)



        
    state_dfs = pd.concat(concat_dfs).reset_index(drop=True)
    return state_dfs

# %%
###########################
## SAT data
def get_sat_graph_data():
    sat_dir = r"c:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data\Data Packets\K-12\data\college board\ap data\school-report-of-ap-exams-grades-11-12-2023-2024.xlsx"
    

    excel_file = pd.ExcelFile(sat_dir)
    df = excel_file.parse(sheet_name='cleaned')
    columns = ['state_abrv','state', '11_12_enrollment','total_ap_stu','total_ap_exams', 'ap_exams_per_k_11_12', 'perc_3_orbetter']
    df.columns = columns

    df['perc_in_an_ap'] = pd.to_numeric(df['total_ap_stu'])/pd.to_numeric(df['11_12_enrollment'])
    df=df.loc[:,['state_abrv','perc_in_an_ap','ap_exams_per_k_11_12', 'perc_3_orbetter']]

    # print(df.to_string())
    return df


# %%
###########################
## DATA COLLECTION
def get_collected_data_file():
    data_directory = Path(r'C:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data\Data Packets\K-12\data')
    
    for file in data_directory.iterdir():
    
        if 'data_collection' in file.name.lower() and 'copy' not in file.name.lower():
            data_collection_file = data_directory / file.name        
            return file
       

def get_collected_data(**kwargs):
    get_sheets = kwargs.get('get_sheets', False)
    metric = kwargs.get('metric', False)
    no_header = kwargs.get('no_header', False)
    index_col = kwargs.get('index_col', False)
    
    file = get_collected_data_file()
    excel_file = pd.ExcelFile(file)
    if get_sheets != False:
        # df = excel_file.parse(sheet_name='Tracking', header=None)
        # sheets = df.iloc[9:20,0:6]
        sheets = excel_file.sheet_names
        return sheets

    if no_header == False:
        df = excel_file.parse(sheet_name=metric)
    else:
        if index_col != False:
            df = excel_file.parse(sheet_name=metric, header=None, index_col=index_col)
        else:
            df = excel_file.parse(sheet_name=metric, header=None)

    return df




# %%
def get_older_data(**kwargs):
    file = r"C:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data Packets\K-12\data\For_Ref_December 2025 K-12 Education Dataset.xlsm"
    get_sheets = kwargs.get('get_sheets', False)
    metric = kwargs.get('metric', False)
    
    
    excel_file = pd.ExcelFile(file)
    if get_sheets != False:
        df = excel_file.parse(sheet_name='Tracking', header=None)
        sheets = df.iloc[9:20,0:6]

        return sheets

    df = excel_file.parse(sheet_name=metric)
    return df

def enrollment_ses():
    df = get_older_data(metric='K-12 level of income')
    df.columns = df.iloc[2,:]
    df = df.iloc[4:0,0:2].reset_index(drop=True)
    print(df.columns)
    df.columns = [x.strip().lower().replace(' ','_') for x in df.columns]
    df['state_abrv'] = df['state'].apply(lambda x: state_ref_lower.get(str(x).lower()))
    return df

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
    act_pdf = r"c:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data\Data Packets\K-12\data\2024-Average-ACT-Scores-by-State-Percent-Meeting-Benchmarks.pdf"

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
