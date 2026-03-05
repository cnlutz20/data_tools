# %%
import os, sys, json, datetime, re  # Provides OS-dependent functionality, system-specific parameters, JSON handling, and date/time manipulation
import pandas as pd             # Provides data structures and data analysis tools
import numpy as np              # Supports large, multi-dimensional arrays and matrices
import requests
import time
from tqdm import tqdm
import glob as glob
import tabula



#thi data contants
from cprl_functions.defined_functions import *
from cprl_functions.state_capture import *
from cprl_functions.text_printing import bordered
from cprl_functions.data_packet_defs import *

sat_files = r'C:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data\Data Packets\K-12\data\college board\sat\2025-sat-suite-state-reports'

import PyPDF2
import itertools
# Function to read a PDF file line by line
import PyPDF2
import itertools


def read_pdf_line_by_line(sat_files):
    # all_lines = kwargs.get('all_lines', False)
    # Open the PDF file for reading
    lines_by_state = {}
    for file_item in glob.glob(os.path.join(sat_files,'*')):
        #open file
        with open(file_item, 'rb') as file:
            filename = file.name.split('\\')[-1].replace('-',' ')
            
            #get state abbreviation
            for state in state_list_lower:
                if state in filename:
                    state_abrv = state_ref_lower.get(state)
            # filter pages
            reader = PyPDF2.PdfReader(file)
            pages_to_read = [3, 4]  # Pages 3 and 4 (0-indexed)
            lines_list = []
            
            #get lines from pages
            for i in pages_to_read:
                if i < 0 or i >= len(reader.pages):
                    continue
                page = reader.pages[i]
                text = page.extract_text()
                if not text:
                    continue
                lines = text.splitlines()
                lines_list.append(lines)
            
            # Flatten and clean lines - remove excessive whitespace
            all_lines = list(itertools.chain.from_iterable(lines_list))
            # Strip whitespace and remove empty lines
            all_lines = [line.strip().replace('\t',' ') for line in all_lines if line.strip()]
        lines_by_state[state_abrv] = all_lines
    return lines_by_state

# %% cell 
dfs = []
lines_by_state = read_pdf_line_by_line(sat_files)
for k,v in lines_by_state.items():
    # if k != 'KS':
        # continue
    print(bordered(k))
    avg = None
    percent = None
    vals = {}
    vals['state_abrv'] = [k]
    for i,element in enumerate(v):
        need = ['SAT','Participation',]
        exclude = ['Suite']

        if all(str(x) in str(element) for x in need) and not any(str(x) in str(element) for x in exclude) and re.search(r'(graduates)?', str(element)):

            print(element)
            
            value = re.search(r'\d{1,3}%',element)
            if value is None:
                continue
            else:
                percent = value.group(0)
                vals['percent'] = [percent]
                # print(value.group(0))
        if 'Total' in element and 'Mean' in element:
            # print(element)
            
            # print(v[i+2].split(' '))
            
            value_row = [x for x in v[i+2].split(' ') if len(x)>0]
            if len(value_row)<3:
                continue
                # print()
            
            print(value_row)
            avg = value_row[2]
            print(f'avg: {avg}')
            if int(avg)<800 or int(avg)>2500:
                print(f'something wrong with {k} avg')
            for val in value_row:
                try:
                    int(val)

                except:
                    continue
            vals['avg'] = [avg]
    
    
    
    df = pd.DataFrame(vals).reset_index(drop=True)
    dfs.append(df)

    
df = pd.DataFrame(vals)
all_sat_data = pd.concat(dfs).reset_index(drop=False)
print(all_sat_data.to_string())
# %%



# %%
def get_sat_data():
    return all_sat_data


if __name__ == "__main__":
   # stuff only to run when not called via 'import' here
    print('Ran in file')
    # print('nothing')


# %%
