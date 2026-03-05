# %% imports
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

import data_collection.pull_data as data_pull



merge_files = {}
# %% Getting Merge tag info


#get merge tags sheet data
merge_tag_df = data_pull.get_collected_data(metric = 'merge_tags')


merge_tag_df = merge_tag_df[merge_tag_df['type']!='graph']
col_order = merge_tag_df.sort_values(by='order')['field'].to_list()

# # print(merge_tag_df.to_string())
merge_tags_by_datasource = dict(tuple(merge_tag_df.groupby('data source var name')))
merge_files = {}

# %%create merge file

merge_template = pd.DataFrame(columns=merge_tag_df['field'], index=[x for x in state_abbreviations if not 'US'])
# # print(merge_template)
# print_merge_tags()

# %%
"""
#################################################
Actual Data Gathering done below
#################################################
"""
# %% NAEP Data ++++++++++++
#pull data
naep = data_pull.get_naep_data()

# # print(naep.to_string())
# for name, value in naep.items():
#     # print(name)
#     # print(value)

#merge file setup
naep_merge = pd.DataFrame({'state_abrv':state_abbreviations})


#get only naep tags
naep_tags = merge_tags_by_datasource['naep']
naep_tags_list = merge_tags_by_datasource['naep']['field'].to_list()
# # print(naep_tags_list)
naep_tags_list = [x.strip() for x in naep_tags_list if 'rank' not in x.lower()]
#data wrangling

dfs = []
for tag in naep_tags_list:
    # # print('=============')
    # # print(tag)
    # # print('__________________')
    try:
        grade = re.search(r'(\d)th [Gg]rade', str(tag)).group(1)
    except:
        continue
    subject = re.search(r'[Gg]rade\s(.+)\sProficiency', str(tag)).group(1).lower().strip()
    
    result = naep[(naep['grade']==int(grade)) &(naep['subject']==subject)]
    #filter main data for category
    result['rank'] = result['at_or_above_proficient'].rank().astype(int)
    result['formatted_pct'] = result['at_or_above_proficient'].apply(lambda x: f"{(x/100):.0%}")
    result = result.loc[:,['state_abrv', 'formatted_pct', 'rank']]
    # # print(result.to_string())

    renaming_dict = {
    "formatted_pct": f"{tag}",
    "rank": f"State Rank - {tag}"
    }
    result = result.rename(columns=renaming_dict)
    # # print(type(result))
    dfs.append(result)

# Concatenate all DataFrames on 'state_abrv' using it as index
naep_df = pd.concat([df.set_index('state_abrv') for df in dfs], axis=1).reset_index()
# # print(*naep_df.columns,sep='\n')

naep_df = naep_df[naep_df['state_abrv'].isin(state_abbreviations_priority)].reset_index(drop=True)


merge_files['naep'] = naep_df



#%% CCD Merge data +++++++++++++++++++

# ============================================================================
#=== CCD Merge Data
# ============================================================================
'''
Set up for CCD Data and tracking
'''
#template set up
ccd_merge = pd.DataFrame({'state_abrv':state_abbreviations})


#get only ccd tags
ccd_tags = merge_tags_by_datasource['ccd']
ccd_tags_list = merge_tags_by_datasource['ccd']['field'].to_list()
ccd_tags_list = [x.strip() for x in ccd_tags_list]
# print(ccd_tags_list)

#final columns needed set up
col_list = ['state_abrv']
col_list.extend(ccd_tags_list)

#merge tags broken up by methods
# # print(ccd_tags_list)
ccd_methods_dict = dict(tuple(ccd_tags.groupby('method')))
ccd_results = data_pull.enrollment_data_cleaned()
# # print(ccd_results.to_string())
#actual data pull
"""
-Gets CCD Data for enrollment and school counts
-prepares for merge template
"""

#alter for enrollment
max_by_state = ccd_results.groupby('state_abrv').agg({'year':'max'}).reset_index()
ccd_enroll_merge = ccd_merge.merge(max_by_state, on='state_abrv', how='left')
#rename year column
ccd_enroll_merge.rename(columns={"year": "Years - K-12 Enrollment by Race Graphic"})
# # print(ccd_enroll_merge.to_string())


#create another template
ccd_counts_merge = ccd_merge

def alter_st_ratio(text):
    parts = str(text).split(':')
    new = ' '.join(parts)
    return new

#pull in school count data
ccd_school_counts = data_pull.ccd_counts_cleaned(debug=False)
ccd_counts_merge = ccd_counts_merge.merge(ccd_school_counts, on='state_abrv', how = 'outer')
ccd_counts_merge["student_teacher_ratio"] = ccd_counts_merge['student_teacher_ratio'].apply(lambda x: f"{x:,.1f}" if pd.notna(x) else x)
# ccd_counts_merge["student_teacher_ratio"] = ccd_counts_merge["student_teacher_ratio"].apply(alter_st_ratio)

#renaming columns
ccd_counts_merge['Years - Student-Teacher Ratio'] = "2023-2024"
ccd_counts_merge["State Rank - Student-Teacher Ratio"] = ccd_counts_merge['student_teacher_ratio'].rank().apply(lambda x: f"{int(x)}" if pd.notna(x) else x)
ccd_counts_merge['num_schools'] = ccd_counts_merge['num_schools'].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else x)

ccd_counts_merge["Years - K-12 Enrollment by Race Graphic"] = "2022-2023"
ccd_counts_merge["Years - K-12 Enrollment by SES Graphic"] = "2022-2023"
renaming_dict = {
    "num_schools": "Number of Public Schools",
    "num_districts": "Number of Public School Districts",
    "num_districts": "Number of Public School Districts",
    "student_teacher_ratio":"Student-Teacher Ratio"
    }
ccd_counts_merge = ccd_counts_merge.rename(columns=renaming_dict)

# merge column and template
ccd_all_merge = pd.merge(ccd_enroll_merge,ccd_counts_merge, on='state_abrv', how = "outer")

#get only needed columns for merging
ccd_all_merge = ccd_all_merge.loc[:,col_list]
ccd_all_merge = ccd_all_merge[ccd_all_merge['state_abrv'].isin(state_abbreviations_priority)].reset_index(drop=True)
print(ccd_all_merge.to_string(max_colwidth=100))


#save to merge dict
merge_files['ccd'] = ccd_all_merge
    # return ccd_all_merge

# ============================================================================
#=== SAT data
# ============================================================================
# %% SAT Data  ++++++++++++++++++++
from data_collection.scraped import sat_data
sat_df = sat_data.get_sat_data().drop(columns = 'index')
sat_df.columns = ['state_abrv','Est. % of Graduates Participating in SAT','Avg SAT Score']

sat_df = sat_df[sat_df['state_abrv'].isin(state_abbreviations_priority)].reset_index(drop=True)
# print(sat_df.to_string())

merge_files['sat'] = sat_df
# %% ACT DATA ++++++++++++++++ comeback
from data_collection.scraped import act_data_2024
act_df = act_data_2024.get_act_data()
act_df = act_df.loc[:,['state_abrv','est_percent_grads_tested','avg_composite_score']]
act_df['est_percent_grads_tested'] = act_df['est_percent_grads_tested'].apply(lambda x: f"{int(x)}%" if pd.notna(x) else x)
act_df['avg_composite_score'] = act_df['avg_composite_score']
columns = ['state_abrv','Est. % of Graduates Participating in ACT', 'Avg ACT Score']
act_df.columns = columns
# act_df.columns = ['state_abrv','Est. % of Graduates Participating in SAT','Avg SAT Score']

act_df = act_df[act_df['state_abrv'].isin(state_abbreviations_priority)].reset_index(drop=True)
merge_files['act'] = act_df
print(act_df.to_string())



# %%Perkins Data ++++++++++++++++

# ============================================================================
#=== Perkins data
# ============================================================================
# %% HS Graduation Rate
hs_grad_rate_df = data_pull.get_collected_data(metric='hs_grad_rate')
hs_grad_rate_df.columns = hs_grad_rate_df.iloc[0,:].reset_index(drop=True)
hs_grad_rate_df = hs_grad_rate_df.iloc[2:,:].reset_index(drop=True)
hs_grad_rate_df = hs_grad_rate_df.loc[:,['state', '2023-2024 HS grad rate']]
hs_grad_rate_df = hs_grad_rate_df.dropna(subset='state')
hs_grad_rate_df['rank'] = hs_grad_rate_df['2023-2024 HS grad rate'].rank(method='min').astype('Int64').apply(lambda x: f"{int(x)}" if pd.notna(x) else x)
hs_grad_rate_df['2023-2024 HS grad rate'] = hs_grad_rate_df['2023-2024 HS grad rate'].apply(lambda x: f"{int(x)}%" if pd.notna(x) else x)
# act_df['avg_composite_score'] = act_df['avg_composite_score'].apply(lambda x: f"{int(x)}%" if pd.notna(x) else x)

hs_grad_rate_df.columns = ['state_abrv', 'Public HS Graduation Rate', 'State Rank - Public HS Graduation Rate']

hs_grad_rate_df = hs_grad_rate_df[hs_grad_rate_df['state_abrv'].isin(state_abbreviations_priority)].reset_index(drop=True)

merge_files['hs_grad_rate'] = hs_grad_rate_df


# print(hs_grad_rate_df.to_string())

# %% Per pupil
per_pupil_exp_df = data_pull.get_collected_data(metric='per_pupil_exp')
per_pupil_exp_df = per_pupil_exp_df.loc[:,'state_abrv':]
per_pupil_exp_df['rank'] = per_pupil_exp_df['expenditures'].rank().astype(int)
per_pupil_exp_df['expenditures'] = per_pupil_exp_df['expenditures'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else x)

per_pupil_exp_df.columns = ['state_abrv', 'Per-Pupil Expenditure', 'State Rank - Per-Pupil Expenditure']
# print(per_pupil_exp_df.to_string())
per_pupil_exp_df = per_pupil_exp_df[per_pupil_exp_df['state_abrv'].isin(state_abbreviations_priority)].reset_index(drop=True)

merge_files['per_pupil'] = per_pupil_exp_df


# %% state assessment text
state_assess_df = data_pull.get_collected_data(metric='state_assessment_text')
state_assess_df = state_assess_df.loc[:,'state_abrv':]
state_assess_df.columns = ['state_abrv','State Assessment Text']


state_assess_df = state_assess_df[state_assess_df['state_abrv'].isin(state_abbreviations_priority)].reset_index(drop=True)
# print(state_assess_df.to_string(max_colwidth = 30))
merge_files['state_assess'] = state_assess_df

# %% Chronic Absenteeism years
#by race and ethnicity
chron_abs_race_df = data_pull.get_collected_data(metric = 'chron_abs_race', no_header=True)
chron_abs_race_df.columns = chron_abs_race_df.iloc[1,:]

chron_abs_race_df = chron_abs_race_df.iloc[2:,:]

# # print(chron_abs_race_df.columns)
chron_abs_race_df = chron_abs_race_df.loc[:,['State', 'Source Year']]
chron_abs_race_df.columns = ['state_abrv','Years - Chronic Absenteeism by R/E']

#other
chron_abs_other_df = data_pull.get_collected_data(metric = 'chron_abs_other', no_header=True)
chron_abs_other_df.columns = chron_abs_other_df.iloc[1,:]

chron_abs_other_df = chron_abs_other_df.iloc[2:,:]
# # print(chron_abs_other_df.columns)
chron_abs_other_df = chron_abs_other_df.loc[:,['State', 'Source Year']]
chron_abs_other_df.columns = ['state_abrv','Years - Chronic Absenteeism by Other Subgroup']



chron_abs = pd.merge(chron_abs_race_df, chron_abs_other_df, on='state_abrv', how='outer')

#priority states only
chron_abs = chron_abs[chron_abs['state_abrv'].isin(state_abbreviations_priority)].reset_index(drop=True)
merge_files['chron_abs'] = chron_abs


# # print(chron_abs.to_string())

# chron_abs_other_df = data_pull.get_collected_data(metric = 'chron_abs_race')
# chron_abs_other_df.columns = chron_abs_other_df.iloc[1,:]


# ============================================================================
#=== help
# ============================================================================
# %%
# print()
def print_tags_tracking(**kwargs):
    option = kwargs.get('option', False)
    done = list(merge_files.keys())
    
    for k,v in merge_tags_by_datasource.items():
        source = k
        if option!=False:
            if option!=source:
                continue
        methods_dict = dict(tuple(v.groupby('method')))
        if source in done:
            continue
        # print('=================')
        # print(source)
        
        # for mk,mv in methods_dict.items():
            # print('___________')
            # print(mk)
            # print(mv.to_string())
            # print('\n')
    # merge_tags_by_datasource['']


# print_tags_tracking()


# %% etc
# look for graphs

full_state_names = pd.DataFrame({'state_abrv':state_abbreviations_priority})
full_state_names['00 State'] = full_state_names['state_abrv'].apply(lambda x: state_ref_r_proper.get(x))
# # print(full_state_names.to_string())

full_state_names['ACT/SAT graph title'] = 'Percentage of Students Meeting 3 or More ACT College Readiness Benchmarks by Race/Ethnicity | 2025'
merge_files['other_state_info'] = full_state_names

# %% The end

merge_tags_gathered = []
for k,v in merge_files.items():
    # # print(k)
    # # print(v.columns)
    for i,col in enumerate(v.columns):
        
        merge_tags_gathered.append(col)

merge_tags = [x for x in merge_tag_df['field'].to_list() if '@' not in str(x)]
# print(*merge_tags, sep = '\n')
# print('==========================')
for tag in merge_tags:
    if tag in merge_tags_gathered or '@' in tag:
        continue
    # else:
    #     # print(tag)
# %%

for tag in merge_tags_gathered:
    if tag in merge_tags:
        continue
    # else:
        # print('this one didnt find a match')
        # print(tag)

# print(merge_tags)

# %%

# for k,v in merge_files.items():
    # print(k)
    # print(v.to_string())
# %%
# # print(merge_files.get('ccd').to_string())
# merge_files.keys

# Assuming your dictionary is structured like: {'naep': df_naep, 'ccd': df_ccd, 'sat': df_sat, ...}

# Start with first dataframe
merged_df = list(merge_files.values())[0]

# Merge all others
for df in list(merge_files.values())[1:]:
    merged_df = merged_df.merge(df, on='state_abrv', how='outer')

# Set index
# merged_df.set_index('state_abrv', inplace=True)

merged_df = merged_df.loc[:,['state_abrv']+col_order]
print(merged_df.to_string(max_colwidth=30))

# %% export
merge_folder = r'C:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data\Data Packets\K-12\merge_files\text'
merged_df.to_csv(os.path.join(merge_folder,'merge_text_file.csv'), index=False)

# %%
