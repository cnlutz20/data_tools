# %%
import pandas as pd
import numpy as np

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

# df_fixed = merge_split_state_names(df)
# print(df_fixed)

# %%
import tabula
import pandas as pd

def get_act_data():
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

