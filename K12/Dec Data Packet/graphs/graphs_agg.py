# %% [markdown]
# # Data Analysis & Visualization Notebook
# 
# ## Overview
# 
# Brief description of your analysis objectives and the data sources
# you’ll be working with.
# 

# %% [markdown]
# 
# ## Setup & Dependencies
# 

# %%
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

#Import Data
###################
import data_sources.data_collection.pull_data as data_pull
from graphs.viz_graphs_template import *


# Create folder if needed
graphs_dir = r"C:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data Packets\K-12\graphs"

import matplotlib.pyplot as plt
from matplotlib import font_manager

font_dirs = [r"C:\Users\clutz\project_folder\Projects\fonts"]  # The path to the custom font file.
font_files = font_manager.findSystemFonts(fontpaths=font_dirs)

import os

font_dir = r"C:\Users\clutz\project_folder\Projects\fonts"
print([f for f in os.listdir(font_dir) if f.lower().endswith(".ttf")])


for font_file in font_files:
    font_manager.fontManager.addfont(font_file)

sorted(font_manager.get_font_names())



# %% [markdown]
# ## Fonts

# %%
from matplotlib import font_manager
import matplotlib as mpl
import os

font_dir = r"C:\Users\clutz\project_folder\Projects\fonts"

# 1. Verify TTF files exist
print("Fonts found in folder:")
print([f for f in os.listdir(font_dir) if f.lower().endswith(".ttf")])

# 2. Register custom fonts
font_files = font_manager.findSystemFonts(fontpaths=[font_dir])
for font_file in font_files:
    font_manager.fontManager.addfont(font_file)

# 3. Rebuild font cache properly
font_manager._load_fontmanager(try_read_cache=False)

# 4. Check for Lato fonts
lato_fonts = [f.name for f in font_manager.fontManager.ttflist if "Lato" in f.name]
print("Lato fonts recognized:", lato_fonts)


# %%
import plotly.io as pio

pio.templates.default = None
pio.templates["custom"] = pio.templates["plotly"]

pio.templates["custom"].layout.font = {
    "family": "Lato", 
    "color": hunt_darkgray
}


# %% [markdown]
# ## Graph Controls

# %%
#graph widget
import json, os
import ipywidgets as widgets
from IPython.display import display
from types import SimpleNamespace

# -----------------------------
# Config
# -----------------------------
SETTINGS_FILE = "toggle_settings.json"
DEFAULTS = {"save_it": False, "show_it": True, "just_one": False}


# -----------------------------
# Helpers
# -----------------------------
def load_settings(defaults=None):
    data = {}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
        except json.JSONDecodeError:
            print("Warning: settings file corrupted or empty. Recreating with defaults.")
            data = {}
    if defaults:
        for k, v in defaults.items():
            data.setdefault(k, v)
    return data


def save_settings(data):
    """Write settings to disk immediately."""
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved settings → {SETTINGS_FILE}")


def dict_to_namespace(d):
    return SimpleNamespace(**d)


# -----------------------------
# Load saved or default settings
# -----------------------------
settings_data = load_settings(DEFAULTS)
settings = dict_to_namespace(settings_data)


# -----------------------------
# Create widgets
# -----------------------------
save_toggle = widgets.Checkbox(value=settings.save_it, description="Save graphs")
show_toggle = widgets.Checkbox(value=settings.show_it, description="Show graphs")
just_one_toggle = widgets.Checkbox(value=settings.just_one, description="Just one graph")


# -----------------------------
# Unified event handler
# -----------------------------
def on_toggle_change(change):
    # Update dict + namespace
    settings_data["save_it"] = save_toggle.value
    settings_data["show_it"] = show_toggle.value
    settings_data["just_one"] = just_one_toggle.value

    settings.save_it = save_toggle.value
    settings.show_it = show_toggle.value
    settings.just_one = just_one_toggle.value

    save_settings(settings_data)  # persist immediately


# Attach handler to all three widgets
for toggle in (save_toggle, show_toggle, just_one_toggle):
    toggle.observe(on_toggle_change, names="value")

# -----------------------------
# Display
# -----------------------------
display(widgets.VBox([save_toggle, show_toggle, just_one_toggle]))


# %%
sizing = {
    '1.1':(171,151),
    '1.2':(505,91),#these two should be the same sime to keep consistency, 
    '1.3':(505,91),
    '1.4':(505,91),
    '2':(252,200),
    '3':(252,144),
    '4':(133,112),
    '4.5':(252,108),
    '4.6':(252,108),
    '5':(260,112),
    '5.3':(235,95),
    '5.7':(245,95),
    '6.1':(490,120),
    '6.2':(260,100),
    '6.3':(485,110),
    '7.1':(504,130),
    '7.2':(504,130),
    '7.3':(504,130),
    '8.1':(505,95),
    '8.2':(540,145),
    '8.3':(165,94),
    '8.4':(165,94),
    '8.5':(165,94),
    '9.1':(510,100),
}

def get_res(val, res): 
    val = val*res
    return val 
    
def get_sizing(graph_num, res=5):

    five_match=re.search(r'^5.\d', str(graph_num))
    four_match = re.search(r'^4.(\d)', str(graph_num))
    if four_match is not None:
        if int(four_match.group(1))<5:
            output = sizing.get('4')
        elif int(four_match.group(1))>=5:
            output = sizing.get(graph_num)

    elif five_match is not None:
        output = sizing.get('5')
    else:
        output = sizing.get(graph_num)
    print(f'output raw: {output}')
    


    output = tuple([get_res(x, res) for x in output])
    print(output)


    return output


get_sizing('8.3', 5)

# %%
# state_abbreviations_priority

# %% [markdown]
# ## Helper Functions

# %%
#save to folder
graphs_dir = r'C:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data\Data Packets\K-12\graphs'
# graphs_dir = r'C:\Users\clutz\Downloads\k12 datapackets'

def save_to_folder(fig,filename, g_width,g_height, state):
    # Create folder if needed
    output_folder = os.path.join(graphs_dir,state)
    os.makedirs(output_folder, exist_ok=True)

    # Save the file
    fig.write_image(
        
        os.path.join(output_folder,filename),
        width=g_width,
        height=g_height,
        scale=10  # For higher resolution (2x default)
    )


# %%
def get_highlight_color(x,state):
    if x==state:
        return hunt_purple
    else:
        return hunt_darkgray
    

# %%
# data_directory = Path(r'C:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data Packets\k12\data')
# def get_files():
#     file_dict = {}
#     for file in data_directory.iterdir():
#         print(file.name)
#         if 'naep' in file.name.lower():
#             naep_file = data_directory / file.name
#             file_dict['naep'] = naep_file
#         elif 'data_collection' in file.name.lower():
#             data_collection_file = data_directory / file.name
#             file_dict['data_collection'] = data_collection_file
        

#     return file_dict


        



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



# glob_pat = os.path.join(filepath, 'NAEP*.xlsx')
# files = glob.glob(glob_pat)
# print(merge_tags)
# for file in filepath:
# pd.ExcelFile()

# %%
def edit_year(year_val, delim):
    years_split = year_val.split(delim,1)
    new_years = []
    for year in years_split:
        if len(year)==4:
            new_years.append(int(year))
        else:
            year_alt = f'20{year}'
            new_years.append(int(year_alt))
    new_years = sorted(new_years)
    year_reformat = f'{new_years[0]}-{"<br>"}{new_years[1]}'
    return year_reformat

# %% [markdown]
# # Merge File

# %%
merge_dir = Path(r'C:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data\Data Packets\K-12\merge_files')
merge = False

merge_dfs = {}
for root, dir, files in os.walk(merge_dir):
    if len(files)!=0:
        # print(root)
        # print(files)
        file = files[0]
        print(file)
        df = pd.read_csv(os.path.join(root,file)).reset_index(drop=True)
        if any('Unnamed: 0' in str(x) for x in df.columns):
            df = df.drop(columns = ['Unnamed: 0'])
        

        print(df.to_string())
        type =root.split('\\')[-1]
        # print(type)
        merge_dfs[type] = df


# %%
# get merge file
# merge_file = pd.concat([merge_dfs.get('text'), merge_dfs.get('graphs')], axis=1).reset_index()
if merge == True:
    merge_file = merge_dfs.get('text').merge(merge_dfs.get('graphs'), on='state_abrv')

    print(merge_file.to_string())
    merge_file.to_csv(os.path.join(merge_dir,'merge.csv'), index=False)


# %% [markdown]
# # Graphs

# %% [markdown]
# ## Page 1

# %%
# pull in enrollment data
enroll_total_df = data_pull.total_enroll_data_clean()
enroll_re_df = data_pull.re_enroll_data_clean(enroll_total_df)

# print(enroll_total_df.to_string())
# print(enroll_re_df.to_string())

# %% [markdown]
# ### 1.1 Total K-12 Enrollment

# %%
#creates table 1.1
from graphs.viz_graphs_template import *
import plotly.graph_objects as go
import plotly.express as px

g_width,g_height = get_sizing('1.1')
axis_font_size = 40
# g_width = 1102
# g_height = 915
offset_control = .10
multiplier = 1.1
filename = f'1.1.png'
enroll_total_df = data_pull.total_enroll_data_clean()

for jur in state_abbreviations_priority:
    if jur == 'US':
        continue
    print(jur)
    #filter for only state vals
    result = enroll_total_df[enroll_total_df['state_abrv']==jur]
    # print(result.to_string())
    years = [edit_year(x,'-') for x in result['year'].to_list()]
    print(years)
    #call graph
    fig = graph_1_1(years, result['total_enrollment'], g_width, g_height)
    # print(type(fig))
    
    #position calculations for text annotations
    ymin = min(result['total_enrollment'])
    ymax = max(result['total_enrollment'])
    yrange = ymax - ymin
    offset = yrange * offset_control  # 5% of the total vertical range
    range_offset = yrange * (offset_control*2)

    enrollment_text = result['total_enrollment'].to_list()
    text_y_positions = []  # Store y-positions for text    
    alignment = []
    for i, x in enumerate(enrollment_text):
        if i == 0:
            # First element - compare with next
            next_val = enrollment_text[i+1]
            if next_val > x:
                value = x - offset  # Position below
                alignment.append('middle center')
            else:
                value = x + offset  # Position above
                alignment.append('middle center')
                
        elif i < len(enrollment_text) - 1:  # Fixed: was missing "- 1"
            # Middle elements - has both previous and next
            next_val = enrollment_text[i+1]
            last = enrollment_text[i-1]
            
            # Calculate slopes (direction of change)
            slope_to = x - last  # Positive if increasing
            slope_from = next_val - x  # Positive if will increase
            
            if slope_to > 0 and slope_from > 0:
                # Going up and will continue up
                value = x + (multiplier * offset)
                alignment.append('top left')
            elif slope_to < 0 and slope_from < 0:
                # Going down and will continue down
                value = x + (offset*multiplier)
                alignment.append('middle right')
            elif slope_to > 0 and slope_from < 0:
                # Peak (was going up, now going down)
                value = x + offset
                alignment.append('top center')
            elif slope_to < 0 and slope_from > 0:
                # Valley (was going down, now going up)
                value = x - offset
                alignment.append('bottom center')
            else:
                # Flat
                value = x + offset
                alignment.append('top center')

                
        else:
            # Last element - compare with previous
            last = enrollment_text[i-1]
                
            if x > last:
                if last==ymin:
                    value = x + (offset/2)  # Was increasing, put above
                    alignment.append('middle left')
                else:
                    value = x + offset  # Was increasing, put above
                    alignment.append('top left')

            else:
                if last==ymin:
                    value = x - (offset/2)  # Was increasing, put above
                    alignment.append('middle left')
                else:
                    value = x - offset  # Was decreasing, put below
                    alignment.append('bottom left')

        text_y_positions.append(value)
    print(len(alignment))
    print(len(text_y_positions))
    # Add text labels
    fig.add_trace(go.Scatter(
        x=years,
        y=text_y_positions,  # Use calculated positions
        mode='text',
        text=[f"{int(val):,}" for val in enrollment_text],  # Format numbers with commas
        textposition=alignment,
        textfont=get_base_text(45, bold = True),
        showlegend=False
    ))
    
    fig.update_yaxes(
        showticklabels=False,  # Hide tick labels
        showgrid=False,        # Hide gridlines
        zeroline=False,         # Hide zero line
        range=[ymin - range_offset, ymax + range_offset]
    )   
    fig.update_xaxes(
        tickfont = get_base_text(axis_font_size)
    ) 
    fig.update_layout(
        
        margin = dict(l=10, r=10, t=10, b=10)

    )
    
    if settings.show_it:
        fig.show()
        if settings.just_one:
            break
    if settings.save_it:
        save_to_folder(fig,filename,g_width,g_height,jur)

    
    # break

# %% [markdown]
# ### 1.2 Enrollment by Race and Ethnicity 

# %%
#creates GRAPH 1.2 (example of 100% bar)
from graphs.viz_graphs_template import *
import plotly.graph_objects as go
import plotly.express as px



#graph settings

aspect_ratio = 7
g_width,g_height = get_sizing('1.2', )
axis_font_size = 45
# graph_h = 458
# graph_wd = 2705


multiplier = 1.5
filename = f'1.2.png'
enroll_re_df = data_pull.re_enroll_data_clean(enroll_total_df)


us_values = enroll_re_df[enroll_re_df['state_abrv']=="US"]

us_values = us_values.sort_values('year', ascending=False).reset_index(drop=True)
# print(us_values[us_values['fy']==us_values['fy'].max()].to_string())
# us_total
for jur in state_abbreviations_priority:
    if jur == 'US':
        continue
    # print(jur)
    
    #fetch for state
    result = enroll_re_df[enroll_re_df['state_abrv']==jur]
    # print(result)
    
    us_series = us_values[us_values['fy']==us_values['fy'].max()]
    
    #set up/cleaning
    series_dict = {'state':result,'us':us_series}
    
    
    if all(len(x)==1 for x in series_dict.values()):
        # print('good to keep going')
        # print(series_dict.get('state').columns)
        categories = series_dict.get('state').columns[5:]
        state_vals = series_dict.get('state').iloc[0,5:].to_list()
        us_vals = series_dict.get('us').iloc[0,5:].to_list()
        both_values_dict = {"us":us_vals, 'state':state_vals}
        for k,v in both_values_dict.items():
            new_values = [int(x) for x in v]
            both_values_dict[k] = new_values

        
        # print(state_percents)
        # us_values = series_dict.get('state').columns[5:]
        categories = [x.replace('_'," ").title() for x in categories]
        
        
        
        fig = graph_1_2(categories, state_vals, us_vals, jur, g_width, g_height)
        fig.update_yaxes(tickfont=get_base_text(axis_font_size))
        fig.update_layout(margin=dict(l=200, r=20, t=100, b=100))
        # save_to_folder(fig,filename,g_width,g_height,state)
        if settings.show_it:
            fig.show()
        if settings.save_it:
            save_to_folder(fig,filename,g_width,g_height,jur)
        if settings.just_one:
            break


    else:
        for k,x in series_dict.items():
            print('not good')
    # print(result['fy'].max())
    


# %% [markdown]
# ### 1.3 K-12 Enrollment, by Socioeconomic Status

# %%
#creates table 1.3 (example of 100% bar)
from graphs.viz_graphs_template import *
import plotly.graph_objects as go
import plotly.express as px

g_width,g_height = get_sizing('1.3')
axis_font_size = 45
# g_width = 2327
# g_height = 419
filename = f'1.3.png'
ses_data = data_pull.get_collected_data(metric = 'enr_ses')
ses_data.columns = [cleaning_col(x) for x in ses_data.columns]
# print(ses_data.to_string())
# data_pull.get_collected_data(get_sheets=True)

#graph settings
aspect_ratio = 7
# graph_h = 200
# graph_wd = graph_h*aspect_ratio

offset = 1500
multiplier = 1.5

#preset values before loop
categories = ['Economically Disadvantaged', 'Not Economically Disadvantaged']
us_values = ses_data[ses_data['state_abrv']=="US"]
# print('US only')
# print(us_values.to_string())

us_values = us_values.sort_values('year', ascending=False).reset_index(drop=True)
us_dict = us_values.to_dict(orient='records')[0]

# us_total
for jur in state_abbreviations_priority:
    if jur == 'US':
        continue
    # print(jur)
    state_name = state_ref_r.get(jur)
    #fetch for state
    result = ses_data[ses_data['state_abrv']==jur]
    result = result.loc[:,['state_abrv','year','percent_economically_disadvantaged']]
    
    # result = result[result['year']==result['year'].max()]
    res_dict = result.to_dict(orient='records')[0]
    # print(res_dict)
    # print(type(us_values))
    # print(us_values)
    dfs = {f'{jur}':result, "US":us_values}
    # concat_dfs = []

        
    fig = graph_1_3(res_dict, us_dict, jur, g_width, g_height)
    fig.update_yaxes(tickfont=get_base_text(axis_font_size))
    fig.update_layout(margin=dict(l=200, r=20, t=100, b=100))

    if settings.show_it:
        fig.show()
    if settings.save_it:
            save_to_folder(fig,filename,g_width,g_height,jur)
    if settings.just_one:
            break


# %%


# %% [markdown]
# ### 1.4: K-12 Enrollment, by Locale
# 

# %%
#creates table 1.4 (example of 100% bar)



g_width,g_height = get_sizing('1.4')
axis_font_size = 45
# g_width = 2327
# g_height = 419
filename = f'1.4.png'
locale_data = data_pull.clean_enroll_by_locale()
locale_columns = list(locale_data.columns)
# print(locale_columns)
locale_data.columns = [cleaning_col(x) for x in locale_data.columns]
filter_state = 'ID'

# print(locale_data.to_string())
# for row in locale_data.itertuples(index = True):
#     print(row)
# data_pull.get_collected_data(get_sheets=True)


#graph settings
aspect_ratio = 7

offset = 1500
multiplier = 1.5

#preset values before loop

us_values = locale_data[locale_data['state_abrv']=="US"]
# print('US only')
# print(us_values.to_string())

us_dict = us_values.to_dict(orient='records')[0]

# us_total
for jur in state_abbreviations_priority:
    if jur == 'US':
        continue
    if settings.just_one == True and filter_state != None:
          if jur != filter_state:
                continue
    # print(jur)
    state_name = state_ref_r.get(jur)
    #fetch for state
    result = locale_data[locale_data['state_abrv']==jur]
    
    
    # result = result[result['year']==result['year'].max()]
    res_dict = result.to_dict(orient='records')[0]
    # print(res_dict)
    # print(type(us_values))
    # print(us_values)
    dfs = {f'{jur}':result, "US":us_values}
    # concat_dfs = []

        
    fig = graph_1_4(res_dict, us_dict, jur, g_width, g_height)
    fig.update_yaxes(tickfont=get_base_text(axis_font_size))
    fig.update_layout(margin=dict(l=200, r=20, t=100, b=100))

    if settings.show_it:
        fig.show()
    if settings.save_it:
            save_to_folder(fig,filename,g_width,g_height,jur)
    if settings.just_one:
            break


# %% [markdown]
# ## Page 2

# %% [markdown]
# ### STATE ASSEMEMNT RESULTS

# %%
def reshape_education_data(df):
    """
    Reshapes education data from wide format to long format.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Input dataframe with education data in wide format
        
    Returns:
    --------
    pandas.DataFrame
        Reshaped dataframe with columns: state_abrv, 2025_available, year, grade, subject, value
    """
    
    # Create a list to store all rows
    rows = []
    
    # Define the column mapping for years and subjects
    # Columns 5-7: 4th grade Reading (2023, 2024, 2025)
    # Columns 8-10: 4th grade Math (2023, 2024, 2025)
    # Columns 11-13: 8th grade Reading (2023, 2024, 2025)
    # Columns 14-16: 8th grade Math (2023, 2024, 2025)
    
    col_mapping = [
        (5, '2023', '4th grade', 'Reading'),
        (6, '2024', '4th grade', 'Reading'),
        (7, '2025', '4th grade', 'Reading'),
        (8, '2023', '4th grade', 'Math'),
        (9, '2024', '4th grade', 'Math'),
        (10, '2025', '4th grade', 'Math'),
        (11, '2023', '8th grade', 'Reading'),
        (12, '2024', '8th grade', 'Reading'),
        (13, '2025', '8th grade', 'Reading'),
        (14, '2023', '8th grade', 'Math'),
        (15, '2024', '8th grade', 'Math'),
        (16, '2025', '8th grade', 'Math'),
    ]
    
    # Iterate through each state (starting from row 3)
    for i in range(3, len(df)):
        state = df.iloc[i, 1]
        unavailable_flag = df.iloc[i, 4]
        
        # Determine if 2025 data is available
        # If the flag is True, then 2025 is unavailable, otherwise it's available
        data_2025_available = 'No' if unavailable_flag == True or (pd.notna(unavailable_flag) and str(unavailable_flag).strip().lower() == 'true') else 'Yes'
        
        # Iterate through each column mapping
        for col_idx, year, grade, subject in col_mapping:
            value = df.iloc[i, col_idx]
            
            # Skip if value is NaN or 0 (which seems to indicate missing data in your dataset)
            if pd.notna(value) and value != 0:
                rows.append({
                    'state_abrv': state,
                    '2025_available': data_2025_available,
                    'year': year,
                    'grade': grade,
                    'subject': subject,
                    'value': value
                })
    
    # Create the final dataframe
    result_df = pd.DataFrame(rows)
    
    # Sort by state, grade, subject, and year for better organization
    result_df = result_df.sort_values(['state_abrv', 'grade', 'subject', 'year']).reset_index(drop=True)
    
    return result_df


# Example usage:
# result_df = reshape_education_data(df)
# print(result_df.head(20))
# print(f"\nTotal rows: {len(result_df)}")
# print(f"\nStates with 2025 data available: {result_df[result_df['2025_available'] == 'Yes']['state_abrv'].nunique()}")
# print(f"States with 2025 data unavailable: {result_df[result_df['2025_available'] == 'No']['state_abrv'].nunique()}")
# result_df.to_csv('education_data_long_format.csv', index=False)

# %%
# GRAPHS for STATE ASSESSMENT RESULTS
g_width,g_height = get_sizing('2')

axis_font_size = 50

# g_width = 1352
# g_height = 768

state_assess_res = data_pull.get_collected_data(metric='state_assess_prof', no_header=True)
state_assess_res = state_assess_res.iloc[:,:17]
# cols = list(state_assess_res.columns)
# state_assess_res.columns = ['priority']+ cols[1:]
state_assess_res = state_assess_res[state_assess_res[0]!='x']


state_assess_res = reshape_education_data(state_assess_res)
state_assess_res = state_assess_res.sort_values(by=['state_abrv'])
state_assess_res = state_assess_res.sort_values(by=['grade','year','subject'], ascending=False).reset_index(drop=True)
grades = sorted(get_col_uniq_vals(state_assess_res['grade']))

# for state in state_abbreviations_priority:
#     if state == 'US':
#         continue
#     results = state_assess_res[state_assess_res['state_abrv']==state]

#     for grade in grades:
#         print(grade)
#         grad_res = results[results['grade']==grade]
#         print(grad_res.to_string())
#         fig = graph_2_state_assess_graph(grad_res, state)
#         fig.show()
break_loop = False
for state in state_abbreviations_priority:
    if state == 'US':
        continue
    results = state_assess_res[state_assess_res['state_abrv']==state]

    for i,grade in enumerate(grades):
        print(grade)
        grad_res = results[results['grade']==grade]
        # Sort by year and subject to ensure consistent ordering
        grad_res = grad_res.sort_values(by=['year', 'subject']).reset_index(drop=True)
        print(grad_res.to_string())
        fig = graph_2_state_assess_graph(grad_res, state)
        fig.update_layout(
            width=g_width,
            height = g_height,
            xaxis = dict(tickfont=get_base_text(axis_font_size))
            )
        # fig.update_xaxes(
        #     tickvals=['2022-2023', '2023-2024', '2024-2025'],
        # )
                    

        fig.update_yaxes(
            visible=False)
        if settings.show_it:
            fig.show()
        if settings.save_it:
            save_to_folder(fig,f'2.{i+1}.png',g_width,g_height,state)
        if settings.just_one:
            break_loop=True
            break
    if break_loop == True:
        break
            

# %% [markdown]
# ## Page 3

# %% [markdown]
# ### NAEP

# %% [markdown]
# ### Overall Proficiency Rates

# %%
#GRAPHS
g_width,g_height = get_sizing('3')
axis_font_size = 50
# g_width = 1340
# g_height = 768


naep_prof = data_pull.get_naep_data_long()

us_only = naep_prof[naep_prof['state_abrv']=='US']



offset = 7.7
break_loop = False
for state in state_abbreviations_priority:
    if 'US' in state:
        continue
    result = naep_prof[naep_prof['state_abrv']==state]
    # print(result.to_string())
    graphs = result.loc[:,["grade", "subject"]]
    graphs = graphs.drop_duplicates(inplace=False).sort_values(by=['grade']).reset_index(drop=True)
    for row in graphs.itertuples():
        narrowed_results = result[(result['grade']==row.grade) & (result['subject']==row.subject)].sort_values(by='year').reset_index(drop = True)
        us_vals = us_only[(us_only['grade']==row.grade) & (us_only['subject']==row.subject)].sort_values(by='year').reset_index(drop = True)
        # print(us_vals)
        # print(narrowed_results.to_string())
        
        fig = graph_naep_overall(narrowed_results,us_vals,'at_or_above_proficient', offset)
        fig.update_layout(
            width=g_width,
            height = g_height,
            xaxis = dict(tickfont=get_base_text(axis_font_size))
            )
        # graph_naep_overall()
        if row.subject == 'reading':
            if row.grade == 4:
                graph_num = 1
            elif row.grade == 8:
                graph_num = 2

        if row.subject == 'math':
            if row.grade == 4:
                graph_num = 3
            elif row.grade == 8:
                graph_num = 4


            
        if settings.show_it:
            fig.show()
        if settings.save_it:
            save_to_folder(fig,f'3.{graph_num}.png',g_width,g_height,state)
        if settings.just_one:
            break_loop=True
            break
    if break_loop == True:
        break
            

# %% [markdown]
# ## Page 4

# %% [markdown]
# ### NAEP by region

# %%
#get the naep data
naep_df = data_pull.get_naep_data()
naep_df = naep_df[naep_df['state_abrv'].isnull()==False].sort_values(by='state_abrv').reset_index(drop=True)
print(naep_df.to_string())

# %%
print(state_abbreviations)
print(state_abbreviations_priority)

# %%
#region graphs dict setup
naep_data_dict = {}
for juri in state_abbreviations_priority+['US']:
    if juri == 'US':
        us_data = naep_df[naep_df['state_abrv']=="US"]
        naep_us_only = dict(tuple(us_data.groupby(['grade','subject'])))
        naep_data_dict[juri] = naep_us_only 
        # continue
    # print(juri)

    else:
        region_df = get_census_regions(juri)

        region_list = region_df['state_code'].to_list()
        region_data = naep_df[naep_df['state_abrv'].isin(region_list)]
    # print(region_data.to_string())

        # Split by state
        naep_by_grade_subject_df = dict(tuple(region_data.groupby(['grade','subject'])))
        naep_data_dict[juri] = naep_by_grade_subject_df
    # Access individual DataFrames
    
    # print(gr_4_math.to_string())
    # ak_df = dfs_by_state['AK']
    # for k,v in split_dfs.items():
    #     print(k,v)


# %%
naep_data_dict

# %%
#graphs set up
g_width,g_height = get_sizing('4')

# g_width = 668
# g_height = 621

# %% [markdown]
# ##### 4.1 NAEP Region_Grade 4 Reading
# 

# %%
# GRAPHS: 4th grade reading

num = 1
offset_m = 1.25
axis_font_size = 37

filename = f'4.1.png'
us_naep_proficiency = naep_data_dict.get('US')[4,'reading']
# us_naep_proficiency = us_naep_proficiency[us_naep_proficiency['state_abrv']=='US'].reset_index(drop=True)
print(us_naep_proficiency.to_string())
for juri,df in naep_data_dict.items():
    if juri == 'US':
        continue

    # print(juri)

    data_df = df[4,'reading'].sort_values(by='at_or_above_proficient', ascending=False)

    all_data = pd.concat([data_df,us_naep_proficiency]).reset_index(drop = True)
    all_data['color'] = all_data['state_abrv'].apply(lambda x: get_highlight_color(x, juri))
    
    print(all_data.to_string())

    fig = graph_4_regions(all_data, offset_m, g_width, g_height)
    fig.update_yaxes(
        tickfont=get_base_text(axis_font_size))

    
    if settings.show_it:
        fig.show()
    if settings.save_it:
        save_to_folder(fig,filename,g_width,g_height,juri)
    if settings.just_one:
        break


# %% [markdown]
# ##### 4.2 NAEP Region_Grade 4 Math 
# 

# %%
# GRAPHS:  4th grade math
filename = f'4.2.png'
num = 1
offset_m = 1.25


us_naep_proficiency = naep_data_dict.get('US')[4,'math']
# us_naep_proficiency = us_naep_proficiency[us_naep_proficiency['state_abrv']=='US'].reset_index(drop=True)
print(us_naep_proficiency.to_string())
for juri,df in naep_data_dict.items():
    if juri == 'US':
        continue

    # print(juri)

    data_df = df[4,'math'].sort_values(by='at_or_above_proficient', ascending=False)

    all_data = pd.concat([data_df,us_naep_proficiency]).reset_index(drop = True)
    all_data['color'] = all_data['state_abrv'].apply(lambda x: get_highlight_color(x, juri))
    
    print(all_data.to_string())

    fig = graph_4_regions(all_data,offset_m, g_width, g_height)
    fig.update_yaxes(
        tickfont=get_base_text(axis_font_size))
    if settings.show_it:
        fig.show()
    if settings.save_it:
        save_to_folder(fig,filename,g_width,g_height,juri)
    if settings.just_one:
        break
        

# %% [markdown]
# ##### 4.3 NAEP Region_Grade 8 Reading
# 

# %%
#  GRAPHS: 8th grade reading
filename = f'4.3.png'
num = 1
offset_m = 1.25

us_naep_proficiency = naep_data_dict.get('US')[8,'reading']
# us_naep_proficiency = us_naep_proficiency[us_naep_proficiency['state_abrv']=='US'].reset_index(drop=True)
print(us_naep_proficiency.to_string())
for juri,df in naep_data_dict.items():
    if juri == 'US':
        continue

    # print(juri)

    data_df = df[8,'reading'].sort_values(by='at_or_above_proficient', ascending=False)

    all_data = pd.concat([data_df,us_naep_proficiency]).reset_index(drop = True)
    all_data['color'] = all_data['state_abrv'].apply(lambda x: get_highlight_color(x, juri))
    
    print(all_data.to_string())

    fig = graph_4_regions(all_data, offset_m,g_width, g_height)
    fig.update_yaxes(
        tickfont=get_base_text(axis_font_size))

    if settings.show_it:
        fig.show()
    if settings.save_it:
        save_to_folder(fig,filename,g_width,g_height,juri)
    if settings.just_one:
        break


# %% [markdown]
# ##### 4.4 NAEP Region_Grade 8 Math
# 

# %%
#  GRAPHS: 8th grade math
filename = f'4.4.png'
num = 1
offset_m = 1.25

us_naep_proficiency = naep_data_dict.get('US')[8,'math']
# us_naep_proficiency = us_naep_proficiency[us_naep_proficiency['state_abrv']=='US'].reset_index(drop=True)
print(us_naep_proficiency.to_string())
for juri,df in naep_data_dict.items():
    if juri == 'US':
        continue

    # print(juri)

    data_df = df[8,'math'].sort_values(by='at_or_above_proficient', ascending=False)

    all_data = pd.concat([data_df,us_naep_proficiency]).reset_index(drop = True)
    all_data['color'] = all_data['state_abrv'].apply(lambda x: get_highlight_color(x, juri))
    
    print(all_data.to_string())

    fig = graph_4_regions(all_data, offset_m,g_width, g_height)
    fig.update_yaxes(
        tickfont=get_base_text(axis_font_size))

    if settings.show_it:
        fig.show()
    if settings.save_it:
        save_to_folder(fig,filename,g_width,g_height,juri)
    if settings.just_one:
        break



# %% [markdown]
# ### State Assessment rigor
# 

# %%
# data set up
state_cut_df = data_pull.get_naep_workbook_data(option='state cut')
state_cut_df = state_cut_df.iloc[4:,:].reset_index(drop=True)
state_cut_df.columns = state_cut_df.iloc[0,:]
state_cut_df = state_cut_df.iloc[1:,:].reset_index(drop=True)


# Rename first column to 'state'
state_cut_df.columns = ['state'] + list(state_cut_df.columns[1:])

# Melt the dataframe
result = []

for col in state_cut_df.columns[1:]:
    # Extract subject and year from column name
    parts = col.split()
    subject = parts[0]
    year = parts[1]
    
    # Create a temporary dataframe
    temp = state_cut_df[['state', col]].copy()
    temp.columns = ['state', 'value']
    temp['year'] = year
    temp['subject'] = subject
    
    result.append(temp)

# Concatenate all dataframes
final_df = pd.concat(result, ignore_index=True)

# Reorder columns
assess_rigor = final_df[['state', 'year', 'subject', 'value']]

# Replace em dashes and en dashes with NaN
assess_rigor['value'] = assess_rigor['value'].replace(['—', '–'], pd.NA)

# Convert value to numeric
assess_rigor['value'] = pd.to_numeric(assess_rigor['value'], errors='coerce')
assess_rigor['state_abrv'] = assess_rigor['state'].apply(get_state_abrv_from_lower)
popped = assess_rigor.pop('state_abrv')
assess_rigor.insert(0,'state_abrv', popped)

# print(assess_rigor.to_string())


# %%
# GRAPHS 
g_width,g_height = get_sizing('4.5')

axis_font_size = 45
# g_width = 1340
# g_height = 575
offset = 10
grade = 4
subjects = {'reading':'4.5.png','math':'4.6.png'}
break_loop = False
for state in state_abbreviations_priority:
    if state == 'US':
        continue
    for sub,filename in subjects.items():
        # filename_plus = f'{sub}{filename}'
        result = assess_rigor[(assess_rigor['state_abrv']==state) & (assess_rigor['subject']==subject)].reset_index(drop=True).sort_values(by=['state_abrv','year'])
        print(bordered(state))
        print(result.to_string())
        ymin = min(result['value'])-50

        fig = graph_state_cut(result, 'value', state, result['year'],g_width, g_height)
        fig.update_yaxes(
            showticklabels=False,  # Hide tick labels
            showgrid=False,        # Hide gridlines
            zeroline=False         # Hide zero line
        )
        fig.update_layout(
            xaxis=dict(
                showgrid=False, 
                showline=True, 
                linecolor=hunt_darkgray, 
                tickmode='array', 
                tickvals=result['year'],
                tickfont=get_base_text(axis_font_size)

            ),
            yaxis=dict(
                range=[ymin, 275],
                showgrid=False, 
                showline=False, 
                linecolor=hunt_darkgray,
                visible = True),
            width = g_width,
            height= g_height)
        
        text_y_positions = [float(x)-offset for x in result['value']]
        # Add text labels
        fig.add_trace(go.Scatter(
            x=result['year'].to_list(),
            y=text_y_positions,  # Use calculated positions
            mode='text',
            showlegend=False,
            text=result['value'].apply(lambda x: str(int(round(x))) if pd.notna(x) else ''),
            textfont=get_base_text(45, bold = True)
        ))
        if settings.show_it:
            fig.show()
        if settings.save_it:
            # save_to_folder(fig,filename,g_width,g_height,juri)
            save_to_folder(fig,filename,g_width,g_height,state)
        # fig.show()
        # break
        if settings.just_one:
            break_loop = True
            break
    if break_loop == True:
        break


# %% [markdown]
# ## Page 5

# %% [markdown]
# #### Proficiency %, by Race/Ethnicity
# 

# %%
longitudal_data = data_pull.get_naep_workbook_data()
longitudal_data = longitudal_data.drop(2, axis=1)

longitudal_data.columns = [str(x).strip().replace('-','').replace(' ','_').lower() for x in longitudal_data.iloc[2,:]]
longitudal_data = longitudal_data.iloc[3:,:].reset_index(drop=True)


longitudal_data['state_abrv'] = longitudal_data['state'].apply(get_state_abrv_from_lower)
popped_col = longitudal_data.pop('state_abrv')
longitudal_data.insert(0,'state_abrv', popped_col)
columns = []
data_cols = []
for col in longitudal_data.columns:
    if 'proficiency' in str(col):
        grade_match = re.search(r'grade_(\d)', str(col))
        # print(grade_match)
        grade = grade_match.group(1)
        subj = col.split('_')[-1]
        col_name = f'{grade}th_{subj}_prof'
        columns.append(col_name)
        data_cols.append(col_name)
    else:
        columns.append(col)

longitudal_data.columns = columns
print(longitudal_data.to_string())



# %%
#RE GRAPHS needs to be run for both subjects |scatter plot|
g_width,g_height = get_sizing('5')
g_width,g_height = get_sizing('5')
# g_width = 1142
# g_height = 541
#math or reading
subject = 'reading'
axis_font_size = 45



subjects = {'reading':'5.1.png','math':'5.2.png'}
break_loop = False
long_dat_dict = {}
for i,jur in enumerate(state_abbreviations_priority):
    if jur == "US":
        continue
    print(jur)
    # if i>10:
    #     break
    for sub,filename in subjects.items():
        result = longitudal_data[(longitudal_data['state_abrv']==jur)&(longitudal_data['year']>=2011)].reset_index(drop=True)
        # print(result.to_string())
        # print(result[result['subgroup']=='Two or more races'].to_string())
        # for year in result['year']:
        #     print(type(year))
        years = sorted(get_col_uniq_vals(result['year']))
        values = sorted(result['year'])
        # x_range = [2011,2025]
        fig = graph_5_multi_series(result,f'4th_{sub}_prof','subgroup',years)
        
        fig.update_layout(
            width=g_width,
            height = g_height, 
            xaxis = dict(tickfont=get_base_text(axis_font_size)),
            margin = dict(l=10,t=10,r=10,b=10)
            # showlegend = True
        )
        fig.update_yaxes(visible = False)
        # full_filename = f'{sub}{filename}'
        # save_to_folder(fig,filename,g_width,g_height,jur)
        if settings.show_it:
            fig.show()
            
        if settings.save_it:
            save_to_folder(fig,filename,g_width,g_height,jur)
        if settings.just_one:
                break_loop  = True
                break
        # fig.show()o
    if break_loop == True:
        break
    

# %% [markdown]
# ### Subgroup: Free/Reduced Lunch Elgibility (FRL)
# table: 
# NAEP Proficiency Rates by Free/Reduced Lunch | Grades 4 | 2009 - 2022
# 
# description:
# The following graphs outline a breakdown of the percentage of students considered Proficient or better by Free/Reduced Lunch eligibility
# 
# 

# %%
frl_long_data = data_pull.get_naep_workbook_data(option='frl')
frl_long_data = frl_long_data.drop(3, axis=1)

frl_long_data.columns = [str(x).strip().replace('-','').replace(' ','_').lower() for x in frl_long_data.iloc[2,:]]
frl_long_data = frl_long_data.iloc[3:,:].reset_index(drop=True)


frl_long_data['state_abrv'] = frl_long_data['state'].apply(get_state_abrv_from_lower)
popped_col = frl_long_data.pop('state_abrv')
frl_long_data.insert(0,'state_abrv', popped_col)

frl_long_data.columns = ['state_abrv','year','state','eligibility','math_prof','reading_prof']
frl_long_data = frl_long_data[~frl_long_data['eligibility'].str.contains('information', case=False)]

# print(frl_long_data.to_string())


# %%
#FRL GRAPHS |scatter plot|
g_width,g_height = get_sizing('5.3')
# g_width = 1142
# g_height = 541
#math or reading

axis_font_size = 45
subjects = {'reading':'5.3.png','math':'5.4.png'}
break_loop = False
frl_long_dat_dict = {}
for i,jur in enumerate(state_abbreviations_priority):
    if jur == "US":
        continue

    for sub, filename in subjects.items():
        result = frl_long_data[(frl_long_data['state_abrv']==jur)&(frl_long_data['year']>=2011)].reset_index(drop=True)
        # print(result.to_string())
        # for year in result['year']:
        #     print(type(year))
        years = sorted(get_col_uniq_vals(result['year']))
        values = sorted(result['year'])
        # x_range = [2011,2025]
        fig = graph_5_multi_series(result,f'{sub}_prof','eligibility',years, label_all=True)
        
        fig.update_layout(
            width=g_width,
            height = g_height, 
            xaxis=dict(tickfont = get_base_text(axis_font_size)))
        fig.update_yaxes(
            range=[-10, 80],
            tickvals=list(range(0, 90, 10)),
            ticksuffix='%',
            showgrid=False,
            showline=True,
            linecolor='black',
            visible = False
        )
        
        if settings.show_it:
            fig.show()
            if settings.just_one:
                break_loop = True
                break
        if settings.save_it:
            save_to_folder(fig,filename,g_width,g_height,jur)
    if break_loop == True:
        break


# %% [markdown]
# ### Subgroup: English Language Learners (ELL)
# 
# table: 
# NAEP Proficiency Rates for English Language Learners | Grades 4 | 2010 - 2024
# 
# description:
# The following graphs outline a breakdown of the percentage of students considered Proficient or better English Language Learners status
# 
# 

# %%
ell_long_data = data_pull.get_naep_workbook_data(option='ell')
# ell_long_data = ell_long_data.drop(3, axis=1)

ell_long_data.columns = [str(x).strip().replace('-','').replace(' ','_').replace('/jurisdiction','').lower() for x in ell_long_data.iloc[2,:]]
ell_long_data = ell_long_data.iloc[3:,:].reset_index(drop=True)


ell_long_data['state_abrv'] = ell_long_data['state/jurisdiction'].apply(get_state_abrv_from_lower)
popped_col = ell_long_data.pop('state_abrv')
ell_long_data.insert(0,'state_abrv', popped_col)

ell_long_data.columns = ['state_abrv','year','state','ell_status','math_prof','reading_prof']
ell_long_data = ell_long_data[~ell_long_data['ell_status'].str.contains('information', case=False)]
print(ell_long_data.to_string())



# %%
# ELL GRAPHS |scatter plot|
#math or reading
# subject="math"
# filename = f'5.4.png'

g_width,g_height = get_sizing('5.3')
axis_font_size = 45

# g_width = 1142
# g_height = 541
subjects = {'reading':'5.5.png','math':'5.6.png'}

ell_long_dat_dict = {}
for i, jur in enumerate(state_abbreviations_priority):
    if jur == "US":
        continue

    for sub, filename in subjects.items():
        result = ell_long_data[(ell_long_data['state_abrv']==jur) & (ell_long_data['year']>=2011)].reset_index(drop=True)
        years = sorted(get_col_uniq_vals(result['year']))
        
        fig = graph_5_multi_series(result, f'{sub}_prof', 'ell_status', years, label_all=True)
        
        fig.update_layout(
            width=g_width,
            height=g_height,
            xaxis=dict(tickfont = get_base_text(axis_font_size))
        )
        
        # Override yaxis separately
        fig.update_yaxes(
            range=[-10, 80],
            tickvals=list(range(0, 90, 10)),
            ticksuffix='%',
            showgrid=False,
            showline=True,
            linecolor='black',
            visible = False
        )
        
        if settings.show_it:
            fig.show()
            if settings.just_one:
                break_loop = True
                break
        if settings.save_it:
            save_to_folder(fig,filename,g_width,g_height,jur)

    if break_loop == True:
        break

    

# %% [markdown]
# ### Subgroup: Disability Status (SWD)
# 
# table: 
# NAEP Proficiency Rates for Students with Disabilities | Grades 4 | 2010 - 2024
# 
# description:
# The following graphs outline a breakdown of the percentage of students considered Proficient or better by disability status
# 

# %%
swd_long_data = data_pull.get_naep_workbook_data(option='swd')
# swd_long_data = swd_long_data.drop(3, axis=1)

swd_long_data.columns = [str(x).strip().replace('-','').replace(' ','_').replace('/jurisdiction','').lower() for x in swd_long_data.iloc[2,:]]
swd_long_data = swd_long_data.iloc[3:,:].reset_index(drop=True)


swd_long_data['state_abrv'] = swd_long_data['state/jurisdiction'].apply(get_state_abrv_from_lower)
popped_col = swd_long_data.pop('state_abrv')
swd_long_data.insert(0,'state_abrv', popped_col)

swd_long_data.columns = ['state_abrv','year','state','ell_status','math_prof','reading_prof']
swd_long_data = swd_long_data[~swd_long_data['ell_status'].str.contains('information', case=False)]
print(swd_long_data.to_string())



# %%
#SWD GRAPHS |scatter plot|

g_width,g_height = get_sizing('5.7')

# g_width = 1142
# g_height = 541
#math or reading
axis_font_size = 45

subjects = {'reading':'5.7.png','math':'5.8.png'}
break_loop = False
swd_long_dat_dict = {}
for i,jur in enumerate(state_abbreviations_priority):
    if jur == "US":
        continue

    for sub,filename in subjects.items():
        
        result = swd_long_data[(swd_long_data['state_abrv']==jur)&(swd_long_data['year']>=2011)].reset_index(drop=True)
        # print(result.to_string())
        # for year in result['year']:
        #     print(type(year))
        years = sorted(get_col_uniq_vals(result['year']))
        values = sorted(result['year'])
        # x_range = [2011,2025]
        fig = graph_5_multi_series(result,f'{sub}_prof','ell_status',years, label_all=True)
        fig.update_layout(
                width=g_width,
                height=g_height,
                xaxis=dict(tickfont = get_base_text(axis_font_size))# font=get_base_text(axis_font_size)
            )
            
        # Override yaxis separately to ensure it takes effect
        fig.update_yaxes(
            range=[-10, 80],
            tickvals=list(range(0, 90, 10)),
            ticksuffix='%',
            showgrid=False,
            showline=True,
            linecolor='black',
            visible = False
    
        )
        if settings.show_it:
            fig.show()
            if settings.just_one:
                break_loop = True
                break
        if settings.save_it:
            save_to_folder(fig,filename,g_width,g_height,jur)

    if break_loop == True:
        break

# %% [markdown]
# ## Page 6

# %% [markdown]
# ### chronic absenteesism (Race)

# %%
# set up
chron_abs_df = data_pull.get_collected_data(metric='chron_abs_race', no_header = True)
chron_abs_df = chron_abs_df.iloc[1:, 0:11]
chron_abs_df = chron_abs_df.drop(columns=chron_abs_df.columns[1:4])

# print(chron_abs_df.to_string())

# Set proper column names
chron_abs_df.columns = [
    'state_abrv', 'year', 'White', 'Black', 'Hispanic', 'Asian',
    'American Indian/Alaska Native', 'Native Hawaiian/Other Pacific Islander'
]

# Clean year column to pick later year if range
def extract_later_year(val):
    if pd.isna(val):
        return np.nan
    years = re.findall(r'\d{4}', str(val))
    return int(years[-1]) if years else np.nan

chron_abs_df['year'] = chron_abs_df['year'].apply(extract_later_year)

# Melt into long format
df_long = chron_abs_df.melt(
    id_vars=['state_abrv', 'year'],
    var_name='group',
    value_name='value'
)

# Normalize values to percentages
def normalize_percentage(x):
    try:
        x = float(str(x).replace('%','').replace('%%',''))  # remove stray % symbols
        if x > 1.5:  # likely already in percent form
            return x
        else:        # decimal → percent
            return x * 100
    except:
        return np.nan

df_long['value'] = df_long['value'].apply(normalize_percentage)

# Optional: sort for readability
chron_abs_df = df_long.sort_values(['state_abrv', 'group']).reset_index(drop=True)

# Preview
print(chron_abs_df.to_string())


# %%
# GRAPHS chronic absenteeism |bar vertical|
# g_width = 2703
# g_height = 628
g_width,g_height = get_sizing('6.1')
axis_font_size = 45
offset = 1
filename = f'6.1.png'
for state in state_abbreviations_priority:
    if state == 'US':
        continue
    result = chron_abs_df[chron_abs_df['state_abrv']==state].reset_index(drop=True)
    # print(result.to_string())
    fig = graph_chron_abs(result, 'value', g_width, g_height)
    fig.update_layout(
        xaxis=dict(tickfont=get_base_text(axis_font_size))
    )
    fig.update_yaxes(
        visible=False
    )
    if settings.show_it:
        fig.show()
        if settings.just_one:
            break
    if settings.save_it:
        save_to_folder(fig,filename,g_width,g_height,state)

    


# %% [markdown]
# ### chronic absenteesism (Other Subgroup)

# %%
# chronic absenteesism other
chron_abs_df_other = data_pull.get_collected_data(metric='chron_abs_other', no_header = True)
chron_abs_df_other = chron_abs_df_other.drop(columns=chron_abs_df_other.columns[1:6])

chron_abs_df_other.columns = ['state', 'year']+list(chron_abs_df_other.iloc[1,2:])
chron_abs_df_other = chron_abs_df_other.iloc[2:, :].reset_index(drop=True)
chron_abs_df_other = chron_abs_df_other.drop(columns=['notes', 'date pulled'])
print(chron_abs_df_other.columns)
# print(chron_abs_df_other.to_string())


# %%
# GRAPHS chronic absenteeism other |bar vertical|
g_width,g_height = get_sizing('6.2')
axis_font_size = 45
filename = '6.2.png'
for state in state_abbreviations_priority:
    result = chron_abs_df_other[chron_abs_df_other['state']==state].reset_index()
    print(result.to_string())
    fig = graph_other_chron_abs(result)
    fig.update_layout(
        width=g_width,
        height=g_height,
        font=get_base_text(axis_font_size)
    )
    fig.update_yaxes(
        visible=False
    )
    if settings.show_it:
        fig.show()
        if settings.just_one:
            break
    if settings.save_it:
        save_to_folder(fig,filename,g_width,g_height,state)

# %%
#out of school suspension
oos_df = data_pull.get_collected_data(metric='suspension_race', no_header = True)
oos_df.columns = list(oos_df.iloc[1,:])
oos_df = oos_df.iloc[2:,:].reset_index(drop=True)


oos_df = oos_df.drop(columns=oos_df.columns[[1,9,10,11]])
print(oos_df.columns)


# %%
# GRAPHS out of school suspension |bar vertical|
g_width,g_height = get_sizing('6.3')

filename = '6.3.png'
axis_font_size = 50

us_only = oos_df[oos_df['state']=="US"].reset_index(drop=True)

for state in state_abbreviations_priority:
    result = oos_df[oos_df['state']==state].reset_index(drop = True)
    print(list(result.columns))
    print(result.to_string())
    print(us_only.to_string())
    fig = graph_oos(result, us_only, state, g_width,g_height)
    fig.update_layout(
        width=g_width,
        height=g_height,
        xaxis=dict(tickfont=get_base_text(axis_font_size)),
        margin = dict(l=0,t=10,r=0,b=0)
                   
    )
    fig.update_yaxes(
        visible=False
    )
    if settings.show_it:
        fig.show()
        
    if settings.save_it:
        save_to_folder(fig,filename,g_width,g_height,state)
    if settings.just_one:
        break


# oos_df.columns = ['state', 'year']+list(oos_df.iloc[1,2:])
# oos_df = oos_df.iloc[2:, :].reset_index(drop=True)
# oos_df = oos_df.drop(columns=['notes', 'date pulled'])
# print(oos_df.columns)


# %% [markdown]
# ## Page 7

# %% [markdown]
# ### Public HS Graduation Rate

# %%
grad_rate_df = data_pull.get_collected_data(metric='hs_grad_rate')
grad_rate_df.columns = grad_rate_df.iloc[0,:].reset_index(drop=True)
grad_rate_df = grad_rate_df.iloc[2:,:].reset_index(drop=True)
grad_rate_df = grad_rate_df.loc[:,['state', '2022-2023 data', '2023-2024 HS grad rate']]
grad_rate_df.columns = ['state_abrv', '2023', '2024']
grad_rate_df = grad_rate_df.dropna(how='all')


# Melt the DataFrame to long format
grad_rate_df = grad_rate_df.melt(id_vars=['state_abrv'], 
                    var_name='year', 
                    value_name='grad_rate')

# Convert 'year' to int and 'grad_rate' to float
grad_rate_df['year'] = pd.to_numeric(grad_rate_df['year'], errors='coerce')
grad_rate_df['grad_rate'] = pd.to_numeric(grad_rate_df['grad_rate'], errors='coerce')
grad_rate_df = grad_rate_df.sort_values(by=['state_abrv','year']).reset_index(drop=True)
# print(grad_rate_df.to_string())

ref = data_pull.get_collected_data(metric='hs_grad_rate (ref)')
ref = ref.iloc[:,:14]
ref.columns = ['state', 'state_abrv']+ [x.split('-')[-1].strip() for x in ref.columns[2:]]
# print(ref.to_string())

# Assuming you already have the original wide-format DataFrame called `ref`
# First, replace '---' strings with NaN and ensure all values from 2011-2023 are numeric
ref.replace('---', pd.NA, inplace=True)

# Convert all year columns to numeric (safe conversion)
for year in ref.columns[2:]:
    ref[year] = pd.to_numeric(ref[year], errors='coerce')

# Now melt the DataFrame from wide to long format
ref_long = ref.melt(id_vars=['state', 'state_abrv'], 
                  var_name='year', 
                  value_name='grad_rate')

# Optional: Convert 'year' column to int (if all values are valid years)
ref_long['year'] = pd.to_numeric(ref_long['year'], errors='coerce')

# Sort and reset index for cleaner output
ref_long = ref_long.loc[:,["state_abrv", "year", "grad_rate"]]
ref_long = ref_long.sort_values(by=['state_abrv', 'year']).reset_index(drop=True)

print(ref_long.to_string())


# %%
full_grad_rate_df = pd.concat([grad_rate_df,ref_long]).sort_values(by=['state_abrv','year']).reset_index(drop=True)
# print(full_grad_rate_df.to_string())

# %%
# GRAPHS overall grad rate |scatter plot|
g_width,g_height = get_sizing('7.1')

us_only = full_grad_rate_df[full_grad_rate_df['state_abrv']=='US'].reset_index(drop=True)
offset = 1
axis_font_size = 60

filename = f'7.1.png'
for state in state_abbreviations_priority:
    if state == 'US':
        continue
    result = full_grad_rate_df[full_grad_rate_df['state_abrv']==state].reset_index(drop=True)
    print(result.to_string())
    fig = graph_grad_rate(result,us_only, 'grad_rate', state, get_col_uniq_vals(result['year']), offset, g_width, g_height)
    fig.update_layout(
        width=g_width,
        height=g_height,
        xaxis = dict(tickfont=get_base_text(axis_font_size)),
        yaxis = dict(
            visible = False
        )
    )

    if settings.show_it:
        fig.show()
        if settings.just_one:
            break
    if settings.save_it:
        save_to_folder(fig,filename,g_width,g_height,state)

    # save_to_folder(fig,filename,g_width,g_height,state)
    # fig.show()
    # break
    


# %%
# GRAPHS Grad Rate By Race and Ethnicity |bar vertical|

g_width,g_height = get_sizing('7.2')

filename = f'7.2.png'
grad_rate_by_re = data_pull.get_collected_data(metric='hs_grad_rate_subgroups')
# print(grad_rate_by_re.to_string())
axis_font_size = 50

# grad_rate_by_re.columns = ['state_abrv','priority','total', including]

import pandas as pd
# Assuming your DataFrame is called df3
# Example cleanup before melting
grad_rate_by_re = grad_rate_by_re.dropna(subset=['state_abrv', 'updated year'])  # Drop rows missing essential data

# List of columns that contain graduation rate values by group
group_columns = [
    'Total',
    'American Indian / Alaska Native',
    'Asian/Pacific Islander',
    'Hispanic',
    'Black',
    'White',
    'Two or more races'
]

# Melt to long format
grad_rate_by_re = grad_rate_by_re.melt(
    id_vars=['state_abrv', 'updated year'],
    value_vars=group_columns,
    var_name='group',
    value_name='grad_rate'
)
grad_rate_by_re['group'] = grad_rate_by_re['group'].replace({
    'Two or more races': 'Two or More'
})

# Rename for consistency
grad_rate_by_re.rename(columns={'updated year': 'year'}, inplace=True)

# # Drop rows without graduation rate values
# grad_rate_by_re = grad_rate_by_re.dropna(subset=['grad_rate'])

# Optional: convert year to int and grad_rate to float
grad_rate_by_re['year'] = pd.to_numeric(grad_rate_by_re['year'], errors='coerce').astype('Int64')
grad_rate_by_re['grad_rate'] = pd.to_numeric(grad_rate_by_re['grad_rate'], errors='coerce')

# Reset index
grad_rate_by_re = grad_rate_by_re[grad_rate_by_re['state_abrv']!='x'].reset_index(drop=True)

# Preview result
# print(grad_rate_by_re.to_string())

us_only = grad_rate_by_re[grad_rate_by_re['state_abrv']=='US'].reset_index(drop=True)
print(us_only.to_string())
for state in state_abbreviations_priority:
    if state == 'US':
        continue
    result = grad_rate_by_re[grad_rate_by_re['state_abrv']==state].reset_index(drop=True)
    print(result.to_string())
    fig = graph_gradrate_re(result, us_only, state)
    fig.update_layout(
        width=g_width,
        height=g_height
        )
    fig.update_xaxes(
           visible=False,
           tickfont=get_base_text(axis_font_size)
        )
    

    if settings.show_it:
        fig.show()
        if settings.just_one:
            break
    if settings.save_it:
        save_to_folder(fig,filename,g_width,g_height,state)





# %%
# GRAPHS Grad Rate By Other Subgroups |bar vertical|
g_width,g_height = get_sizing('7.3')

axis_font_size = 55

filename = f'7.3.png'

grad_rate_by_re = data_pull.get_collected_data(metric='hs_grad_rate_subgroups')
# print(grad_rate_by_re.to_string())

# grad_rate_by_re.columns = ['state_abrv','priority','total', including]

import pandas as pd

# Assuming your DataFrame is called df3
# Example cleanup before melting
grad_rate_by_re = grad_rate_by_re.dropna(subset=['state_abrv', 'updated year'])  # Drop rows missing essential data

# List of columns that contain graduation rate values by group
group_columns = [
    'Economically disadvantaged (Based on state definition)',
    'Limited English proficiency',
    'Students with disabilities'
]


# Melt to long format
grad_rate_by_re = grad_rate_by_re.melt(
    id_vars=['state_abrv', 'updated year'],
    value_vars=group_columns,
    var_name='group',
    value_name='grad_rate'
)
grad_rate_by_re['group'] = grad_rate_by_re['group'].replace({
    'Two or more races': 'Two or More'
})


# Rename for consistency
grad_rate_by_re.rename(columns={'updated year': 'year'}, inplace=True)

# # Drop rows without graduation rate values
# grad_rate_by_re = grad_rate_by_re.dropna(subset=['grad_rate'])

# Optional: convert year to int and grad_rate to float
grad_rate_by_re['year'] = pd.to_numeric(grad_rate_by_re['year'], errors='coerce').astype('Int64')
grad_rate_by_re['grad_rate'] = pd.to_numeric(grad_rate_by_re['grad_rate'], errors='coerce')

# Reset index
grad_rate_by_re = grad_rate_by_re[grad_rate_by_re['state_abrv']!='x'].reset_index(drop=True)

# Preview result
# print(grad_rate_by_re.to_string())

us_only = grad_rate_by_re[grad_rate_by_re['state_abrv']=='US'].reset_index(drop=True)
# print(us_only.to_string())
for state in state_abbreviations_priority:
    if state == 'US':
        continue
    result = grad_rate_by_re[grad_rate_by_re['state_abrv']==state].reset_index(drop=True)
    # print(result.to_string())
    fig = graph_gradrate_other_subgroup(group_columns,result, us_only, state)
    
    fig.update_layout(
        width=g_width,
        height=g_height,
        yaxis=dict(tickfont=get_base_text(axis_font_size))
    )
    
    fig.update_yaxes(
           visible=False
        )

    if settings.show_it:
        fig.show()
        if settings.just_one:
            break
    if settings.save_it:
        save_to_folder(fig,filename,g_width,g_height,state)







# %% [markdown]
# ## Page 8

# %% [markdown]
# ### 8.1: Dropout Rate

# %%
dropout_df = data_pull.get_collected_data(metric = 'dropout_rate')
dropout_df = dropout_df.iloc[:,:11]
print(dropout_df.to_string(max_colwidth=30))


# Step 1: Rename columns properly
dropout_df.columns = [
    'state_abrv', 'priority', 'source', 'updated_year', 'Total',
    'White', 'Black', 'Hispanic', 'Asian/Pacific Islander',
    'American Indian/Alaska Native', 'Two or more races'
]

# Step 2: Keep only rows where state_abrv is not NaN or 'x'
df_clean = dropout_df[~dropout_df['state_abrv'].isna()]
df_clean = df_clean[df_clean['state_abrv'] != 'x']

# Step 3: Select columns of interest
group_columns = [
    'Total', 'White', 'Black', 'Hispanic', 'Asian/Pacific Islander',
    'American Indian/Alaska Native', 'Two or more races'
]
df_clean = df_clean[['state_abrv', 'updated_year'] + group_columns]

# Step 4: Convert updated_year to a single year (pick later if range)
def extract_later_year(val):
    if pd.isna(val):
        return np.nan
    # Match years in format "YYYY" or "YYYY-YYYY"
    years = re.findall(r'\d{4}', str(val))
    if not years:
        return np.nan
    return int(years[-1])  # pick the later year

df_clean['updated_year'] = df_clean['updated_year'].apply(extract_later_year)

# Step 5: Melt to long format
df_long = df_clean.melt(
    id_vars=['state_abrv', 'updated_year'],
    value_vars=group_columns,
    var_name='group',
    value_name='value'
)

# Step 6: Convert values to float and standardize percentages
def normalize_percentage(x):
    try:
        x = float(x)
        if x > 1.5:  # Likely stored as 35.1 → treat as 35.1%
            return x
        else:        # Already decimal (0.351 → 35.1%)
            return x * 100
    except:
        return np.nan

df_long['value'] = df_long['value'].apply(normalize_percentage)

# Step 7: Rename column
df_long.rename(columns={'updated_year': 'year'}, inplace=True)

# Optional: sort for readability
dropout_df = df_long.sort_values(['state_abrv', 'group']).reset_index(drop=True)




# %%
# GRAPHS Dropout rate by Race and Ethnicity
g_width,g_height = get_sizing('8.1')
axis_font_size = 50

filename = f'8.1.png'
# Reset index

# Preview result
# print(grad_rate_by_re.to_string())

us_only = dropout_df[dropout_df['state_abrv']=='US'].reset_index(drop=True)
print(us_only.to_string())
for state in state_abbreviations_priority:
    if state == 'US':
        continue
    result = dropout_df[dropout_df['state_abrv']==state].reset_index(drop=True)
    print(result.to_string())
    fig = graph_dropouts(result, us_only, state)
    fig.update_layout(
        width=g_width,
        height=g_height,
        xaxis=dict(tickfont=get_base_text(axis_font_size)))
    
    fig.update_yaxes(
           visible=False)
    if settings.show_it:
        fig.show()
        if settings.just_one:
            break
    if settings.save_it:
        save_to_folder(fig,filename,g_width,g_height,state)


# %% [markdown]
# ### 8.2: CTE concentratos

# %%
# GRAPHS
cte_df = data_pull.cte_calculated()
# print(cte_df.to_string())
axis_font_size = 50

# GRAPHS Grad Rate By Race and Ethnicity
g_width,g_height = get_sizing('8.2')

filename = f'8.2.png'
grad_rate_by_re = data_pull.get_collected_data(metric='hs_grad_rate_subgroups')

for state in state_abbreviations_priority:
    
    if state == 'US':
        continue
    fig = graph_8_cte(cte_df,state)
    fig.update_yaxes(
        visible=False
    )
    fig.update_layout(
    width=g_width,
    height=g_height,
        xaxis=dict(tickfont=get_base_text(axis_font_size))
    )
    if settings.show_it:
        fig.show()
        if settings.just_one:
            break
    if settings.save_it:
        save_to_folder(fig,filename,g_width,g_height,state)



# %% [markdown]
# ### AP graphs 
# 

# %%
# GRAPHS participation

sat_df = data_pull.get_sat_graph_data()
# print(sat_df.to_string())
g_width,g_height = get_sizing('8.3')
axis_font_size = 45

filename = f'8.3.png'

for state in state_abbreviations_priority:
    if state =="US":
        continue
    us_only = sat_df[sat_df['state_abrv']=="US"]['perc_in_an_ap'].to_list()
    state_only = sat_df[sat_df['state_abrv']==state]['perc_in_an_ap'].to_list()

    print(us_only)
    print(state_only)
    
    fig = graph_ap(us_only[0],state_only[0],state, 'percent')
    fig.update_layout(
        
        width=g_width,
        height=g_height,
        margin = dict(l=0,t=10,b=0,r=0),

        xaxis=dict(tickfont=get_base_text(axis_font_size),
                   title = dict(
                       text = wrap_category_name('% of 11TH GRADERS ENROLLED IN AT LEAST ONE AP COURSE', 37),
                       font = get_base_text(40),
                    standoff=60)))
    
    fig.update_yaxes(
           visible=False
        )
    
    if settings.show_it:
        fig.show()
    if settings.save_it:
        save_to_folder(fig,filename,g_width,g_height,state)
    if settings.just_one:
        break


    # break


# %%
# GRAPHS num ap exams per 1000
sat_df = data_pull.get_sat_graph_data()
# print(sat_df.to_string())
g_width,g_height = get_sizing('8.4')
filename = f'8.4.png'
axis_font_size = 45


for state in state_abbreviations_priority:
    if state =="US":
        continue
    us_only = sat_df[sat_df['state_abrv']=="US"]['ap_exams_per_k_11_12'].to_list()
    state_only = sat_df[sat_df['state_abrv']==state]['ap_exams_per_k_11_12'].to_list()

    print(us_only)
    print(state_only)
    
    fig = graph_ap(us_only[0],state_only[0],state, 'number')
    fig.update_layout(
        width=g_width,
        height=g_height,
        margin = dict(l=0,t=10,b=0,r=0),
        
        xaxis=dict(tickfont=get_base_text(axis_font_size),
                   title = dict(
                       text = wrap_category_name('# of AP EXAMS PER 1,000 11TH-12TH GRADERS', 37),
                       font = get_base_text(40),
                    standoff=60)))
    
    fig.update_yaxes(
           visible=False
        )

    if settings.show_it:
        fig.show()
    if settings.save_it:
        save_to_folder(fig,filename,g_width,g_height,state)
    if settings.just_one:
        break

    # break


# %%
#GRAPHS Percent passing
sat_df = data_pull.get_sat_graph_data()
# print(sat_df.to_string())
g_width,g_height = get_sizing('8.5')
filename = f'8.5.png'
axis_font_size = 45


for state in state_abbreviations_priority:
    if state =="US":
        continue
    us_only = sat_df[sat_df['state_abrv']=="US"]['perc_3_orbetter'].to_list()
    state_only = sat_df[sat_df['state_abrv']==state]['perc_3_orbetter'].to_list()

    print(us_only)
    print(state_only)
    
    fig = graph_ap(us_only[0],state_only[0],state, 'percent')
    
    fig.update_layout(
        width=g_width,
        height=g_height,
        margin = dict(l=0,t=10,b=0,r=0),

        xaxis=dict(tickfont=get_base_text(axis_font_size),
            title = dict(
                text = wrap_category_name('% of AP EXAMS WITH PASSING GRADES', 37),
                font = get_base_text(40),
            standoff=60)))

    fig.update_yaxes(
           visible=False
        )
    

    if settings.show_it:
        fig.show()
    if settings.save_it:
        print(g_width,g_height)
        save_to_folder(fig,filename,g_width,g_height,state)
    if settings.just_one:
        break


# %% [markdown]
# ## Page 9

# %%
# College Entrance Exams

g_width,g_height = get_sizing('9.1')

filename = f'9.1.png'
axis_font_size = 45

#data set up
act_df = data_pull.get_collected_data(metric='act_benchmarks', no_header=True)
act_df = act_df.iloc[1:,1:].reset_index(drop = True)
act_df.columns = act_df.iloc[0,:]

act_df = act_df.iloc[1:,:].reset_index(drop=True)
# print(act_df.to_string())


us_only = act_df[act_df['State']=='US']
print(us_only.to_string())
for state in state_abbreviations_priority:
    result = act_df[act_df['State']==state]
    # print(result.to_string())
    fig = graph_act_benchmarks(result, us_only, state, g_width, g_height)
    fig.update_yaxes(
        visible=False
    )
    fig.update_layout(
    width=g_width,
    height=g_height,
        xaxis=dict(tickfont=get_base_text(axis_font_size)))

    if settings.show_it:
        fig.show()
        if settings.just_one:
            break
    if settings.save_it:
        save_to_folder(fig,filename,g_width,g_height,state)
    




