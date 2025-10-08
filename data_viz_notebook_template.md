# Data Analysis & Visualization Notebook

## Overview
Brief description of your analysis objectives and the data sources you'll be working with.

## Setup & Dependencies

```python
# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import sqlite3
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go

# Set visualization style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
```

## Data Source 1: CSV Files

### Load and Explore CSV Data
```python
# Load CSV data
df_csv = pd.read_csv('path/to/your/file.csv')

# Basic exploration
print(f"Shape: {df_csv.shape}")
print(f"Columns: {df_csv.columns.tolist()}")
df_csv.head()
```

### Data Cleaning & Preprocessing
```python
# Handle missing values, data types, etc.
df_csv.info()
df_csv.describe()
```

## Data Source 2: API Data

### Fetch Data from API
```python
# Example API call
api_url = "https://api.example.com/data"
headers = {'Authorization': 'Bearer YOUR_TOKEN'}

response = requests.get(api_url, headers=headers)
api_data = response.json()

# Convert to DataFrame
df_api = pd.DataFrame(api_data)
df_api.head()
```

## Data Source 3: Database Connection

### Connect to Database
```python
# SQLite example
conn = sqlite3.connect('database.db')
df_db = pd.read_sql_query("SELECT * FROM your_table", conn)

# Or using SQLAlchemy for other databases
# engine = create_engine('postgresql://user:password@localhost/dbname')
# df_db = pd.read_sql_query("SELECT * FROM your_table", engine)

df_db.head()
```

## Data Integration & Merging

### Combine Multiple Sources
```python
# Merge datasets
merged_df = pd.merge(df_csv, df_api, on='common_column', how='inner')

# Concatenate if needed
# combined_df = pd.concat([df1, df2], ignore_index=True)

print(f"Merged dataset shape: {merged_df.shape}")
merged_df.head()
```

## Exploratory Data Analysis

### Summary Statistics
```python
# Generate summary statistics
merged_df.describe()

# Check for missing values
merged_df.isnull().sum()
```

## Visualizations

### Basic Plots with Matplotlib/Seaborn

#### Distribution Analysis
```python
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Histogram
axes[0,0].hist(merged_df['numeric_column'], bins=30, alpha=0.7)
axes[0,0].set_title('Distribution of Numeric Column')

# Box plot
sns.boxplot(data=merged_df, y='numeric_column', ax=axes[0,1])
axes[0,1].set_title('Box Plot')

# Scatter plot
axes[1,0].scatter(merged_df['x_column'], merged_df['y_column'], alpha=0.6)
axes[1,0].set_title('Scatter Plot')

# Bar chart
category_counts = merged_df['category_column'].value_counts()
axes[1,1].bar(category_counts.index, category_counts.values)
axes[1,1].set_title('Category Distribution')

plt.tight_layout()
plt.show()
```

#### Correlation Analysis
```python
# Correlation heatmap
plt.figure(figsize=(10, 8))
correlation_matrix = merged_df.select_dtypes(include=[np.number]).corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Matrix')
plt.show()
```

### Interactive Visualizations with Plotly

#### Interactive Scatter Plot
```python
fig = px.scatter(merged_df, 
                 x='x_column', 
                 y='y_column',
                 color='category_column',
                 size='size_column',
                 hover_data=['additional_info'],
                 title='Interactive Scatter Plot')
fig.show()
```

#### Time Series Plot
```python
# If you have time series data
fig = px.line(merged_df, 
              x='date_column', 
              y='value_column',
              color='category_column',
              title='Time Series Analysis')
fig.show()
```

#### Dashboard-style Subplots
```python
from plotly.subplots import make_subplots

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Plot 1', 'Plot 2', 'Plot 3', 'Plot 4'),
    specs=[[{"secondary_y": False}, {"secondary_y": False}],
           [{"secondary_y": False}, {"secondary_y": False}]]
)

# Add traces
fig.add_trace(go.Bar(x=category_counts.index, y=category_counts.values, name="Categories"), row=1, col=1)
fig.add_trace(go.Scatter(x=merged_df['x_column'], y=merged_df['y_column'], mode='markers', name="Scatter"), row=1, col=2)
fig.add_trace(go.Histogram(x=merged_df['numeric_column'], name="Distribution"), row=2, col=1)
fig.add_trace(go.Box(y=merged_df['numeric_column'], name="Box Plot"), row=2, col=2)

fig.update_layout(height=600, showlegend=False, title_text="Multi-Source Data Dashboard")
fig.show()
```

## Advanced Analysis

### Statistical Analysis
```python
# Perform statistical tests, regression analysis, etc.
from scipy import stats

# Example: t-test between groups
group1 = merged_df[merged_df['category'] == 'A']['value']
group2 = merged_df[merged_df['category'] == 'B']['value']
t_stat, p_value = stats.ttest_ind(group1, group2)
print(f"T-statistic: {t_stat:.4f}, P-value: {p_value:.4f}")
```

## Export Results

### Save Visualizations
```python
# Save matplotlib figures
plt.savefig('output/visualization.png', dpi=300, bbox_inches='tight')

# Save plotly figures
fig.write_html('output/interactive_plot.html')
fig.write_image('output/plotly_plot.png')
```

### Export Processed Data
```python
# Save cleaned/processed data
merged_df.to_csv('output/processed_data.csv', index=False)
merged_df.to_excel('output/processed_data.xlsx', index=False)

# Save to database
merged_df.to_sql('processed_table', conn, if_exists='replace', index=False)
```

## Summary & Conclusions

### Key Findings
- Bullet point 1
- Bullet point 2
- Bullet point 3

### Next Steps
- Future analysis directions
- Additional data sources to explore
- Model development recommendations

## Appendix

### Data Dictionary
| Column Name | Description | Data Type | Source |
|-------------|-------------|-----------|---------|
| column1     | Description | int64     | CSV     |
| column2     | Description | object    | API     |

### Code Utilities
```python
def custom_plotting_function(data, column):
    """Custom function for repeated plotting tasks"""
    pass

def data_quality_check(df):
    """Function to perform data quality checks"""
    pass
```