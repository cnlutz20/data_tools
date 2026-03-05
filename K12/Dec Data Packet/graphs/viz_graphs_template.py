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
FONT_FAMILY = 'Lato Bold'
FONT_SIZE = 30
font_size_graph = 45
font_mod = 5
# Common layout template
def get_base_layout(width=500, height=500, **kwargs):
    margin_type = kwargs.get('margin_type', False)
    if margin_type == False:
        
            margins = dict(l=10, r=10, t=10, b=10)
    else:
        if isinstance(margin_type, list):
            margins = dict(l=margin_type[0],r=margin_type[1], t=margin_type[2],b =margin_type[3])
        else:
            margins = dict(l=70, r=20, t=40, b=60)
    
    return dict(
        font=get_base_text(FONT_SIZE),
        plot_bgcolor='white',
        paper_bgcolor='white',
        # title=dict(text=title, x=0.5, xanchor='center'),
        showlegend=False,
        width=width,
        height=height,
        margin=margins
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
        elif options == 'bluegreen_dual':
            return [hunt_blue, hunt_acc_green]
        elif options == 'other':
            return [hunt_blue,hunt_acc_aq_blue, hunt_red, hunt_acc_orange, hunt_acc_green, hunt_purple]

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
def get_base_text(font_size, weight='normal', **kwargs):
    """
    Returns a font dictionary for Plotly text styling.
    Ensures consistent use of the Lato font across environments.
    """
    color = kwargs.get('color', hunt_darkgray)
    bold = kwargs.get('bold', False)

    # Normalize bold variants to CSS-like weights
    if bold == True:
        weight = 'bold'
    elif bold == 'super':
        weight = 700  # same as bold; you could map to 800 if you want stronger emphasis

    # Lato is a single family name in most environments
    fam = 'Lato'

    return dict(
        size=font_size,
        color=color,
        family=fam,
        weight=weight
    )
def add_letter_spacing(text):
    # Use thin space (U+2009) for subtle spacing
    return '\u2009'.join(text)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
import textwrap

def wrap_category_name(name, width=20):
    """Wrap category names using textwrap module"""
    return '<br>'.join(textwrap.wrap(name, width=width))

def prepare_data_with_na_handling(data_list, na_text_replacement = 'n/a'):
    processed_values = []
    text_labels = []

    for val in data_list:
        # --- Handle missing, text, or invalid entries ---
        # print(val)
        if pd.isna(val) or str(val).strip().lower() in ['n/a', 'na', '', 'none']:
            # print(f'this is na: {val}')

            processed_values.append(0)
            text_labels.append(na_text_replacement)
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
            text_labels.append(na_text_replacement)
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
            text_labels.append(f"{percent_val:.0%}")  # Always use .0% for no decimals


            # if float(percent_val).is_integer():
            #     text_labels.append(f"{percent_val:.0%}")
            # else:
            #     text_labels.append(f"{percent_val:.1%}")
                    



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
#===Page 1: Enrollment  
# ============================================================================
#Enrollment Total

# ! 1.1
def graph_1_1(years, values, width, height):
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
        line=dict(color=hunt_blue, width=7),
        marker=dict(size=23, color=hunt_blue),
    ))
    
    # Update layout
    fig.update_layout(
        get_base_layout(width, height),
        xaxis=dict( 
            showgrid=False, 
            showline=True, 
            showticklabels = True,
            ticklabeloverflow='allow',

            linewidth = 1, 
            linecolor=hunt_darkgray,
            tickfont = get_base_text(font_size_graph-(font_mod*2)),
            tickvals=years,  # your list of strings
            ticktext=years   # same text to display
            ),
        yaxis=dict(
            range=[ymin,ymax],
            showgrid=False, 
            gridcolor='lightgray', 
            showline=True, 
            linewidth = 1, 
            linecolor=hunt_darkgray,
            ),
        
    )
    
    return fig
#By Race and Ethnicity

# ! 1.2
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

    print(state)
    # Calculate totals
    total_state_series = sum(state_series)
    total_us_series = sum(us_series)
    print('STATE SUM')
    print(state_series)
    print(total_state_series)
    
    print('US SUM')
    print(us_series)
    print(total_us_series)
    
    
    # Calculate percentages
    pct_state_series = [((val / total_state_series)*100) if total_state_series > 0 else 0 for val in state_series]
    pct_us_series = [((val / total_us_series)*100) if total_us_series > 0  else 0 for val in us_series]

    print('STATE VALS')
    print(pct_state_series)
    # print(total_state_series)
    
    print('US VALS')
    print(pct_us_series)
    # print(total_us_series)

    text_pct_state_series = [x if x > 3 else '' for x in pct_state_series]
    text_pct_us_series = [x if x > 3 else '' for x in pct_us_series]
    
    print('STATE TEXT')
    print(text_pct_state_series)
    # print(total_state_series)
    
    print('US TEXT')
    print(text_pct_us_series)
    # print(total_us_series)
    


    text_pct_state_series = [
    f"{x:.0f}%" if isinstance(x, (int, float)) else x
    for x in text_pct_state_series
    ]
    text_pct_us_series = [
        f"{x:.0f}%" if isinstance(x, (int, float)) else x
        for x in text_pct_us_series
    ]


    # Define colors for 6 race&ethnicity categories
    colors = get_colors(categories)
    
    # stop = len(categories)-1
    


    fig = go.Figure()
    
    

    
    # Add traces for each category in us series
    for i, category in enumerate(categories):
        fig.add_trace(go.Bar(
            name=category,
            y=[add_letter_spacing('UNITED STATES')],
            x=[pct_us_series[i]],
            orientation='h',
            marker=dict(color=colors[i]),
            text=[text_pct_us_series[i]],
            textposition='inside',
            insidetextanchor = 'middle',
            textfont=get_base_text(font_size_graph,bold = 'super', color = 'white'),
            legendgroup=category,
            showlegend=False  # Only show legend once per category
        ))
    # Add traces for each category in state series 
    for i, category in enumerate(categories):
        fig.add_trace(go.Bar(
            name=category,
            y=[add_letter_spacing(full_state_name.upper())],
            x=[pct_state_series[i]],
            orientation='h',
            marker=dict(color=colors[i]),
            text=[text_pct_state_series[i]],
            textposition='inside',
            insidetextanchor = 'middle',
            textfont=get_base_text(font_size_graph,bold = 'super', color = 'white'),
            # hovertemplate=f'{category}<br>Count: {state_series[i]:,}<br>Percentage: {pct_state_series[i]:.1f}%<extra></extra>',
            legendgroup=category,
            showlegend=False
        ))
    fig.update_layout(
        **get_base_layout(graph_wd, graph_h, margin_type = True),
        barmode='stack',
        bargap=0.2,
        xaxis=dict(
            # title='Percentage (%)',
            visible=False,
            showgrid=True,
            showline=False,
            linecolor=hunt_darkgray,
            range=[0, 100]
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            linecolor=hunt_darkgray,
            tickfont = get_base_text(28),
            categoryorder='array',  # ADD THIS
            categoryarray=[add_letter_spacing('UNITED STATES'), add_letter_spacing(full_state_name.upper())],
            ticklabelstandoff=10

        )
    )
    
    return fig


# ! 1.3
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
            y=[add_letter_spacing('UNITED STATES')],
            x=[us_x_vals[i]],
            orientation='h',
            marker=dict(color=colors[i]),
            text=f'{us_x_vals[i]:.0f}%',
            textposition='inside',
            insidetextanchor = 'middle',
            textfont=get_base_text(font_size_graph, bold= True, color = 'white'),
            # hovertemplate=f'{category}<br>Count: {us_series[i]:,}<br>Percentage: {pct_us_series[i]:.1f}%<extra></extra>',
            legendgroup=category,
            showlegend=False  # Only show legend once per category
        ))
    # Add traces for each category in state series 
    for i, category in enumerate(categories):
        fig.add_trace(go.Bar(
            name=category,
            y=[add_letter_spacing(full_state_name.upper())],
            x=[state_x_vals[i]],
            orientation='h',
            marker=dict(color=colors[i]),
            text=f'{state_x_vals[i]:.0f}%',
            textposition='inside',
            insidetextanchor = 'middle',
            textfont=get_base_text(font_size_graph, bold= True, color = 'white'),
            # hovertemplate=f'{category}<br>Count: {state_series[i]:,}<br>Percentage: {pct_state_series[i]:.1f}%<extra></extra>',
            legendgroup=category,
            showlegend=False
        ))
    fig.update_layout(
        **get_base_layout(graph_wd, graph_h,margin_type = True),
        barmode='stack',
        bargap=0.2,
        xaxis=dict(
            # title='Percentage (%)',
            visible=False,
            showgrid=True,
            showline=False,
            linecolor=hunt_darkgray,
            range=[0, 100]
        ),
        yaxis=dict(
            # title='',
            showgrid=False,
            showline=False,
            linecolor=hunt_darkgray,
            tickfont=get_base_text(28),
            categoryorder='array',  # ADD THIS
            categoryarray=[
            add_letter_spacing('UNITED STATES'),
            add_letter_spacing(full_state_name.upper())],
            # ticklabelposition = 'outside left',
            ticklabelstandoff=10
    )

    )


    return fig

# ! 1.4
#by Locale
def graph_1_4(input_dict, us_dict, state,graph_wd, graph_h):
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
    
    full_state_name = state_ref_r.get(state)
    cats = ['city', 'suburban', 'town', 'rural']
    colors = get_colors(options = 'other')
    colors = colors[:len(cats)]
    inp_dict = {k:v for k,v in input_dict.items() if 'state' not in str(k) }
    us_inp_dict = {k:v for k,v in us_dict.items() if 'state' not in str(k) }


    inp_dict = {k:(v if v > .03 else '') for k,v in inp_dict.items()}
    us_inp_dict = {k:(v if v > .03 else'') for k,v in us_inp_dict.items()}
    
    print(inp_dict)
    print(us_inp_dict)

    
    inp_dict = {k: (f"{v:.0%}" if isinstance(v, (int, float)) else v) for k,v in inp_dict.items()}
    us_inp_dict = {k: (f"{v:.0%}" if isinstance(v, (int, float)) else v) for k,v in us_inp_dict.items()}

    

    # text_pct_state_series = [
    # f"{x:.0f}%" if isinstance(x, (int, float)) else x
    # for x in text_pct_state_series
    # ]
    # text_pct_us_series = [
    #     f"{x:.0f}%" if isinstance(x, (int, float)) else x
    #     for x in text_pct_us_series
    # ]

    

    fig = go.Figure()


    # Add traces for each category in us series
    for i, category in enumerate(cats):
        fig.add_trace(go.Bar(
        name=category,
        y=[add_letter_spacing('UNITED STATES')],
        x=[us_dict.get(category)],
        orientation='h',
        marker=dict(color=colors[i]),
        text=us_inp_dict.get(category),
        textposition='inside',
        insidetextanchor = 'middle',
        textfont=get_base_text(font_size_graph, bold= True, color = 'white'),
        # hovertemplate=f'{category}<br>Count: {us_series[i]:,}<br>Percentage: {pct_us_series[i]:.1f}%<extra></extra>',
        legendgroup=category,
        showlegend=False  # Only show legend once per category
        ))
    # Add traces for each category in state series 
    for i, category in enumerate(cats):
        fig.add_trace(go.Bar(
        name=category,
        y=[add_letter_spacing(full_state_name.upper())],
        x=[input_dict.get(category)],
        orientation='h',
        marker=dict(color=colors[i]),
        text=inp_dict.get(category),
        textposition='inside',
        insidetextanchor = 'middle',
        textfont=get_base_text(font_size_graph, bold= True, color = 'white'),
        # hovertemplate=f'{category}<br>Count: {state_series[i]:,}<br>Percentage: {pct_state_series[i]:.1f}%<extra></extra>',
        legendgroup=category,
        showlegend=False
        ))
    fig.update_layout(
        **get_base_layout(graph_wd, graph_h,margin_type = True),
        barmode='stack',
        bargap=0.2,
        xaxis=dict(
        # title='Percentage (%)',
        visible=False,
        showgrid=True,
        showline=False,
        linecolor=hunt_darkgray,
        range=[0, 1]
        ),
        yaxis=dict(
        # title='',
        showgrid=False,
        showline=False,
        linecolor=hunt_darkgray,
        tickfont=get_base_text(28),
        categoryorder='array',  # ADD THIS
        categoryarray=[
        add_letter_spacing('UNITED STATES'),
        add_letter_spacing(full_state_name.upper())],
        # ticklabelposition = 'outside left',
        ticklabelstandoff=10
        )

    )


    return fig



# ============================================================================
#===Page 2: State Assessment Results
# ============================================================================
def graph_2_state_assess_graph(df, state):
    
    categories = get_col_uniq_vals(df['subject'])
    y_max = max(df['value'])+10 if len(df) > 0 else 100
    
    # Ensure all years are present
    all_years = ['2023', '2024', '2025']
    school_years = ['2022-2023', '2023-2024', '2024-2025']
    
    colors = [hunt_blue, hunt_acc_green]
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
                text_list.append("--")
        
        fig.add_trace(go.Bar(
            name=category,
            x=years_list,
            y=values_list,
            marker=dict(
                color=colors[i],
                line=dict(width=0)),
            text=text_list,
            textfont = get_base_text(font_size_graph, bold = True),
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
            linecolor=hunt_darkgray,
            tickfont = get_base_text(25),
        )
    )
    
    return fig


# ============================================================================
#===Page 3: NAEP Assessment Results
# ============================================================================


def graph_naep_overall(df, y_min,offset):
    

    fig = go.Figure()
    # val_list = df[col_label].to_list()
    df['state'] = df['state'].apply(lambda x: float(safe_format(x)))
    df['us'] = df['us'].apply(lambda x: float(safe_format(x)))
    # y_max = max(val_list) + 5


    #actual data points
    # US only data
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['us'],
        mode='lines+markers',
        line=dict(color=hunt_gray50, width=6),
        marker=dict(size=23),
        showlegend=True
    ))
    # State only data
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['state'],
        mode='lines+markers',
        line=dict(color=hunt_purple, width=6),
        marker=dict(size=23),
        showlegend=True
    ))


    # Add text labels
    #us text lables
    # us_text_y_positions = [float(x)+offset for x in us_df[col_label]]

    fig.add_trace(go.Scatter(
        x=df['year'].to_list(),
        y=df['us_position'],  # Use calculated positions
        mode='text',
        showlegend=False,
        text=df['us'].round(0).astype(int).astype(str),  # Round for cleaner display
        textfont=get_base_text(font_size_graph+font_mod, bold = True),
        texttemplate='%{text:,.0f}%'
    ))
    #state text lables
    # state_text_y_positions = [float(x)-offset for x in df[col_label]]

    fig.add_trace(go.Scatter(
        x=df['year'].to_list(),
        y=df['state_position'],  # Use calculated positions
        mode='text',
        showlegend=False,
        text=df['state'],
        textfont=get_base_text(font_size_graph+font_mod, color = hunt_dark_purple, bold = True),
        texttemplate='%{text:,.0f}%'
    ))
    fig.update_yaxes(
            showticklabels=False,  # Hide tick labels
            showgrid=False,        # Hide gridlines
            zeroline=False,         # Hide zero line
            showline = False,
            range = [y_min,80]
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
#===Page 4: NAEP Assessment Results AND State Assessment compared
# ============================================================================
# get_census regions for analysis
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

    
# ! 4.1-4
#regions graph
def graph_4_regions(df, offset_m, graph_w, graph_h, max_states=6, **kwargs):
    """
    Create horizontal bar chart for regions
    
    Parameters:
    - df: DataFrame with the data
    - offset_m: Multiplier for y_max calculation
    - max_states: Maximum number of states to display (excluding US National)
    """

    debug = kwargs.get('debug', False)
    df = df.copy()
    df['at_or_above_proficient'] = pd.to_numeric(df['at_or_above_proficient'], errors='coerce')
    
    # Separate US National from states
    us_row = df[df['jurisdiction'] == 'National'].reset_index(drop=True)
    us_row.loc[0,'color'] = hunt_darkgray
    states_df = df[df['jurisdiction'] != 'National']
    
    # Always include the highlighted state (color #63007E)
    highlighted_state = states_df[states_df['color'] == '#500066']
    other_states = states_df[states_df['color'] != '#500066'].reset_index(drop=True)
    
    # Get top states (minus 1 to account for highlighted state)
    # Sort by value to get the top performing states
    top_other_states = other_states.nlargest(max_states - 1, 'at_or_above_proficient').sort_index(ascending=False)
    
    # Combine highlighted state with other top states
    selected_states = pd.concat([highlighted_state, top_other_states])
    selected_states = selected_states.sort_values(by='at_or_above_proficient', ascending = True).reset_index(drop = True)

    # Sort states by value (ascending for bottom to top display)
    # selected_states = selected_states.sort_values('at_or_above_proficient', ascending=True)
    
    # Combine with US at the top (will be displayed at top due to reverse later)
    df_display = pd.concat([selected_states, us_row])
    
    states = df_display['jurisdiction']
    values = df_display['at_or_above_proficient']
    if debug == True:
        print(df_display.to_string(max_colwidth=30))
    # Calculate y_max excluding NA values
    valid_values = [v for v in values.to_list() if v > 0.01]
    y_max = (max(valid_values)*offset_m) if valid_values else offset_m
    print(valid_values)
    print(y_max)
    
    colors = df_display['color'].to_list()
    fig = go.Figure()
   
    custom_order = df_display['state_abrv'].to_list()

    # custom_order.reverse()
    print(custom_order)

    fig.add_trace(go.Bar(
        y=states,
        x=values,
        orientation='h',
        marker=dict(color=colors),
        text=values,
        textfont=get_base_text(font_size_graph-(font_mod*2), bold = True),
        textposition='outside',
        texttemplate='%{text:,.0f}%'
    ))
    margins_list = [2,0,10,0]
    fig.update_layout(
        **get_base_layout(graph_w, graph_h), #margin_type = margins_list),
        xaxis=dict(range=[0, y_max], showgrid=False, showline=True, visible=False),

        yaxis=dict(showgrid=False, showline=False, categoryorder='array', categoryarray=custom_order, ticklabelstandoff = 10)
    )
   
    return fig

# ! 4.5
def graph_state_cut(df, col_label, state, years, graph_w, graph_h):

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
        line=dict(color=hunt_purple, width=7),
        marker=dict(size=20),
        showlegend=False,
        zorder=10
    ))
    # line
    text_labels = [''] * (len(df['year']) - 1) + [str(subject_line)]  # Show label only on last point
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=[subject_line]*len(df['year']),
        mode='lines',
        line=dict(color=hunt_gray50, width=7),
        marker=dict(size=20),
        showlegend=False,
        # text=text_labels,
        # textfont=get_base_text(font_size_graph, bold = True),
        # textposition='top left',
        zorder=2

    ))
    fig.update_layout(get_base_layout(graph_w, graph_w))
    

    
    return fig

# ============================================================================
#===Page 5: NAEP BY SUBGROUP
# ============================================================================


def graph_5_multi_series(df, col_label, group_col, years, **kwargs):
    label_all = kwargs.get('label_all', False)
    
    
    
    # FILTER OUT ‡ symbols and invalid data FIRST
    df_clean = df.copy()
    df_clean[col_label] = df_clean[col_label].replace('‡', np.nan)
    df_clean[col_label] = pd.to_numeric(df_clean[col_label], errors='coerce')
    df_clean = df_clean.dropna(subset=[col_label])
    # print(df_clean.to_string())
    # GET CATEGORIES ONCE AND KEEP ORDER CONSISTENT
    categories = sorted(df_clean[group_col].unique())  # Sort for consistency!
    # print('CATEGORIES')

    # print(len(categories))

    if len(categories)==2:
        colors = get_colors(categories, options='bluegreen_dual')
    else:
        colors = get_colors(categories)
    
    # CREATE COLOR MAP to ensure consistency
    color_map = {cat: colors[i] for i, cat in enumerate(categories)}
    fig = go.Figure()
    val_list = df_clean[col_label].to_list()
    val_list = [float(x) for x in val_list]
    y_max = max(val_list) + 5
    # print(val_list)
    # print(y_max)

    # Get latest year data for each subgroup
    latest_data = []
    max_year = max(years)
    
    for r in categories:  # Use the same categories list
        subgroup_result = df_clean[df_clean[group_col] == r].copy()  # Add .copy()!
        
        valid_years = subgroup_result['year'].dropna().unique()
        if len(valid_years) == 0:
            continue
        latest_year = max(valid_years)
        
        latest_row = subgroup_result[subgroup_result['year'] == latest_year].iloc[0]
        latest_value = float(latest_row[col_label])
        
        latest_data.append({
            'category': r,
            'year': latest_year,
            'value': latest_value,
            'subgroup_result': subgroup_result,
            'is_max_year': latest_year == max_year,
            'color': color_map[r]  # Store color here!
        })
    

    
    if label_all == True:

        for cat in categories:  # Use categories directly instead of enumerate
            # Get the color for this category
            cat_color = color_map[cat]
            
            # Determine text position based on category name
            if re.search(r'[Nn]on?t?', str(cat)):
                pos = 'top center'
            else:
                pos = 'bottom center'
            # print(cat)
            subgroup_result = df_clean[df_clean[group_col] == cat]  # Use df_clean!
            # print(subgroup_result)
            fig.add_trace(go.Scatter(
                x=subgroup_result['year'],
                y=subgroup_result[col_label],
                mode='lines+markers',
                line=dict(color=cat_color, width=5),  # Use color_map
                marker=dict(size=15),
                showlegend=True,
                name=cat,  # Add name for legend
                text=subgroup_result[col_label],
                textfont=get_base_text(font_size_graph, bold=True),
                textposition=pos,  # Use the pos variable you calculated
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
            ), 
            yaxis=dict(
                range=[0,100],
                visible=False
            )
        )
    else:
        # Separate data into two groups
        max_year_data = [d for d in latest_data if d['is_max_year']]
        earlier_year_data = [d for d in latest_data if not d['is_max_year']]
        
        # SORT max_year data by value
        max_year_data.sort(key=lambda x: x['value'])
        
        # Calculate evenly spaced positions
        if len(max_year_data) > 1:
            min_val = max_year_data[0]['value']
            n_labels = len(max_year_data)
            evenly_spaced_positions = [min_val + i * (90 - min_val) / (n_labels - 1) for i in range(n_labels)]
        elif len(max_year_data) == 1:
            evenly_spaced_positions = [max_year_data[0]['value']]
        else:
            evenly_spaced_positions = []
        
        # ADD CONNECTOR LINES FOR MAX YEAR
        for i, data_item in enumerate(max_year_data):
            label_y = evenly_spaced_positions[i]
            
            fig.add_shape(
                type='line',
                x0=data_item['year'],
                y0=data_item['value'],
                x1=data_item['year'] + 0.5,
                y1=label_y,
                line=dict(color=data_item['color'], width=3, dash='dot')  # Use stored color
            )
            
            fig.add_annotation(
                x=data_item['year'] + 0.5,
                y=label_y,
                text=f"{data_item['value']:.0f}%",
                showarrow=False,
                xanchor='left',
                font=get_base_text(font_size_graph, bold=True),
                bgcolor='rgba(255,255,255,0.8)',
                borderpad=3
            )
        
        # ADD CONNECTOR LINES FOR EARLIER YEARS
        for data_item in earlier_year_data:
            offset = y_max-5
            print(offset)
            label_y = offset
            
            fig.add_shape(
                type='line',
                x0=data_item['year'],
                y0=data_item['value'],
                x1=data_item['year'] + 0.3,
                y1=label_y,
                line=dict(color=data_item['color'], width=3, dash='dot')  # Use stored color
            )
            
            fig.add_annotation(
                x=data_item['year'] + 0.3,
                y=label_y,
                text=f"{data_item['value']:.0f}%",
                showarrow=False,
                xanchor='left',
                font=get_base_text(font_size_graph, bold=True),
                bgcolor='rgba(255,255,255,0.8)',
                borderpad=3
            )
        
        # ADD MAIN LINE TRACES - USE CATEGORIES IN SAME ORDER
        for cat in categories:  # Use categories, not enumerate
            # Find the data item for this category
            data_item = next((d for d in latest_data if d['category'] == cat), None)
            if data_item is None:
                continue
                
            subgroup_result = data_item['subgroup_result']
            
            fig.add_trace(go.Scatter(
                x=subgroup_result['year'],
                y=subgroup_result[col_label],
                mode='lines+markers',
                name=cat,
                line=dict(color=data_item['color'], width=5),
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
                tickvals=years,
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
        # # Separate data into two groups: max_year vs earlier years
        # max_year_data = [d for d in latest_data if d['is_max_year']]
        # earlier_year_data = [d for d in latest_data if not d['is_max_year']]
        
        # # SORT max_year data by value for even spacing
        # max_year_data.sort(key=lambda x: x['value'])
        
        # # Calculate evenly spaced positions for max_year labels only
        # if len(max_year_data) > 1:
        #     min_val = max_year_data[0]['value']
        #     max_val = max_year_data[-1]['value']
        #     n_labels = len(max_year_data)
        #     evenly_spaced_positions = [min_val + i * (90 - min_val) / (n_labels - 1) for i in range(n_labels)]
        # elif len(max_year_data) == 1:
        #     evenly_spaced_positions = [max_year_data[0]['value']]
        # else:
        #     evenly_spaced_positions = []
        
        # # ADD THIS DEBUG CODE
        # print("\n=== LABEL POSITIONS DEBUG ===")
        # for i, data_item in enumerate(max_year_data):
        #     print(f"{data_item['category']}: year={data_item['year']}, value={data_item['value']:.1f}%")
        #     # Check what the actual last point in the line data is
        #     last_point = data_item['subgroup_result'].iloc[-1]
        #     print(f"  Last plotted point: year={last_point['year']}, value={last_point[col_label]}")
        # print("=" * 40)
        
        # # ADD CONNECTOR LINES FOR MAX YEAR (with even spacing)
        # for i, data_item in enumerate(max_year_data):
        #     idx = categories.index(data_item['category'])
        #     label_y = evenly_spaced_positions[i]
            
        #     # Add dotted connector line
        #     fig.add_shape(
        #         type='line',
        #         x0=data_item['year'],
        #         y0=data_item['value'],
        #         x1=data_item['year'] + 0.5,
        #         y1=label_y,
        #         line=dict(
        #             color=colors[idx],
        #             width=3,
        #             dash='dot'
        #         )
        #     )
            
        #     # Add text annotation
        #     fig.add_annotation(
        #         x=data_item['year'] + 0.5,
        #         y=label_y,
        #         text=str(safe_format(data_item['value'])) + '%',
        #         showarrow=False,
        #         xanchor='left',
        #         font=get_base_text(font_size_graph, bold=True),
        #         bgcolor='rgba(255,255,255,0.8)',
        #         borderpad=3
        #     )
        
        # # ADD CONNECTOR LINES FOR EARLIER YEARS (close to actual value)
        # for data_item in earlier_year_data:
        #     idx = categories.index(data_item['category'])
        #     # Position label just slightly above/below the actual value
        #     offset = 3  # Small offset
        #     label_y = data_item['value'] + offset
            
        #     # Add shorter dotted connector line
        #     fig.add_shape(
        #         type='line',
        #         x0=data_item['year'],
        #         y0=data_item['value'],
        #         x1=data_item['year'] + 0.3,  # Shorter horizontal line
        #         y1=label_y,
        #         line=dict(
        #             color=colors[idx],
        #             width=3,
        #             dash='dot'
        #         )
        #     )
            
        #     # Add text annotation
        #     fig.add_annotation(
        #         x=data_item['year'] + 0.3,
        #         y=label_y,
        #         text=str(safe_format(data_item['value'])) + '%',
        #         showarrow=False,
        #         xanchor='left',
        #         font=get_base_text(font_size_graph, bold=True),
        #         bgcolor='rgba(255,255,255,0.8)',
        #         borderpad=3
        #     )
        
        # # ADD MAIN LINE TRACES LAST (so markers appear on top)
        # for idx, r in enumerate(categories):
        #     subgroup_result = df[df[group_col] == r]
            
        #     fig.add_trace(go.Scatter(
        #         x=subgroup_result['year'],
        #         y=subgroup_result[col_label],
        #         mode='lines+markers',
        #         name=f'{r}',
        #         line=dict(color=colors[idx], width=5),
        #         marker=dict(size=15),
        #         showlegend=True
        #     ))
        
        # fig.update_layout(
        #     **get_base_layout(700, 450),
        #     xaxis=dict(
        #         showgrid=False, 
        #         showline=True,
        #         linecolor=hunt_darkgray, 
        #         tickmode='array', 
        #         tickvals=years,
        #     ),
        #     yaxis=dict(
        #         range=[0, 100],
        #         showgrid=False, 
        #         showline=True, 
        #         linecolor=hunt_darkgray, 
        #         ticksuffix='%'
        #     )
        # )
    

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
# ===Page 6: NON academic metrics
# ============================================================================
# --------------------------------------------


# ! 6.1
import plotly.graph_objects as go
def graph_chron_abs(df, col_label,graph_w, graph_h):
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
        'Native Hawaiian/Other Pacific Islander',
        'Asian',
        'Hispanic',
        'Black',
        'White',
        'Two or More Races'
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
    print(complete_df.to_string(max_colwidth=30))
    # Merge with existing data
    df_merged = complete_df.merge(df[['group', 'value']], on='group', how='left')
    print('looking at groups ')
    print(df.to_string(max_colwidth = 30))
    print('merged')
    print(df_merged.to_string(max_colwidth=30))
    # Add group_key and order
    df_merged['group_key'] = df_merged['group'].map(remap).fillna(df_merged['group'])
    df_merged['order'] = df_merged['group_key'].apply(get_order)
    df_sorted = df_merged.sort_values('order')
    df_sorted.loc[df_sorted['group']=='Two or More','group'] = 'Two or More Races'

    # Get colors for all groups
    categories = df_sorted['group'].tolist()
    colors = get_colors(categories)
    
    # Create text labels (show "n/a" for missing values)
    text_labels = df_sorted['value'].apply(
        lambda x: f"{x:.0f}%" if pd.notna(x) else '--'
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
        textfont = get_base_text(font_size_graph,bold = True),
        marker_color=colors
    ))
   
    valid_values = [v for v in df_sorted['value'] if v > 0.01]
    y_max = (max(valid_values) * 1.25) if valid_values else 1.0
    # Layout

    cat_order = ['American Indian or Alaska Native','Native Hawaiian or Other Pacific Islander', 'Two or More Races']
    fig.update_layout(
        xaxis=dict(showgrid=False, 
                    showline=True, 
                    linecolor='gray',
                    tickmode='array',
                    tickvals=list(range(len(categories))),
                    ticktext=[wrap_category_name(c,width = 16) for c in categories],
                    tickformat=".0%",
                    tickangle=0),

        yaxis = dict(
            range = [0,100]),
        **get_base_layout(graph_w, graph_h)
    )
   
    return fig
# --------------------------------------------
# ! 6.2
def graph_other_chron_abs(df):
    import plotly.graph_objects as go
    import pandas as pd
    categories = list(df.columns)[3:]
    print(categories)

    # Use the NA handling function
    state_data, state_text = prepare_data_with_na_handling(df.iloc[0].values.tolist()[3:], na_text_replacement='-')
    
    state_text = [
    f"{x:.0%}" if isinstance(x, (int, float)) else x
    for x in state_text
    ]
   
    # Calculate y_max excluding NA values
    valid_values = [v for v in state_data if v > 0.01]
    y_max = (max(valid_values) + 0.10) if valid_values else 1.0

    colors = [hunt_purple if re.search(r'^[Aa]ll',v) else hunt_light_purple for i,v in enumerate(categories) ]
    # Create grouped bar chart
    fig = go.Figure()
    # Add state bar trace
    fig.add_trace(go.Bar(
        x=df.columns,
        y=state_data,
        marker=dict(
            color=[x if v > 0.01 else hunt_gray30 for i, (x,v) in enumerate(zip(colors,state_data))],
            line=dict(width=0)
        ),
        text=state_text,
        texttemplate='%{text}',
        textposition='outside', 
        textfont = get_base_text(font_size_graph, bold = True)
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
        ticktext=[wrap_category_name(c,width = 15) for c in categories]
    ))
    return fig


# --------------------------------------------
# ! 6.3
def graph_oos(df, us_df, state, graph_w, graph_h):
    
    
    cat_order = ['American Indian or Alaska Native', 'Asian', 'Native Hawaiian or Other Pacific Islander', 'Hispanic', 'Black', 'White', 'Two or More Races']
    df = df.loc[:,cat_order]
    us_df = us_df.loc[:,cat_order]
    # print(f'raw_graph_input: {'\n'}{df.to_string()}{'\n'}')
    categories = list(df.columns)
    # print(categories)

    # Use the NA handling function
    state_data, state_text = prepare_data_with_na_handling(df.iloc[0].values.tolist())
    us_data, us_text = prepare_data_with_na_handling(us_df.iloc[0].values.tolist())
    
    state_text = [
    f"{x:.0%}" if isinstance(x, (int, float)) else x
    for x in state_text
    ]
    us_text = [
        f"{x:.0%}" if isinstance(x, (int, float)) else x
        for x in us_text
    ]
    all_data = state_data+us_data
    
    og_y_max = max(all_data)
    y_max = max(all_data)
    print(f'og ymax: {y_max}')
    if y_max>.70:
        y_max += .30
    else:
        y_max += .10
    print(f'ymax: {y_max}')
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
        textposition='outside', 
        textfont = get_base_text(font_size_graph, bold = True)
        # name='Dataset 1'  # Legend label
    ))
    # Add us bar trace
    fig.add_trace(go.Bar(
        x=us_df.columns,
        y=us_data,
        marker=dict(
            color=[hunt_gray50 if v > 0.01 else hunt_gray30 for v in us_data],
            line=dict(width=0)
        ),
        text=us_text,
        texttemplate='%{text}',
        textposition='outside',
        textfont=get_base_text(font_size_graph, bold = True)
        # name='Dataset 1'  # Legend label
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
        tickvals = categories,
        ticktext=[wrap_category_name(c, 16) for c in categories]

    )
)
    return og_y_max, fig
    

# ============================================================================
#===Page 7: Graduation Rate Analysis
# ============================================================================


def convert_to_percent(input_list):
    arr = np.array(input_list, dtype=np.float64)
    arr = arr[~np.isnan(arr)]

    if arr.size == 0:
        return 

    if arr.max() > 1:
        return (arr / 100).tolist()
    return arr.tolist()


# ! 7.1
def graph_grad_rate(df, graph_w, graph_h):
    
    
    # Make a copy to avoid modifying the original
    df = df.copy()
    
    fig = go.Figure()
    
    #actual data points
    # US only data
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['us'],
        mode='lines+markers',
        line=dict(color=hunt_gray50, width=8),
        marker=dict(size=23),
        showlegend=True
    ))
    # State only data
    fig.add_trace(go.Scatter(
        x=df['year'],
        y=df['state'],
        mode='lines+markers',
        line=dict(color=hunt_purple, width=8),
        marker=dict(size=23),
        showlegend=True
    ))
    
    # Add text labels
    state_data, state_text = prepare_data_with_na_handling(df['state'].to_list(),'--')
    us_data, us_text = prepare_data_with_na_handling(df['us'].to_list(),'--')
    # print(state_text)
    # print(us_text)
    
    # Fix NaN positions BEFORE plotting
    # Calculate offset from non-NaN rows
    valid_us = df[df['us_position'].notna() & df['us'].notna()].copy()
    if not valid_us.empty:
        valid_us['offset'] = valid_us['us_position'] - valid_us['us']
        avg_offset = valid_us['offset'].mean()
    else:
        avg_offset = 0
    
    valid_state = df[df['state_position'].notna() & df['state'].notna()].copy()
    if not valid_state.empty:
        valid_state['offset'] = valid_state['state_position'] - valid_state['state']
        avg_state_offset = valid_state['offset'].mean()
    else:
        avg_state_offset = 0
    
    # Fill NaN positions
    for idx, row in df.iterrows():
        if pd.isna(row['us_position']) and pd.notna(row['us']):
            df.at[idx, 'us_position'] = row['us'] + avg_offset
            
        if pd.isna(row['state_position']) and pd.notna(row['state']):
            df.at[idx, 'state_position'] = row['state'] + avg_state_offset
    
    # print("After fixing positions:")
    # print(df[['year', 'us', 'us_position', 'state', 'state_position']].to_string())
    
    # US text labels
    fig.add_trace(go.Scatter(
        x=df['year'].to_list(),
        y=df['us_position'],  # Use calculated positions
        mode='text',
        showlegend=False,
        text=us_text,
        textfont=get_base_text(font_size_graph+font_mod, color=hunt_darkgray, bold=True),
    ))
    
    # State text labels
    fig.add_trace(go.Scatter(
        x=df['year'].to_list(),
        y=df['state_position'],  # Use calculated positions
        mode='text',
        showlegend=False,
        text=state_text,
        textfont=get_base_text(font_size_graph+font_mod, color=hunt_purple, bold=True),
    ))
    
    fig.update_yaxes(
        visible=False,
        showticklabels=False,
        showgrid=False,
        zeroline=False
    )
    fig.update_xaxes()
    fig.update_layout(
        **get_base_layout(graph_w, graph_h),
        xaxis=dict(
            showgrid=False, 
            showline=True, 
            linecolor=hunt_darkgray, 
            tickmode='array', 
            tickvals=df['year']
        ),
    )
    
    return fig
def wrap_category_name_other(name):
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


# ! 7.2
def graph_gradrate_re(df, us_df, state, asian_only):
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
    state_data, state_text = prepare_data_with_na_handling(df['grad_rate'].tolist(), '--')
    us_data, us_text = prepare_data_with_na_handling(us_df['grad_rate'].tolist(), '--')
    
    state_text = [
    f"{x:.0%}" if isinstance(x, (int, float)) else x
    for x in state_text
    ]
    us_text = [
        f"{x:.0%}" if isinstance(x, (int, float)) else x
        for x in us_text
    ]

    if state in asian_only:
        state_text = [v if not re.search('[Aa]sian', str(x)) else v+'*' for (x,v) in zip(categories,state_text)]


    # Calculate y_max excluding NA values
    valid_values = [v for v in state_data + us_data if v > 0.01]
    y_max = (max(valid_values) + 0.20) if valid_values else 1.0
    
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
        textposition='outside', 
        textfont = get_base_text(font_size_graph, bold = True)
        
    ))
    
    # US bar
    fig.add_trace(go.Bar(
        x=categories,
        y=us_data,
        name='US',
        marker=dict(
            color=[hunt_gray50 if v > 0.01 else hunt_gray30 for v in us_data],
            line=dict(width=0)
        ),
        text=us_text,
        textposition='outside',
        texttemplate='%{text}',
        textfont=get_base_text(font_size_graph, bold = True)
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
            tickformat='.0%',
            visible = False
        ),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor=hunt_darkgray,
            tickangle=0,
            tickmode='array',
            tickvals=list(range(len(categories))),
            ticktext=[wrap_category_name(c,15) for c in categories]        )
    )
    fig.update_xaxes(type='category')
    return fig

# ! 7.3
def graph_gradrate_other_subgroup(categories, df, us_df, state):
    # Standardize group names if needed
    
    # Align both datasets to the same category order
    df = df.set_index('group').reindex(categories).reset_index()
    us_df = us_df.set_index('group').reindex(categories).reset_index()

    state_data, state_text = prepare_data_with_na_handling(df['grad_rate'].tolist(),'--')
    us_data, us_text = prepare_data_with_na_handling(us_df['grad_rate'].tolist(), '--')
    # print('state info')    
    # print(state_data)
    # print(state_text)
    # print('us info')    
    # print(us_data)
    # print(us_text)

    y_max = max(state_data + us_data) + 0.10

    fig = go.Figure()

    # State bar
    fig.add_trace(go.Bar(
        x=categories,
        y=state_data,
        name='% of CTE',
        marker=dict(color=hunt_purple, line=dict(width=0)),
        text=state_text,
        textposition='outside',
        # text_template = state_text,
        # texttemplate=['%{text}' if str(x) == '--' else '%{text:,.0%}' for x in state_text],
        textfont=get_base_text(font_size_graph, bold = True)
    ))

    # US bar
    fig.add_trace(go.Bar(
        x=categories,
        y=us_data,
        name='% of Enrollment',
        marker=dict(color=hunt_gray50, line=dict(width=0)),
        text=us_text,

        textposition='outside',
        # texttemplate='%{text:,.0%}',
        textfont=get_base_text(font_size_graph, bold = True)
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
            ticktext=[wrap_category_name(c, 30) for c in categories]),
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
        tickfont=get_base_text(45)
        )
    
                     

    return fig


# ============================================================================
#===Page 8: Dropouts, CTE concentrators, and AP CLASSES 
# ============================================================================
# ! 8.1

def graph_dropouts(df, us_df, state, debug = True):
    # Standardize group names if needed
    if debug == True:
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
    if debug == True:
        print("After mapping df groups:", df['group'].unique())
        print("After mapping us_df groups:", us_df['group'].unique())
        
    categories = ['Total', 'American Indian/Alaska Native', 'Asian/Pacific Islander', 
                  'Hispanic', 'Black', 'White', 'Two or More']
    # label_map = {
    label_categories = ['Two or More Races' if 'two or more' in str(x).lower() else x for x in categories]
    
    
    # Align both datasets to the same category order
    df = df.set_index('group').reindex(categories).reset_index()
    us_df = us_df.set_index('group').reindex(categories).reset_index()
    
    # Use the NA handling function
    state_data, state_text = prepare_data_with_na_handling(df['value'].tolist(), '--')
    us_data, us_text = prepare_data_with_na_handling(us_df['value'].tolist(), '--')
    
    state_text = [
    f"{x:.0%}" if isinstance(x, (int, float)) else x
    for x in state_text
    ]
    us_text = [
        f"{x:.0%}" if isinstance(x, (int, float)) else x
        for x in us_text
    ]




    # Calculate y_max excluding NA values
    valid_values = [v for v in state_data + us_data if v > 0.01]
    y_max = (max(valid_values) + 0.10) if valid_values else 1.0
    
    fig = go.Figure()
    print(state_data)
    # State bar
    fig.add_trace(go.Bar(
        x=categories,
        y=state_data,
        name=state,
        marker=dict(
            color=[hunt_purple if v > 0.01 else hunt_purple for v in state_data],
            line=dict(width=0)
        ),
        text=state_text,
        texttemplate='%{text}',
        textposition='outside', 
        textfont=get_base_text(font_size_graph,bold=True)
        
    ))
    
    # US bar
    fig.add_trace(go.Bar(
        x=categories,
        y=us_data,
        name='US',
        marker=dict(
            color=[hunt_gray50 if v > 0.01 else hunt_purple for v in us_data],
            line=dict(width=0)
        ),
        text=us_text,
        textposition='outside',
        texttemplate='%{text}',
        textfont=get_base_text(font_size_graph,bold=True)
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
            tickvals=list(range(len(label_categories))),
            ticktext=[wrap_category_name(c, 16) for c in label_categories],
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

# ! 8.2
def graph_8_cte(df, state):
    df = df[df['state']==state].reset_index(drop=True)
    df['order'] = df['group'].apply(lambda x: get_order(x))
    df = df.sort_values(by='order')
    print(df.to_string())
    categories = ["American Indian/ Alaska Native","Asian/ Pacific Islander","Hispanic","Black","White", "Two or  More Races"]
    by_cte_total_series = df['perc_o_cte'].to_list()
    by_enroll_series = df['perc_o_enr'].to_list()
    
    # Use the NA handling function
    total_data, total_text = prepare_data_with_na_handling(by_cte_total_series, '--')
    enr_data, enr_text = prepare_data_with_na_handling(by_enroll_series, '--')
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
   # %  of CTE concentrators 
    fig.add_trace(go.Bar(
        x=categories,
        y=enr_data,
        name=state,
        marker=dict(
            color=[hunt_blue if v > 0.01 else hunt_gray30 for v in enr_data],
            line=dict(width=0)
        ),
        text=enr_text,
        texttemplate='%{text}',
        textposition='outside',
        textfont=get_base_text(font_size_graph,bold=True)
        
    ))
    
    # % of subgroup enrollment 
    fig.add_trace(go.Bar(
        x=categories,
        y=total_data,
        name='US',
        marker=dict(
            color=[hunt_acc_green if v > 0.01 else hunt_gray30 for v in total_data],
            line=dict(width=0)
        ),
        text=total_text,
        textposition='outside',
        texttemplate='%{text}',
        textfont=get_base_text(font_size_graph,bold=True)
    ))

   
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
            tickangle=0,
            ticktext=[wrap_category_name(c,16) for c in categories]

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

# ! 8.3-5
def graph_ap(state_value, us_value, state, display_type):

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
                color=[hunt_purple, hunt_gray50],  # Different colors for each bar
                line=dict(width=0)
            ),
            text=values,
            textposition='outside',
            texttemplate='%{text:.0%}',
            textfont=get_base_text(font_size_graph,bold=True)
        ))
    elif display_type == 'number':
          y_max = max(values)+(max(values)*.1)
          fig.add_trace(go.Bar(
            x=categories,
            y=values,
            marker=dict(
                color=[hunt_purple, hunt_gray50],  # Different colors for each bar
                line=dict(width=0)
            ),
            text=values,
            textposition='outside',
            texttemplate='%{text:.0f}',
            textfont=get_base_text(font_size_graph,bold=True)))
    
    fig.update_layout(
        **get_base_layout(600, 400),
        bargap=0.15,
        xaxis=dict(
            showticklabels = False,
            showgrid=False,
            showline=True,
            linecolor=hunt_darkgray,
            tickangle=0  # No angle needed for just 2 bars
        ),
        yaxis=dict(
            range=[0, y_max+(y_max*.15)],
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
# ===Page 9: College Entrance
# ============================================================================
# ! 9.1

def graph_act_benchmarks(df, us_df, state, graph_w, graph_h):
    import plotly.graph_objects as go
    import pandas as pd
    categories = list(df.columns)[1:]
    print(categories)

    # Use the NA handling function
    state_data, state_text = prepare_data_with_na_handling(df.iloc[0].values.tolist()[1:])
    us_data, us_text = prepare_data_with_na_handling(us_df.iloc[0].values.tolist()[1:])
    

    # Create grouped bar chart
    fig = go.Figure()
    print(us_text)
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
        textposition='outside', 
        textfont=get_base_text(font_size_graph+font_mod,bold=True)
        # name='Dataset 1'  # Legend label
    ))
    # Add us bar trace
    fig.add_trace(go.Bar(
        x=df.columns,
        y=us_data,
        marker=dict(
            color=[hunt_gray50 if v > 0.01 else hunt_gray30 for v in us_data],
            line=dict(width=0)
        ),
        text=us_text,
        texttemplate='%{text}',
        textposition='outside',
        textfont=get_base_text(font_size_graph+font_mod,bold=True)
        # name='Dataset 1'  # Legend label
    ))

    fig.update_layout(
    **get_base_layout(graph_w, graph_h),
    barmode='group',
    bargap=0.15,
    bargroupgap=0.1,
    uniformtext=dict(
    mode='show',
    minsize=30
    ),
    yaxis=dict(
        range=[0, 1],
        tickformat='%'
    ),
    xaxis=dict(
        showgrid=False,
        showline=True,
        linecolor=hunt_darkgray,
        tickangle=0,
        tickmode='array',
        tickvals=list(range(len(categories))),
        ticktext=[wrap_category_name(c, 15) for c in categories]    )
)
    return fig
  


if __name__ == "__main__":
    # Example: Display a single graph
    fig = graph_1_1()
    fig.show()
