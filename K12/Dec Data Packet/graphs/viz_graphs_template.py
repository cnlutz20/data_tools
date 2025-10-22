"""
Data Visualization Graphs Template
Organized by graph type with consistent styling
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from pathlib import Path
from .brand_pallete import *
#thi data contants
from cprl_functions.defined_functions import *
from cprl_functions.state_capture import *
from cprl_functions.text_printing import bordered
from cprl_functions.data_packet_defs import *


# ============================================================================
# STYLING CONFIGURATION
# ============================================================================

PRIMARY_COLOR = hunt_darkgray

# Font configuration
FONT_FAMILY = 'Lato, sans-serif'
FONT_SIZE = 12

# Common layout template
def get_base_layout(width=500, height=500):
    return dict(
        font=dict(family=FONT_FAMILY, size=FONT_SIZE, color=hunt_darkgray),
        plot_bgcolor='white',
        paper_bgcolor='white',
        # title=dict(text=title, x=0.5, xanchor='center'),
        showlegend=False,
        width=width,
        height=height,
        margin=dict(l=80, r=20, t=40, b=60)
    )
def get_colors(categories=False, **kwargs):
    """
    Returns a list of colors for the provided categories.
    Uses r_and_e_colors dictionary for mapping. Provides a fallback color if no match.
    """
    colors = []
    options = kwargs.get('options', False)
    
    # Handle preset color options
    if options:
        if options == 'purple_dual':
            return [hunt_light_purple, hunt_purple]

    for c in categories:
        c_str = str(c).strip()
        app_color = None  # default in case nothing matches

        # Match categories in order of specificity
        if re.search(r'[Tt]wo|[Mm]ore', c_str):
            app_color = r_and_e_colors.get('two_or_more')
        elif re.search(r'[Aa]sian', c_str):
            app_color = r_and_e_colors.get('aapi')
    
        elif re.search(r'[Pp]acific|[Hh]awa', c_str):
            app_color = r_and_e_colors.get('pacific_islander')
        elif re.search(r'[Aa]merican [Ii]ndian|[Nn]ative', c_str):
            app_color = r_and_e_colors.get('native')
        elif re.search(r'[Ww]hite', c_str):
            app_color = r_and_e_colors.get('white')
        elif re.search(r'[Bb]lack', c_str):
            app_color = r_and_e_colors.get('black')
        elif re.search(r'[Hh]ispanic', c_str):
            app_color = r_and_e_colors.get('hispanic')
        # Generic 'Other' fallback, last so more specific matches override
        elif re.search(r'[Oo]ther', c_str):
            app_color = r_and_e_colors.get('other')

        # Fallback for anything unmatched
        if app_color is None:
            app_color = 'gray'  # you can choose any fallback color

        colors.append(app_color)

    # Safety check
    if len(colors) != len(categories):
        print("Warning: color matching not working properly")
        return None

    return colors


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
import textwrap

def wrap_category_name(name, width=20):
    """Wrap category names using textwrap module"""
    return '<br>'.join(textwrap.wrap(name, width=width))

def prepare_data_with_na_handling(data_list):
    processed_values = []
    text_labels = []

    for val in data_list:
        # --- Handle missing, text, or invalid entries ---
        if pd.isna(val) or str(val).strip().lower() in ['n/a', 'na', '', 'none']:
            processed_values.append(0)
            text_labels.append('N/A')
            continue
        elif '<1' in str(val):
            processed_values.append(.005)
            text_labels.append('<1%')
            continue
        elif float(val) == 0:
            processed_values.append(.001)
            text_labels.append('<1%')
            continue

        try:
            num_val = float(val)
        except ValueError:
            processed_values.append(0)
            text_labels.append('N/A')
            continue

        # --- Decide if value is already in decimal or needs conversion ---
        # Heuristic: if the value > 1.5, it’s likely a whole-number percent
        # (e.g. 75 means 75%), else assume it’s a decimal fraction (0.75 → 75%)
        if num_val > 1.5:
            percent_val = num_val / 100
        else:
            percent_val = num_val

        # --- Handle very small nonzero values ---
        if 0 < percent_val < 0.01:
            processed_values.append(percent_val)
            text_labels.append('<1%')
        else:
            processed_values.append(percent_val)
            if float(percent_val).is_integer():
                text_labels.append(f"{percent_val:.0%}")
            else:
                text_labels.append(f"{percent_val:.1%}")



    return processed_values, text_labels


def calculate_label_overlap_score(positions, y_values):
    """
    Calculate overlap penalty for label positions
    Similar to the article's overlap_weight principle
    """
    scores = []
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            # Check vertical overlap (y-axis proximity)
            y_diff = abs(y_values[i] - y_values[j])
            # Penalize if labels are close (within 3% of range)
            if y_diff < 3:
                scores.append(1 / (y_diff + 0.1))  # Higher penalty for closer labels
    return sum(scores) if scores else 0

def optimize_text_positions(y_values, available_positions):
    """
    Find optimal text positions to minimize overlap
    Adapted from the article's optimization principle
    """
    n_labels = len(y_values)
    best_positions = ['middle right'] * n_labels
    best_score = float('inf')
    
    # Sort by y-value to assign positions systematically
    sorted_indices = np.argsort(y_values)
    
    # Try different position assignments
    for attempt in range(min(100, 3**n_labels)):
        positions = ['middle right'] * n_labels
        
        # Assign positions based on relative y-values
        for idx, sort_idx in enumerate(sorted_indices):
            if idx % 3 == 0:
                positions[sort_idx] = 'top right'
            elif idx % 3 == 1:
                positions[sort_idx] = 'middle right'
            else:
                positions[sort_idx] = 'bottom right'
        
        # Calculate overlap score
        score = calculate_label_overlap_score(positions, y_values)
        
        if score < best_score:
            best_score = score
            best_positions = positions.copy()
        
        # Rotate positions for next attempt
        available_positions = available_positions[1:] + [available_positions[0]]
    
    return best_positions

def safe_format(val):
    try:
        return f"{float(val):.0f}"
    except (ValueError, TypeError):
        return 0
    
def format_percent_text(values):
    formatted = []
    for v in values:
        if v is None or pd.isna(v) or v < 0.01:
            formatted.append("N/A")  # or whatever text you use for missing
        else:
            formatted.append(f"{v:.0%}")
    return formatted

# ============================================================================
#   Page 1: Enrollment
# ============================================================================
#Enrollment Total
def graph_1_1(years, values):
    # Sample data
    # years = list(range(2015, 2025))
    # values = [45, 52, 48, 61, 67, 72, 78, 85, 89, 95]
    # all_values = years.to_list()+values.to_list()
    
    
    ymax = max(values)*1.10
    ymin = min(values)*.90
    
    fig = go.Figure()
    
    # Add line
    fig.add_trace(go.Scatter(
        x=years,
        y=values,
        mode='lines+markers',
        line=dict(color=PRIMARY_COLOR, width=3),
        marker=dict(size=8, color=PRIMARY_COLOR),
        name='Series 1'
    ))
    
    # Update layout
    fig.update_layout(
        **get_base_layout(500, 400),
        xaxis=dict(title='Year', showgrid=False, showline=True, linecolor=hunt_darkgray),
        yaxis=dict(range=[ymin,ymax],showgrid=False, gridcolor='lightgray', showline=True, linecolor=hunt_darkgray),
    )
    
    return fig
#By Race and Ethnicity
def graph_1_2(categories, state_series, us_series, state,graph_wd, graph_h):
    """
    Creates a horizontal stacked bar chart showing population breakdown by percentages.
    
    Args:
        categories: List of 6 category names (e.g., racial/ethnic groups)
        series1: List of 6 values for first series (e.g., state data)
        series2: List of 6 values for second series (e.g., US data)
    
    Returns:
        plotly Figure object
    """
    full_state_name = state_ref_r.get(state)
    # Calculate totals
    total_state_series = sum(state_series)
    total_us_series = sum(us_series)
    
    # Calculate percentages
    pct_state_series = [(val / total_state_series * 100) if total_state_series > 0 else 0 for val in state_series]
    pct_us_series = [(val / total_us_series * 100) if total_us_series > 0 else 0 for val in us_series]
    
    # Define colors for 6 race&ethnicity categories
    colors = get_colors(categories)
    
    # stop = len(categories)-1
    


    fig = go.Figure()
    
    
    
    # Add traces for each category in us series
    for i, category in enumerate(categories):
        fig.add_trace(go.Bar(
            name=category,
            y=['United States'],
            x=[pct_us_series[i]],
            orientation='h',
            marker=dict(color=colors[i]),
            text=f'{pct_us_series[i]:.0f}%',
            textposition='inside',
            insidetextanchor = 'middle',
            textfont=dict(
                size=14,           # Font size
                color='white',     # Font color
                family='Lato'     # Font family
            ),
            # hovertemplate=f'{category}<br>Count: {us_series[i]:,}<br>Percentage: {pct_us_series[i]:.1f}%<extra></extra>',
            legendgroup=category,
            showlegend=False  # Only show legend once per category
        ))
    # Add traces for each category in state series 
    for i, category in enumerate(categories):
        fig.add_trace(go.Bar(
            name=category,
            y=[f'{full_state_name}'],
            x=[pct_state_series[i]],
            orientation='h',
            marker=dict(color=colors[i]),
            text=f'{pct_state_series[i]:.1f}%',
            textposition='inside',
            insidetextanchor = 'middle',
            textfont=dict(
                size=14,           # Font size
                color='white',     # Font color
                family='Lato'     # Font family
            ),
            # hovertemplate=f'{category}<br>Count: {state_series[i]:,}<br>Percentage: {pct_state_series[i]:.1f}%<extra></extra>',
            legendgroup=category,
            showlegend=True
        ))
    fig.update_layout(
        **get_base_layout(graph_wd, graph_h),
        barmode='stack',
        xaxis=dict(
            # title='Percentage (%)',
            showgrid=True,
            showline=False,
            linecolor=hunt_darkgray,
            range=[0, 100]
        ),
        yaxis=dict(
            # title='',
            showgrid=False,
            showline=False,
            linecolor=hunt_darkgray
        )
    )
    
    return fig

#by Socioeconomic Status
def graph_1_3(input_dict, us_dict, state,graph_wd, graph_h):
    """
    Creates a horizontal stacked bar chart showing population breakdown by percentages.
    
    Args:
        categories: List of 6 category names (e.g., racial/ethnic groups)
        series1: List of 6 values for first series (e.g., state data)
        series2: List of 6 values for second series (e.g., US data)
    
    Returns:
        plotly Figure object
    """
    
    # Define colors for 6 race&ethnicity categories
    colors = get_colors(options = 'purple_dual')
    full_state_name = state_ref_r.get(state)
    
    perc_ed = float(input_dict.get('percent_economically_disadvantaged'))
    # print(perc_ed)
    perc_not_ed = 100-(perc_ed)
    state_x_vals = [perc_ed,perc_not_ed]
    # print('state vals')
    # for x in state_x_vals:
    #     print(x)

    us_perc_ed = float(us_dict.get('percent_economically_disadvantaged'))
    us_perc_not_ed = 100-(us_perc_ed)
    us_x_vals = [us_perc_ed,us_perc_not_ed]
    # print('us vals')
    # for x in us_x_vals:
    #     print(x)

    fig = go.Figure()
    
    categories = ['% Economically Disadvantaged','% Economically Disadvantaged']
    
    # Add traces for each category in us series
    for i, category in enumerate(categories):
        fig.add_trace(go.Bar(
            name=category,
            y=["United States"],
            x=[us_x_vals[i]],
            orientation='h',
            marker=dict(color=colors[i]),
            text=f'{us_x_vals[i]:.0f}%',
            textposition='inside',
            insidetextanchor = 'middle',
            textfont=dict(
                size=14,           # Font size
                color='white',     # Font color
                family='Lato'     # Font family
            ),
            # hovertemplate=f'{category}<br>Count: {us_series[i]:,}<br>Percentage: {pct_us_series[i]:.1f}%<extra></extra>',
            legendgroup=category,
            showlegend=False  # Only show legend once per category
        ))
    # Add traces for each category in state series 
    for i, category in enumerate(categories):
        fig.add_trace(go.Bar(
            name=category,
            y=[f'{full_state_name}'],
            x=[state_x_vals[i]],
            orientation='h',
            marker=dict(color=colors[i]),
            text=f'{state_x_vals[i]:.1f}%',
            textposition='inside',
            insidetextanchor = 'middle',
            textfont=dict(
                size=14,           # Font size
                color='white',     # Font color
                family='Lato'     # Font family
            ),
            # hovertemplate=f'{category}<br>Count: {state_series[i]:,}<br>Percentage: {pct_state_series[i]:.1f}%<extra></extra>',
            legendgroup=category,
            showlegend=True
        ))
    fig.update_layout(
        **get_base_layout(graph_wd, graph_h),
        barmode='stack',
        xaxis=dict(
            # title='Percentage (%)',
            showgrid=True,
            showline=False,
            linecolor=hunt_darkgray,
            range=[0, 100]
        ),
        yaxis=dict(
            # title='',
            showgrid=False,
            showline=False,
            linecolor=hunt_darkgray
        )
    )
    
    return fig


# ============================================================================
# GRAPH 1.4 - Horizontal stacked bar (2 series, 4 categories)
# ============================================================================

def graph_1_4(): # not completed
    categories = ['Category A', 'Category B', 'Category C', 'Category D']
    series1 = [32, 45, 38, 41]
    series2 = [18, 25, 22, 19]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=categories,
        x=series1,
        name='Series 1',
        orientation='h',
        marker=dict(color=PRIMARY_COLOR)
    ))
    
    fig.add_trace(go.Bar(
        y=categories,
        x=series2,
        name='Series 2',
        orientation='h',
        marker=dict(color=SECONDARY_COLOR)
    ))
    
    fig.update_layout(
        **get_base_layout('Graph 1.4: Horizontal Stacked Bar', 600, 350),
        barmode='stack',
        xaxis=dict(title='Values', showgrid=False, showline=True, linecolor=hunt_darkgray),
        yaxis=dict(title='', showgrid=False, showline=True, linecolor=hunt_darkgray)
    )
    
    return fig



# ============================================================================
#   Page 2: State Assessment Results
# ============================================================================
def graph_2_state_assess_graph(df, state):
    
    categories = get_col_uniq_vals(df['subject'])
    y_max = max(df['value'])+10 if len(df) > 0 else 100
    
    # Ensure all years are present
    all_years = ['2023', '2024', '2025']
    school_years = ['2022-2023', '2023-2024', '2024-2025']
    
    colors = [hunt_purple, hunt_light_purple]
    fig = go.Figure()
    
    for i, category in enumerate(categories):
        # Filter dataframe by subject/category
        category_df = df[df['subject'] == category]
        
        # Create a complete dataset with all years
        years_list = []
        values_list = []
        text_list = []
        
        for year in all_years:
            year_data = category_df[category_df['year'] == year]
            years_list.append(year)
            
            if len(year_data) > 0:
                values_list.append(year_data['value'].values[0])
                text_list.append(f"{year_data['value'].values[0]:.0f}%")
            else:
                values_list.append(0)  # Use 0 for missing data
                text_list.append("Not Available")
        
        fig.add_trace(go.Bar(
            name=category,
            x=years_list,
            y=values_list,
            marker=dict(
                color=colors[i],
                line=dict(width=0)
            ),
            text=text_list,
            textposition='outside',
            texttemplate='%{text}'
        ))
   
    fig.update_layout(
        **get_base_layout(600, 400),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1,
        xaxis=dict(
            showgrid=False, 
            showline=True, 
            linecolor=hunt_darkgray,
            tickangle=0,
            tickmode='array',
            tickvals=all_years,
            ticktext=school_years  # Display school year format
        ),
        yaxis=dict(
            range=[0, y_max],
            showgrid=True, 
            gridcolor='lightgray', 
            showline=True, 
            linecolor=hunt_darkgray
        )
    )
    
    return fig


# ============================================================================
#   Page 3: NAEP Assessment Results
# ============================================================================

def graph_naep_overall(df,us_df, col_label, offset):
    fig = go.Figure()
    val_list = df[col_label].to_list()
    val_list = [float(safe_format(x)) for x in val_list]
    # y_max = max(val_list) + 5


    #actual data points
    # US only data
    fig.add_trace(go.Scatter(
        x=us_df['year'],
        y=us_df[col_label],
        mode='lines+markers',
        line=dict(color=hunt_darkgray, width=5),
        marker=dict(size=20),
        showlegend=True
    ))
    # State only data
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df[col_label],
        mode='lines+markers',
        line=dict(color=hunt_light_purple, width=5),
        marker=dict(size=20),
        showlegend=True
    ))


    # Add text labels
    #us text lables
    us_text_y_positions = [float(x)+offset for x in us_df[col_label]]

    fig.add_trace(go.Scatter(
        x=us_df['year'].to_list(),
        y=us_text_y_positions,  # Use calculated positions
        mode='text',
        showlegend=False,
        text=us_df[col_label].round(0).astype(int).astype(str),  # Round for cleaner display
        textfont=dict(
                size=20,           # Font size
                color=hunt_darkgray,     # Font color
                family='Lato'     # Font family
            ),
        texttemplate='%{text:,.0f}%'
    ))
    #state text lables
    state_text_y_positions = [float(x)-offset for x in df[col_label]]

    fig.add_trace(go.Scatter(
        x=df['year'].to_list(),
        y=state_text_y_positions,  # Use calculated positions
        mode='text',
        showlegend=False,
        text=df[col_label],
        textfont=dict(
                size=20,           # Font size
                color=hunt_darkgray,     # Font color
                family='Lato'     # Font family
            ),
        texttemplate='%{text:,.0f}%'
    ))
    fig.update_yaxes(
            showticklabels=False,  # Hide tick labels
            showgrid=False,        # Hide gridlines
            zeroline=False         # Hide zero line
        )
    fig.update_layout(
        **get_base_layout(700, 450),
        xaxis=dict(
            showgrid=False, 
            showline=True, 
            linecolor=hunt_darkgray, 
            tickmode='array', 
            tickvals=df['year']
        ),
        yaxis=dict(
            # range=[ymin, 250],
            showgrid=False, 
            showline=True, 
            linecolor=hunt_darkgray
        ))
    
    # text_y_positions = [float(x)-offset for x in result['value']]
    
    return fig


# ============================================================================
#   Page 4: NAEP Assessment Results AND State Assessment compared
# ============================================================================

def get_census_regions(state):
    #region data set up 
    census_dir = r'C:\Users\clutz\THE HUNT INSTITUTE\The Hunt Institute Team Site - Documents\Policy Team\Data\Data Packets\K-12\data\census'
    regions_file = glob.glob(os.path.join(census_dir,'*.csv'))[0]
    regions = pd.read_csv(regions_file)
    regions.columns = [x.strip().lower().replace(' ','_') for x in regions.columns]
    # print(regions.head().to_string())
    regions_dict = dict(zip(regions['state_code'],regions['division']))
    if len(state)!= 2:
        print('state not right')
        return None
    region = regions_dict.get(state)
    # print(region)
    only_main_region = regions[regions['division']==region]
    
    return only_main_region
    
    
#regions graph
def graph_4_regions(df):
    
    states = df['jurisdiction']
    # categories = [f'Category {chr(65+i)}' for i in range(num_categories)]
    values = df['at_or_above_proficient']
    colors = df['color'].to_list()
    fig = go.Figure()
    
    custom_order = df['state_abrv'].to_list()
    custom_order.reverse()
    print(custom_order)
    fig.add_trace(go.Bar(
        y=states,
        x=values,
        orientation='h',
        marker=dict(color=colors),
        text=values,
        textposition='outside',
        texttemplate='%{text:,.0f}%'
    ))
    
    fig.update_layout(
        **get_base_layout(600, 350),
        # showlegend=False,
        xaxis=dict(title='Values', showgrid=False, showline=False, visible=False),
        yaxis=dict(title='', showgrid=False, showline=True, linecolor=hunt_darkgray,categoryorder='array',categoryarray=custom_order)
    )
    
    return fig


def graph_state_cut(df, col_label, state, years):

    fig = go.Figure()
    val_list = df[col_label].to_list()
    val_list = [float(safe_format(x)) for x in val_list]
    # y_max = max(val_list) + 5
    
    
    
    
    subj = get_col_uniq_vals(df['subject'])
    if len(subj)==1:
        if 'read' in str(subj[0]):
            subject_line = 238
        elif 'math' in str(subj[0]):
            subject_line = 249
    

    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['value'],
        mode='lines+markers+text',
        line=dict(color=hunt_purple, width=4),
        marker=dict(size=15),
        showlegend=True
    ))
    # line
    text_labels = [''] * (len(df['year']) - 1) + [str(subject_line)]  # Show label only on last point
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=[subject_line]*len(df['year']),
        mode='lines+text',
        line=dict(color=hunt_darkgray, width=4),
        marker=dict(size=20),
        showlegend=True,
        text=text_labels,
        textfont=dict(
                size=23,           # Font size
                color=hunt_darkgray,     # Font color
                family='Lato'     # Font family
            ),
        textposition='top center'

    ))
    

    
    return fig

# ============================================================================
#   Page 5: NAEP BY SUBGROUP
# ============================================================================


def graph_5_multi_series(df, col_label, group_col, years, **kwargs):
    label_all = kwargs.get('label_all', False)
    categories = get_col_uniq_vals(df[group_col])
    print(len(categories))
    if len(categories)==2:
        colors = get_colors(categories, options='purple_dual')
    else:
        colors = get_colors(categories)
    
    fig = go.Figure()
    val_list = df[col_label].to_list()
    val_list = [float(safe_format(x)) for x in val_list]
    y_max = max(val_list) + 5
    
    # Get latest year data for each subgroup
    latest_data = []
    for r in categories:
        subgroup_result = df[df[group_col] == r]
        latest_year = get_latest_year_with_data(subgroup_result, col_label)
        if latest_year is not None:
            latest_row = subgroup_result[subgroup_result['year'] == latest_year].iloc[0]
            latest_data.append({
                'category': r,
                'year': latest_year,
                'value': float(safe_format(latest_row[col_label])),
                'subgroup_result': subgroup_result
            })
    
    # SORT by value before distributing positions
    latest_data.sort(key=lambda x: x['value'])
    
    # Evenly distribute y-positions from lowest to highest value
    n_labels = len(latest_data)
    if n_labels > 1:
        # Use the actual min and max values for better spacing
        min_val = latest_data[0]['value']
        max_val = latest_data[-1]['value']
        # Spread them proportionally in the plot range
        evenly_spaced_positions = [min_val + i * (max_val - min_val) / (n_labels - 1) for i in range(n_labels)]
    else:
        evenly_spaced_positions = [latest_data[0]['value']]
    
    if label_all == True:
        for idx, r in enumerate(categories):
            if re.search(r'[Nn]on?t?', str(r)):
                pos = 'top center'
            else:
                pos = 'bottom center'
            subgroup_result = df[df[group_col] == r]
            
            fig.add_trace(go.Scatter(
                x=subgroup_result['year'],
                y=subgroup_result[col_label],
                mode='lines+markers+text',
                line=dict(color=colors[idx], width=5),
                marker=dict(size=15),
                showlegend=True,
                    text=subgroup_result[col_label],
                    textfont=dict(
                        size=23,           # Font size
                        color=hunt_darkgray,     # Font color
                        family='Lato'     # Font family
                    ),
                    textposition='top center',
                    texttemplate='%{text:,.0f}%'

                
            ))
            fig.update_layout(
            **get_base_layout(700, 450),
            xaxis=dict(
                showgrid=False, 
                showline=True, 
                linecolor=hunt_darkgray, 
                tickmode='array', 
                tickvals=years
            )
        )
    else:
        # ADD CONNECTOR LINES FIRST (so they're in the back)
        for i, data_item in enumerate(latest_data):
            idx = categories.index(data_item['category'])
            label_y = evenly_spaced_positions[i]
            
            # Add dotted connector line
            fig.add_shape(
                type='line',
                x0=data_item['year'],
                y0=data_item['value'],
                x1=data_item['year'] + 0.5,
                y1=label_y,
                line=dict(
                    color=colors[idx],
                    width=1,
                    dash='dot'
                )
            )
            
            # Add text annotation
            fig.add_annotation(
                x=data_item['year'] + 0.5,
                y=label_y,
                text=str(safe_format(data_item['value'])) + '%',
                showarrow=False,
                xanchor='left',
                font=dict(size=20, color=hunt_darkgray, family='Lato'),
                bgcolor='rgba(255,255,255,0.8)',
                borderpad=3
            )
        
        # ADD MAIN LINE TRACES LAST (so markers appear on top)
        for idx, r in enumerate(categories):
            subgroup_result = df[df[group_col] == r]
            
            fig.add_trace(go.Scatter(
                x=subgroup_result['year'],
                y=subgroup_result[col_label],
                mode='lines+markers',
                line=dict(color=colors[idx], width=5),
                marker=dict(size=15),
                showlegend=True
            ))
    
        fig.update_layout(
            **get_base_layout(700, 450),
            xaxis=dict(
                showgrid=False, 
                showline=True, 
                linecolor=hunt_darkgray, 
                tickmode='array', 
                tickvals=years
            ),
            yaxis=dict(
                range=[0, 100],
                showgrid=False, 
                showline=True, 
                linecolor=hunt_darkgray, 
                ticksuffix='%'
            )
        )
    
    
    return fig

def get_latest_year_with_data(subgroup_df, col_label):
    """Find the most recent year with valid data"""
    for year in sorted(subgroup_df['year'].unique(), reverse=True):
        val = subgroup_df[subgroup_df['year'] == year][col_label].values
        if len(val) > 0 and val[0] not in ['‡', '—', '–', 'N/A', '', None]:
            try:
                if safe_format(val[0]) != 0.0:
                    return year
            except:
                continue
    return None

# ============================================================================
#   Page 6: NON academic metrics
# ============================================================================

import plotly.graph_objects as go
def graph_chron_abs(df, col_label):
    """
    Simple single-measure bar graph.
    Parameters:
    - df: DataFrame containing your data
    - col_label: the column name with values for the bars
    - x_col: column name for x-axis categories
    - title: optional chart title
    - bar_color: color of the bars
    """
   
    # Step 1: Define all possible groups in order
    all_groups = [
        'American Indian/Alaska Native',
        'Asian/Pacific Islander',
        'Native Hawaiian/Other Pacific Islander',
        'Asian',
        'Hispanic',
        'Black',
        'White',
        'Two or More'
    ]
    
    # Remap the group names to match get_order keys
    remap = {
        'American Indian/Alaska Native': 'nat_am_or_ak',
        'Asian/Pacific Islander': 'asian_pacific_islander',
        "Native Hawaiian/Other Pacific Islander": 'pacific',
        "Asian": 'asian',
        'Hispanic': 'hispanic',
        'Black': 'black',
        'White': 'white',
        'Two or More': 'two_or_more'
    }
    
    # Step 2: Create a complete DataFrame with all groups
    complete_df = pd.DataFrame({'group': all_groups})
    
    # Merge with existing data
    df_merged = complete_df.merge(df[['group', 'value']], on='group', how='left')
    
    # Add group_key and order
    df_merged['group_key'] = df_merged['group'].map(remap).fillna(df_merged['group'])
    df_merged['order'] = df_merged['group_key'].apply(get_order)
    df_sorted = df_merged.sort_values('order')
    
    # Get colors for all groups
    categories = df_sorted['group'].tolist()
    colors = get_colors(categories)
    
    # Create text labels (show "n/a" for missing values)
    text_labels = df_sorted['value'].apply(
        lambda x: f"{x:.1f}%" if pd.notna(x) else "n/a"
    )
    
    print('CATEGORIES')
    print(categories)
    print(colors)
    print(df_sorted)
    
    # Create figure
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_sorted['group'],
        y=df_sorted['value'].fillna(0),  # Fill NaN with 0 for visualization
        text=text_labels,
        textposition='outside',
        marker_color=colors
    ))
   
    # Layout
    fig.update_layout(
        xaxis=dict(showgrid=False, showline=True, linecolor='gray'),
        yaxis=dict(showgrid=True, tickformat=".0%"),
        **get_base_layout(700, 450)
    )
   
    return fig
def graph_other_chron_abs(df):
    import plotly.graph_objects as go
    import pandas as pd
    categories = list(df.columns)[3:]
    print(categories)

    # Use the NA handling function
    state_data, state_text = prepare_data_with_na_handling(df.iloc[0].values.tolist()[3:])
    
    state_text = [
    f"{x:.0%}" if isinstance(x, (int, float)) else x
    for x in state_text
    ]
   
    # Calculate y_max excluding NA values
    valid_values = [v for v in state_data if v > 0.01]
    y_max = (max(valid_values) + 0.10) if valid_values else 1.0

    
    # Create grouped bar chart
    fig = go.Figure()

    # Add state bar trace
    fig.add_trace(go.Bar(
        x=df.columns,
        y=state_data,
        marker=dict(
            color=[hunt_purple if v > 0.01 else hunt_gray30 for v in state_data],
            line=dict(width=0)
        ),
        text=state_text,
        texttemplate='%{text}',
        textposition='outside'
        # name='Dataset 1'  # Legend label
    ))
    

    fig.update_layout(
    **get_base_layout(600, 400),

    yaxis=dict(
        range=[0, y_max],
        tickformat='.0%'
    ),
    xaxis=dict(
        showgrid=False,
        showline=True,
        linecolor=hunt_darkgray,
        tickangle=0,
        tickmode='array',
        tickvals=list(range(len(categories))),
        ticktext=[wrap_category_name(c) for c in categories]
    ))
    return fig


def graph_oos(df, us_df, state):
    import plotly.graph_objects as go
    import pandas as pd
    categories = list(df.columns)[1:]
    print(categories)

    # Use the NA handling function
    state_data, state_text = prepare_data_with_na_handling(df.iloc[0].values.tolist()[1:])
    us_data, us_text = prepare_data_with_na_handling(us_df.iloc[0].values.tolist()[1:])
    
    state_text = [
    f"{x:.0%}" if isinstance(x, (int, float)) else x
    for x in state_text
    ]
    us_text = [
        f"{x:.0%}" if isinstance(x, (int, float)) else x
        for x in us_text
    ]


    # Create grouped bar chart
    fig = go.Figure()

    # Add state bar trace
    fig.add_trace(go.Bar(
        x=df.columns,
        y=state_data,
        marker=dict(
            color=[hunt_purple if v > 0.01 else hunt_gray30 for v in state_data],
            line=dict(width=0)
        ),
        text=state_text,
        texttemplate='%{text}',
        textposition='outside'
        # name='Dataset 1'  # Legend label
    ))
    # Add us bar trace
    fig.add_trace(go.Bar(
        x=df.columns,
        y=us_data,
        marker=dict(
            color=[hunt_darkgray if v > 0.01 else hunt_gray30 for v in us_data],
            line=dict(width=0)
        ),
        text=us_text,
        texttemplate='%{text}',
        textposition='outside'
        # name='Dataset 1'  # Legend label
    ))

    fig.update_layout(
    **get_base_layout(600, 400),
    barmode='group',
    bargap=0.15,
    bargroupgap=0,
    uniformtext=dict(
    mode='show',
    minsize=30
    ),
    yaxis=dict(
        range=[0, 1],
        tickformat='.0%'
    ),
    xaxis=dict(
        showgrid=False,
        showline=True,
        linecolor=hunt_darkgray,
        tickangle=0,
        tickmode='array',
        tickvals=list(range(len(categories))),
        ticktext=[wrap_category_name(c) for c in categories]
    )
)
    return fig
    

# ============================================================================
#   Page 7: Graduation Rate Analysis
# ============================================================================


def convert_to_percent(input_list):
    arr = np.array(input_list, dtype=np.float64)
    arr = arr[~np.isnan(arr)]

    if arr.size == 0:
        return []

    if arr.max() > 1:
        return (arr / 100).tolist()
    return arr.tolist()



def graph_grad_rate(df, us_df, col_label, state, years, offset):
    
    
    fig = go.Figure()
    val_list = df[col_label].to_list()
    val_list = [float(safe_format(x)) for x in val_list]
    # y_max = max(val_list) + 5
    
    
    

    #actual data points
    # US only data
    fig.add_trace(go.Scatter(
        x=us_df['year'],
        y=us_df[col_label],
        mode='lines+markers',
        line=dict(color=hunt_darkgray, width=4),
        marker=dict(size=20),
        showlegend=True
    ))
    # State only data
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df[col_label],
        mode='lines+markers',
        line=dict(color=hunt_light_purple, width=4),
        marker=dict(size=20),
        showlegend=True
    ))


    # Add text labels
    #us text lables
    us_text_y_positions = [float(x)+offset for x in us_df[col_label]]

    fig.add_trace(go.Scatter(
        x=us_df['year'].to_list(),
        y=us_text_y_positions,  # Use calculated positions
        mode='text',
        showlegend=False,
        text=us_df[col_label].round(0).astype(int).astype(str),  # Round for cleaner display
        textfont=dict(
                size=20,           # Font size
                color=hunt_darkgray,     # Font color
                family='Lato'     # Font family
            ),
        texttemplate='%{text:,.0f}%'
    ))
    #state text lables
    state_text_y_positions = [float(x)-offset for x in df[col_label]]

    fig.add_trace(go.Scatter(
        x=df['year'].to_list(),
        y=state_text_y_positions,  # Use calculated positions
        mode='text',
        showlegend=False,
        text=df[col_label],
        textfont=dict(
                size=20,           # Font size
                color=hunt_darkgray,     # Font color
                family='Lato'     # Font family
            ),
        texttemplate='%{text:,.0f}%'
    ))
    # fig.update_yaxes(
    #         visible = False,
    #         showticklabels=False,  # Hide tick labels
    #         showgrid=False,        # Hide gridlines
    #         zeroline=False         # Hide zero line
    #     )
    fig.update_layout(
        **get_base_layout(700, 450),
        xaxis=dict(
            showgrid=False, 
            showline=True, 
            linecolor=hunt_darkgray, 
            tickmode='array', 
            tickvals=df['year']
        ),
        )
    
    # text_y_positions = [float(x)-offset for x in result['value']]
    
    return fig

def wrap_category_name(name):
    # Custom wrapping for each category
    wrapping = {
        'Total': 'Total',
        'American Indian/Alaska Native': 'American Indian/<br>Alaska Native',
        'Asian/Pacific Islander': 'Asian/<br>Pacific Islander',
        'Hispanic': 'Hispanic',
        'Black': 'Black',
        'White': 'White',
        'Two or More': 'Two or<br>More'
    }
    return wrapping.get(name, name)

def graph_gradrate_re(df, us_df, state):
    # Standardize group names if needed
    print("Original df groups:", df['group'].unique())
    print("Original us_df groups:", us_df['group'].unique())
    
    # Expanded label map to catch more variations
    label_map = {
        'Total': 'Total',
        'American Indian / Alaska Native': 'American Indian/Alaska Native',
        'American Indian/Alaska Native': 'American Indian/Alaska Native',
        'Asian/Pacific Islander': 'Asian/Pacific Islander',
        'Asian / Pacific Islander': 'Asian/Pacific Islander',
        'Hispanic': 'Hispanic',
        'Black': 'Black',
        'Black or African American': 'Black',
        'White': 'White',
        'Two or more races': 'Two or More',
        'Two or More': 'Two or More',
        'Multiracial': 'Two or More'
    }
    
    # Apply the mapping
    df['group'] = df['group'].map(label_map).fillna(df['group'])  # Keep original if no match
    us_df['group'] = us_df['group'].map(label_map).fillna(us_df['group'])
    
    # Print after mapping to see if something didn't map
    print("After mapping df groups:", df['group'].unique())
    print("After mapping us_df groups:", us_df['group'].unique())
    
    categories = ['Total', 'American Indian/Alaska Native', 'Asian/Pacific Islander', 
                  'Hispanic', 'Black', 'White', 'Two or More']

    # Align both datasets to the same category order
    df = df.set_index('group').reindex(categories).reset_index()
    us_df = us_df.set_index('group').reindex(categories).reset_index()
    
    # Use the NA handling function
    state_data, state_text = prepare_data_with_na_handling(df['grad_rate'].tolist())
    us_data, us_text = prepare_data_with_na_handling(us_df['grad_rate'].tolist())
    
    state_text = [
    f"{x:.0%}" if isinstance(x, (int, float)) else x
    for x in state_text
    ]
    us_text = [
        f"{x:.0%}" if isinstance(x, (int, float)) else x
        for x in us_text
    ]


    
    # state_text = [f"{x:.0%}" if str(x).lower()!= 'n/a' else x for x in state_text ]
    # us_text = [f"{x:.0%}" if str(x).lower()!= 'n/a' else x for x in us_text]
    # state_text = format_percent_text(state_data)
    # us_text = format_percent_text(us_data)

    # Calculate y_max excluding NA values
    valid_values = [v for v in state_data + us_data if v > 0.01]
    y_max = (max(valid_values) + 0.10) if valid_values else 1.0
    
    fig = go.Figure()
    
    # State bar
    fig.add_trace(go.Bar(
        x=categories,
        y=state_data,
        name=state,
        marker=dict(
            color=[hunt_purple if v > 0.01 else hunt_gray30 for v in state_data],
            line=dict(width=0)
        ),
        text=state_text,
        texttemplate='%{text}',
        textposition='outside'
        
    ))
    
    # US bar
    fig.add_trace(go.Bar(
        x=categories,
        y=us_data,
        name='US',
        marker=dict(
            color=[hunt_darkgray if v > 0.01 else hunt_gray30 for v in us_data],
            line=dict(width=0)
        ),
        text=us_text,
        textposition='outside',
        texttemplate='%{text}',
    ))
    
    fig.update_layout(
        **get_base_layout(600, 400),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1,
        uniformtext=dict(
            mode='show',
            minsize=30
        ),
        yaxis=dict(
            range=[0, y_max],
            tickformat='.0%'
        ),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor=hunt_darkgray,
            tickangle=0,
            tickmode='array',
            tickvals=list(range(len(categories))),
            ticktext=[wrap_category_name(c) for c in categories]
        )
    )
    fig.update_xaxes(type='category')
    return fig


def graph_gradrate_other_subgroup(categories, df, us_df, state):
    # Standardize group names if needed
    
    # Align both datasets to the same category order
    df = df.set_index('group').reindex(categories).reset_index()
    us_df = us_df.set_index('group').reindex(categories).reset_index()

    state_data = convert_to_percent(df['grad_rate'].tolist())
    us_data = convert_to_percent(us_df['grad_rate'].tolist())

    y_max = max(state_data + us_data) + 0.10

    fig = go.Figure()

    # State bar
    fig.add_trace(go.Bar(
        x=categories,
        y=state_data,
        name='% of CTE',
        marker=dict(color=hunt_purple, line=dict(width=0)),
        text=state_data,
        textposition='outside',
        texttemplate='%{text:,.0%}',
        textfont=dict(
            size=20,           # Font size
            color=hunt_darkgray,     # Font color
            family='Lato'     # Font family
            ),
    ))

    # US bar
    fig.add_trace(go.Bar(
        x=categories,
        y=us_data,
        name='% of Enrollment',
        marker=dict(color=hunt_darkgray, line=dict(width=0)),
        text=us_data,
        textposition='outside',
        texttemplate='%{text:,.0%}',
        textfont=dict(
            size=20,           # Font size
            color=hunt_darkgray,     # Font color
            family='Lato'     # Font family
            ),
    ))

    fig.update_layout(
        **get_base_layout(600, 400),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1,
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor=hunt_darkgray,
            tickangle=0,
            tickmode='array',
            tickvals=categories,
            ticktext=categories,
        ),
        yaxis=dict(
            range=[0, y_max],
            showgrid=True,
            gridcolor='lightgray',
            showline=True,
            linecolor=hunt_darkgray,
            ticksuffix = '%',
           
        )
    )

    fig.update_xaxes(
        type='category',
        tickfont=dict(
            family='Lato',  # Font family
            size=20,        # Font size
            color=hunt_darkgray   # Font color
        )
    )
                     

    return fig


# ============================================================================
#   Page 8: Dropouts, CTE concentrators, and AP CLASSES 
# ============================================================================

def graph_dropouts(df, us_df, state):
    # Standardize group names if needed
    print("Original df groups:", df['group'].unique())
    print("Original us_df groups:", us_df['group'].unique())
    
    # Expanded label map to catch more variations
    label_map = {
        'Total': 'Total',
        'American Indian / Alaska Native': 'American Indian/Alaska Native',
        'American Indian/Alaska Native': 'American Indian/Alaska Native',
        'Asian/Pacific Islander': 'Asian/Pacific Islander',
        'Asian / Pacific Islander': 'Asian/Pacific Islander',
        'Hispanic': 'Hispanic',
        'Black': 'Black',
        'Black or African American': 'Black',
        'White': 'White',
        'Two or more races': 'Two or More',
        'Two or More': 'Two or More',
        'Multiracial': 'Two or More'
    }
    
    # Apply the mapping
    df['group'] = df['group'].map(label_map).fillna(df['group'])  # Keep original if no match
    us_df['group'] = us_df['group'].map(label_map).fillna(us_df['group'])
    
    # Print after mapping to see if something didn't map
    print("After mapping df groups:", df['group'].unique())
    print("After mapping us_df groups:", us_df['group'].unique())
    
    categories = ['Total', 'American Indian/Alaska Native', 'Asian/Pacific Islander', 
                  'Hispanic', 'Black', 'White', 'Two or More']
    # label_map = {
    #     'Total': 'Total',
    #     'American Indian / Alaska Native': 'American Indian/Alaska Native',
    #     'Asian/Pacific Islander': 'Asian/Pacific Islander',
    #     'Hispanic': 'Hispanic',
    #     'Black':'Black',
    #     'White': 'White',
    #     'Two or more races': 'Two or More',
    #     'Two or More': 'Two or More'
    # }
    # df['group'] = df['group'].replace(label_map)
    # us_df['group'] = us_df['group'].replace(label_map)
    # categories = list(label_map.values())
    
    # Align both datasets to the same category order
    df = df.set_index('group').reindex(categories).reset_index()
    us_df = us_df.set_index('group').reindex(categories).reset_index()
    
    # Use the NA handling function
    state_data, state_text = prepare_data_with_na_handling(df['value'].tolist())
    us_data, us_text = prepare_data_with_na_handling(us_df['value'].tolist())
    
    state_text = [
    f"{x:.0%}" if isinstance(x, (int, float)) else x
    for x in state_text
    ]
    us_text = [
        f"{x:.0%}" if isinstance(x, (int, float)) else x
        for x in us_text
    ]


    
    # state_text = [f"{x:.0%}" if str(x).lower()!= 'n/a' else x for x in state_text ]
    # us_text = [f"{x:.0%}" if str(x).lower()!= 'n/a' else x for x in us_text]
    # state_text = format_percent_text(state_data)
    # us_text = format_percent_text(us_data)

    # Calculate y_max excluding NA values
    valid_values = [v for v in state_data + us_data if v > 0.01]
    y_max = (max(valid_values) + 0.10) if valid_values else 1.0
    
    fig = go.Figure()
    
    # State bar
    fig.add_trace(go.Bar(
        x=categories,
        y=state_data,
        name=state,
        marker=dict(
            color=[hunt_purple if v > 0.01 else hunt_gray30 for v in state_data],
            line=dict(width=0)
        ),
        text=state_text,
        texttemplate='%{text}',
        textposition='outside'
        
    ))
    
    # US bar
    fig.add_trace(go.Bar(
        x=categories,
        y=us_data,
        name='US',
        marker=dict(
            color=[hunt_darkgray if v > 0.01 else hunt_gray30 for v in us_data],
            line=dict(width=0)
        ),
        text=us_text,
        textposition='outside',
        texttemplate='%{text}',
    ))
    
    fig.update_layout(
        **get_base_layout(600, 400),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1,
        uniformtext=dict(
            mode='show',
            minsize=30
        ),
        yaxis=dict(
            range=[0, y_max],
            tickformat='.0%'
        ),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor=hunt_darkgray,
            tickangle=0,
            tickmode='array',
            tickvals=list(range(len(categories))),
            ticktext=[wrap_category_name(c) for c in categories]
        )
    )
    fig.update_xaxes(type='category')
    return fig




def get_order(x):

    if x=='nat_am_or_ak':
        return 1
    elif x=='total':
        return 0
    elif x=='asian_pacific_islander':
        return 2
    elif x=='asian':
        return 2
    elif x == 'pacific':
        return 2
    elif x=='hispanic':
        return 3
    elif x=='black':
        return 4
    elif x=='white':
        return 5    
    elif x=='two_or_more':
        return 6    
    
def graph_8_cte(df, state):
    df = df[df['state']==state].reset_index(drop=True)
    df['order'] = df['group'].apply(lambda x: get_order(x))
    df = df.sort_values(by='order')
    print(df.to_string())
    categories = ["American Indian/Alaska Native","Asian/Pacific Islander","Hispanic","Black","White", "Two or More"]
    by_cte_total_series = df['perc_o_cte'].to_list()
    by_enroll_series = df['perc_o_enr'].to_list()
    
    # Use the NA handling function
    total_data, total_text = prepare_data_with_na_handling(by_cte_total_series)
    enr_data, enr_text = prepare_data_with_na_handling(by_enroll_series)
    # total_text = [f"{x:.0%}" if str(x).lower()!= 'n/a' or '<' in str(x).lower() else x for x in total_text ]
    # enr_text = [f"{x:.0%}" if str(x).lower()!= 'n/a'  or '<' in str(x).lower() else x for x in enr_text]
    
    total_text = [
    f"{x:.0%}" if isinstance(x, (int, float)) else x
    for x in total_text
    ]
    enr_text = [
        f"{x:.0%}" if isinstance(x, (int, float)) else x
        for x in enr_text
    ]

    # Calculate y_max excluding NA values
    valid_values = [v for v in total_data + enr_data if v > 0.01]
    y_max = (max(valid_values) + 0.10) if valid_values else 1.0
    
    # print(by_cte_total_series)
    # print(by_enroll_series)

    # y_max = max(by_cte_total_series+by_enroll_series)+0.10
    

    fig = go.Figure()
   # State bar
    fig.add_trace(go.Bar(
        x=categories,
        y=enr_data,
        name=state,
        marker=dict(
            color=[hunt_purple if v > 0.01 else hunt_gray30 for v in enr_data],
            line=dict(width=0)
        ),
        text=enr_text,
        texttemplate='%{text}',
        textposition='outside'
        
    ))
    
    # total_data
    fig.add_trace(go.Bar(
        x=categories,
        y=total_data,
        name='US',
        marker=dict(
            color=[hunt_darkgray if v > 0.01 else hunt_gray30 for v in total_data],
            line=dict(width=0)
        ),
        text=total_text,
        textposition='outside',
        texttemplate='%{text}',
    ))
    # fig.add_trace(go.Bar(
    #     x=categories,
    #     y=by_cte_total_series,
    #     name='% of CTE',
    #     marker=dict(
    #         color=hunt_dark_purple,
    #         line=dict(width=0)
    #     ),
    #     text=by_cte_total_series,
    #     textposition='outside',
    #     texttemplate='%{text:,.0%}'
    # ))
   
    # fig.add_trace(go.Bar(
    #     x=categories,
    #     y=by_enroll_series,
    #     name='% of Enrollment',
    #     marker=dict(
    #         color=hunt_light_purple,
    #         line=dict(width=0)
    #     ),
    #     text=by_enroll_series,
    #     textposition='outside',
    #     texttemplate='%{text:,.0%}'
    # ))
   
    fig.update_layout(
        **get_base_layout(600, 400),
        barmode='group',      # Side-by-side bars
        bargap=0.15,          # Gap between category groups
        bargroupgap=0.1,      # Gap between bars within each group
        xaxis=dict(
            showgrid=False, 
            showline=True, 
            linecolor=hunt_darkgray,
            tickmode='array',
            tickvals=categories,
            ticktext=[c.replace(" / ", "/").replace(" ", "<br>") for c in categories]  # optional: line wrap

            # tickangle=-45     # Angle labels for better readability
        ),
        yaxis=dict(
            range=[0,1],
            title='Values', 
            showgrid=True, 
            gridcolor='lightgray', 
            showline=True, 
            linecolor=hunt_darkgray
        )
    )
    
    fig.update_xaxes(type='category')
    
    return fig


def graph_ap(state_value, us_value, state, display_type):
    # df = df[df['state_abrv'] == state].reset_index(drop=True)
   
    # # Get US data
    # us_only = df[df['state_abrv'] == "US"]
    # us_value = us_only['perc_in_an_ap'].iloc[0] if len(us_only) > 0 else 0
    
    # # Get state data
    # state_data = df[df['state_abrv'] == state]
    # state_value = state_data['perc_in_an_ap'].iloc[0] if len(state_data) > 0 else 0
   
    state_name = state_ref_r.get(state)
    categories = [f'{state_name}', "United States"]
    values = [state_value, us_value]  # Match categories with values
    
    
   
    fig = go.Figure()
   
    if display_type == 'percent':
        y_max = max(values) + 0.10
    # Single trace with both values
        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            marker=dict(
                color=[hunt_purple, hunt_darkgray],  # Different colors for each bar
                line=dict(width=0)
            ),
            text=values,
            textposition='outside',
            texttemplate='%{text:.0%}'
        ))
    elif display_type == 'number':
          y_max = max(values)+(max(values)*.1)
          fig.add_trace(go.Bar(
            x=categories,
            y=values,
            marker=dict(
                color=[hunt_purple, hunt_darkgray],  # Different colors for each bar
                line=dict(width=0)
            ),
            text=values,
            textposition='outside',
            texttemplate='%{text:.0f}'))
    
    fig.update_layout(
        **get_base_layout(600, 400),
        bargap=0.15,
        xaxis=dict(
            title='',  # Remove or keep as needed
            showgrid=False,
            showline=True,
            linecolor=hunt_darkgray,
            tickangle=0  # No angle needed for just 2 bars
        ),
        yaxis=dict(
            range=[0, y_max],
            title='Percentage in AP',
            showgrid=True,
            gridcolor='lightgray',
            showline=True,
            linecolor=hunt_darkgray,
        )
    )
   
    fig.update_xaxes(type='category')
   
    return fig



# ============================================================================
#   Page 9: College Entrance
# ============================================================================

def graph_act_benchmarks(df, us_df, state):
    import plotly.graph_objects as go
    import pandas as pd
    categories = list(df.columns)[1:]
    print(categories)

    # Use the NA handling function
    state_data, state_text = prepare_data_with_na_handling(df.iloc[0].values.tolist()[1:])
    us_data, us_text = prepare_data_with_na_handling(us_df.iloc[0].values.tolist()[1:])
    
    state_text = [
    f"{x:.0%}" if isinstance(x, (int, float)) else x
    for x in state_text
    ]
    us_text = [
        f"{x:.0%}" if isinstance(x, (int, float)) else x
        for x in us_text
    ]



    # Create grouped bar chart
    fig = go.Figure()

    # Add state bar trace
    fig.add_trace(go.Bar(
        x=df.columns,
        y=state_data,
        marker=dict(
            color=[hunt_purple if v > 0.01 else hunt_gray30 for v in state_data],
            line=dict(width=0)
        ),
        text=state_text,
        texttemplate='%{text}',
        textposition='outside'
        # name='Dataset 1'  # Legend label
    ))
    # Add us bar trace
    fig.add_trace(go.Bar(
        x=df.columns,
        y=us_data,
        marker=dict(
            color=[hunt_darkgray if v > 0.01 else hunt_gray30 for v in us_data],
            line=dict(width=0)
        ),
        text=us_text,
        texttemplate='%{text}',
        textposition='outside'
        # name='Dataset 1'  # Legend label
    ))

    fig.update_layout(
    **get_base_layout(600, 400),
    barmode='group',
    bargap=0.15,
    bargroupgap=0,
    uniformtext=dict(
    mode='show',
    minsize=30
    ),
    yaxis=dict(
        range=[0, 1],
        tickformat='.0%'
    ),
    xaxis=dict(
        showgrid=False,
        showline=True,
        linecolor=hunt_darkgray,
        tickangle=0,
        tickmode='array',
        tickvals=list(range(len(categories))),
        ticktext=[wrap_category_name(c) for c in categories]
    )
)
    return fig
    
    # # Standardize group names if needed
    # print("Original df groups:", df['group'].unique())
    # print("Original us_df groups:", us_df['group'].unique())
    
    # # Expanded label map to catch more variations
    # label_map = {
    #     'Total': 'Total',
    #     'American Indian / Alaska Native': 'American Indian/Alaska Native',
    #     'American Indian/Alaska Native': 'American Indian/Alaska Native',
    #     'Asian/Pacific Islander': 'Asian/Pacific Islander',
    #     'Asian / Pacific Islander': 'Asian/Pacific Islander',
    #     'Hispanic': 'Hispanic',
    #     'Black': 'Black',
    #     'Black or African American': 'Black',
    #     'White': 'White',
    #     'Two or more races': 'Two or More',
    #     'Two or More': 'Two or More',
    #     'Multiracial': 'Two or More'
    # }
    
    # # Apply the mapping
    # df['group'] = df['group'].map(label_map).fillna(df['group'])  # Keep original if no match
    # us_df['group'] = us_df['group'].map(label_map).fillna(us_df['group'])
    
    # # Print after mapping to see if something didn't map
    # print("After mapping df groups:", df['group'].unique())
    # print("After mapping us_df groups:", us_df['group'].unique())
    
    # categories = ['Total', 'American Indian/Alaska Native', 'Asian/Pacific Islander', 
    #               'Hispanic', 'Black', 'White', 'Two or More']
    # # label_map = {
    # #     'Total': 'Total',
    # #     'American Indian / Alaska Native': 'American Indian/Alaska Native',
    # #     'Asian/Pacific Islander': 'Asian/Pacific Islander',
    # #     'Hispanic': 'Hispanic',
    # #     'Black':'Black',
    # #     'White': 'White',
    # #     'Two or more races': 'Two or More',
    # #     'Two or More': 'Two or More'
    # # }
    # # df['group'] = df['group'].replace(label_map)
    # # us_df['group'] = us_df['group'].replace(label_map)
    # # categories = list(label_map.values())
    
    # # Align both datasets to the same category order
    # df = df.set_index('group').reindex(categories).reset_index()
    # us_df = us_df.set_index('group').reindex(categories).reset_index()
    
    # # Use the NA handling function
    # state_data, state_text = prepare_data_with_na_handling(df['grad_rate'].tolist())
    # us_data, us_text = prepare_data_with_na_handling(us_df['grad_rate'].tolist())
    
    # state_text = [
    # f"{x:.0%}" if isinstance(x, (int, float)) else x
    # for x in state_text
    # ]
    # us_text = [
    #     f"{x:.0%}" if isinstance(x, (int, float)) else x
    #     for x in us_text
    # ]


    
    # # state_text = [f"{x:.0%}" if str(x).lower()!= 'n/a' else x for x in state_text ]
    # # us_text = [f"{x:.0%}" if str(x).lower()!= 'n/a' else x for x in us_text]
    # # state_text = format_percent_text(state_data)
    # # us_text = format_percent_text(us_data)

    # # Calculate y_max excluding NA values
    # valid_values = [v for v in state_data + us_data if v > 0.01]
    # y_max = (max(valid_values) + 0.10) if valid_values else 1.0
    
    # fig = go.Figure()
    
    # # State bar
    # fig.add_trace(go.Bar(
    #     x=categories,
    #     y=state_data,
    #     name=state,
    #     marker=dict(
    #         color=[hunt_purple if v > 0.01 else hunt_gray30 for v in state_data],
    #         line=dict(width=0)
    #     ),
    #     text=state_text,
    #     texttemplate='%{text}',
    #     textposition='outside'
        
    # ))
    
    # # US bar
    # fig.add_trace(go.Bar(
    #     x=categories,
    #     y=us_data,
    #     name='US',
    #     marker=dict(
    #         color=[hunt_darkgray if v > 0.01 else hunt_gray30 for v in us_data],
    #         line=dict(width=0)
    #     ),
    #     text=us_text,
    #     textposition='outside',
    #     texttemplate='%{text}',
    # ))
    
    # fig.update_layout(
    #     **get_base_layout(600, 400),
    #     barmode='group',
    #     bargap=0.15,
    #     bargroupgap=0.1,
    #     uniformtext=dict(
    #         mode='show',
    #         minsize=30
    #     ),
    #     yaxis=dict(
    #         range=[0, y_max],
    #         tickformat='.0%'
    #     ),
    #     xaxis=dict(
    #         showgrid=False,
    #         showline=True,
    #         linecolor=hunt_darkgray,
    #         tickangle=0,
    #         tickmode='array',
    #         tickvals=list(range(len(categories))),
    #         ticktext=[wrap_category_name(c) for c in categories]
    #     )
    # )
    # fig.update_xaxes(type='category')
    return fig


if __name__ == "__main__":
    # Example: Display a single graph
    fig = graph_1_1()
    fig.show()
    
    # Example: Save a graph
    # output_path = Path('output/graph_1_1.png')
    # output_path.parent.mkdir(parents=True, exist_ok=True)
    # fig.write_image(str(output_path), width=500, height=400, scale=2)
    
    # Example: Generate all graphs in a loop
    # graph_functions = [
    #     graph_1_1, graph_1_2, graph_1_3, graph_1_4,
    #     graph_2_1, graph_2_2,
    #     graph_3_1, graph_3_2, graph_3_3, graph_3_4,
    #     # ... add all other functions
    # ]
    # 
    # for func in graph_functions:
    #     fig = func()
    #     # fig.show()  # Display
    #     # or save: fig.write_image(f'output/{func.__name__}.png')
