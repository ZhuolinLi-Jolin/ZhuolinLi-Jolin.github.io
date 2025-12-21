import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from scipy import stats
import json

# ==========================================
# 1. Data Preparation
try:
    df_aioe = pd.read_csv('project/dataset/AIOE_DataAppendix__Appendix_A.csv')
    df_bls = pd.read_csv('project/dataset/national_M2024_dl__national_M2024_dl.csv')
except FileNotFoundError:
    print("Warning: Data files not found. Please ensure files are in the working directory.")
    # For demonstration purposes, create empty structure; actual run requires your files
    df_aioe = pd.DataFrame(columns=['SOC Code', 'AIOE'])
    df_bls = pd.DataFrame(columns=['OCC_CODE', 'TOT_EMP', 'A_MEAN', 'O_GROUP', 'OCC_TITLE'])

# Data cleaning logic remains unchanged
df_aioe['clean_soc'] = df_aioe['SOC Code'].astype(str).str.strip()
df_bls['clean_soc'] = df_bls['OCC_CODE'].astype(str).str.strip()
df_bls_detailed = df_bls[df_bls['O_GROUP'] == 'detailed'].copy()
df_bls_detailed['TOT_EMP'] = pd.to_numeric(df_bls_detailed['TOT_EMP'], errors='coerce')
df_bls_detailed['A_MEAN'] = pd.to_numeric(df_bls_detailed['A_MEAN'], errors='coerce')
df_clean = df_bls_detailed.dropna(subset=['TOT_EMP', 'A_MEAN', 'clean_soc'])
merged_df = pd.merge(df_clean, df_aioe, left_on='clean_soc', right_on='clean_soc', how='inner')

merged_df['major_code'] = merged_df['clean_soc'].str[:2]
sector_map = {
    '11': 'Business & Admin', '13': 'Business & Admin', '23': 'Business & Admin',
    '41': 'Business & Admin', '43': 'Business & Admin',
    '15': 'STEM & Tech', '17': 'STEM & Tech', '19': 'STEM & Tech',
    '21': 'Edu, Health & Arts', '25': 'Edu, Health & Arts', '27': 'Edu, Health & Arts', '29': 'Edu, Health & Arts',
    '31': 'Services', '33': 'Services', '35': 'Services', '37': 'Services', '39': 'Services',
    '45': 'Manual & Trades', '47': 'Manual & Trades', '49': 'Manual & Trades', '51': 'Manual & Trades', '53': 'Manual & Trades'
}
merged_df['Sector'] = merged_df['major_code'].map(sector_map)
# Filter out data without Sector to prevent plotting errors
merged_df = merged_df.dropna(subset=['Sector'])

# ==========================================
# 2. Calculate Regression Line & Confidence Interval
# ==========================================
x_data = np.log10(merged_df['A_MEAN'])
y_data = merged_df['AIOE']

slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)

# Generate range (log space)
x_range_log = np.linspace(x_data.min(), x_data.max(), 100)
x_range_real = 10**x_range_log 
y_pred = slope * x_range_log + intercept

# Simple confidence interval calculation
n = len(x_data)
dof = n - 2
t_score = stats.t.ppf(0.975, dof)
resid = y_data - (slope * x_data + intercept)
sum_errs = np.sum(resid**2)
stdev = np.sqrt(sum_errs / dof)
mean_x = np.mean(x_data)
sum_sq_diff_x = np.sum((x_data - mean_x)**2)
se_pred = stdev * np.sqrt(1/n + (x_range_log - mean_x)**2 / sum_sq_diff_x)

ci_upper = y_pred + t_score * se_pred
ci_lower = y_pred - t_score * se_pred

# 
# ==========================================
# 3. Plotting - Visual Refinement Version
# ==========================================

# [Key Fix 1] Precise color codes extracted from original plot
# Original plot doesn't use pure yellow, but greenish-yellow; purple is also brighter
color_map_fixed = {
    # 'Business & Admin': '#440154',  # Deep purple (keep it deep)
    'Business & Admin': '#6A4C93',
    'STEM & Tech': '#395D9C',       # Bluish (softer than before)
    'Edu, Health & Arts': '#2A9D8F',# Blue-green/Cyan (Teal)
    'Services': '#55C667',          # Emerald green (Green)
    'Manual & Trades': '#DCE319'    # [Key] Lime green/yellow-green (no longer harsh pure yellow)

    # 'Business & Admin': '#6A4C93',  
    # 'STEM & Tech': '#395D9C',       # Keep stable blue
    # 'Edu, Health & Arts': '#2A9D8F',# Keep cyan-teal color
    # 'Services': '#55C667',          # Keep emerald green
    # 'Manual & Trades': '#DCE319'    # Keep corrected lime green (not harsh)
}

fig = go.Figure()

# --- Layer 1: Gray confidence band (at the bottom) ---
fig.add_trace(go.Scatter(
    x=x_range_real, y=ci_upper,
    mode='lines', line=dict(width=0),
    showlegend=False, hoverinfo='skip'
))
fig.add_trace(go.Scatter(
    x=x_range_real, y=ci_lower,
    mode='lines', line=dict(width=0),
    fill='tonexty', 
    fillcolor='rgba(200, 200, 200, 0.3)', # Lower opacity, more like original plot's light gray
    showlegend=False, hoverinfo='skip'
))

# --- Layer 2: Dashed regression line ---
fig.add_trace(go.Scatter(
    x=x_range_real, y=y_pred,
    mode='lines', name='Trend Line',
    line=dict(color='#555555', width=2, dash='dash'), # Slightly lighter black
    showlegend=False, hoverinfo='skip'
))

# --- Layer 3: Bubble chart (core visual fix) ---
# Use px to generate data structure, but manually control parameters
scatter_fig = px.scatter(
    merged_df,
    x='A_MEAN', y='AIOE', size='TOT_EMP', color='Sector',
    hover_name='OCC_TITLE', 
    log_x=True, 
    size_max=60, # This only gives px an initial reference, we'll manually override later
    color_discrete_map=color_map_fixed,
    category_orders={"Sector": list(color_map_fixed.keys())},
    hover_data={
        'Sector': True,   # customdata[0]
        'TOT_EMP': True,  # customdata[1]
        'A_MEAN': False,  # Not needed in customdata, it's on x-axis, use %{x}
        'AIOE': False     # Not needed in customdata, it's on y-axis, use %{y}
    }
)

# Calculate max employment for scaling ratio
max_emp = merged_df['TOT_EMP'].max()

# [Key Modification] Set expected maximum bubble diameter (pixels)
# Previously 45, now changed to 55, bubbles will be noticeably larger
target_max_diameter = 55

# Transfer px traces to go.Figure and apply transparency
for trace in scatter_fig.data:
    trace.marker.opacity = 0.75  # [Key Fix 3] Increase transparency to mimic original plot texture
    trace.marker.line.width = 0.5 # Add very subtle white border to bubbles, increase separation
    trace.marker.line.color = 'white'
    # Force bubble size calculation mode to 'area' (area), visually more intuitive
    trace.marker.sizemode = 'area' 
    # Slightly enlarge overall scaling ratio (ref) to match original plot's fullness
    trace.marker.sizeref = 2.0 * max(merged_df['TOT_EMP']) / (45**2)
    trace.hovertemplate = (
        '<b>%{hovertext}</b><br><br>' +
        'Job Sector: %{customdata[0]}<br>' +
        'Annual Salary: %{x:$,.0f}<br>' +  # Format: $ symbol, thousands separator, 0 decimals
        'AIOE Score: %{y:.3f}<br>' +       # Format: 3 decimals
        'Total Employment: %{customdata[1]:,.0f}' + # Format: thousands separator
        '<extra></extra>' # Hide Plotly's default trace name box
    )
    
    
    trace.hoverlabel = dict(
        font_size=13,
        font_family="Arial",
        font_color="white" 
    )
    fig.add_trace(trace)

# ==========================================
# 4. Styling & Annotations
# ==========================================
key_occupations = [
    'Chief Executives', 'Software Developers', 'Cashiers', 
    'Registered Nurses', 'Lawyers', 'Waiters and Waitresses', 
    'General and Operations Managers', 'Carpenters'
]

annotations = []
for occ in key_occupations:
 
    row = merged_df[merged_df['OCC_TITLE'].str.contains(occ, case=False, na=False)].sort_values('TOT_EMP', ascending=False).head(1)
    
    if not row.empty:
        
        ay_val = -30
        ax_val = 0
        if "Waiters" in occ: ay_val = 40 
        if "Carpenters" in occ: ay_val = 25; ax_val = 20
        if "Nurses" in occ: ax_val = -40; ay_val = 10
        
        annotations.append(dict(
            x=row['A_MEAN'].values[0],
            y=row['AIOE'].values[0],
            xref="x", yref="y", 
            text=f"<b>{occ}</b>",
            showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor="#666666",
            ax=ax_val, ay=ay_val,
            font=dict(size=10, color="#222222", family="Arial"), 
            bgcolor="rgba(255,255,255,0.7)", 
            borderpad=2
        ))

fig.update_layout(
    title=dict(
        text='<b>AI Exposure vs. Wage: A Structural Shift</b><br><span style="font-size:14px; color:grey;">(Logarithmic Scale)</span>',
        x=0.5, xanchor='center',
        font=dict(size=20)
    ),
    plot_bgcolor='white',
    width=1100, height=750,
    showlegend=True,
    legend=dict(
        title_text="Job Sector",
        yanchor="top", y=0.95, xanchor="right", x=1.15, 
        font=dict(size=12),
        itemsizing='constant'
    ),
    xaxis=dict(
        title='<b>Annual Mean Wage (Log Scale)</b>', 
        gridcolor='#eeeeee', 
        tickprefix='$', 
        type='log', 
        dtick=np.log10(2), 
        tickvals=[30000, 50000, 75000, 100000, 150000, 250000],
        ticktext=['$30k', '$50k', '$75k', '$100k', '$150k', '$250k'],
        range=[np.log10(25000), np.log10(350000)]
    ),
    yaxis=dict(
        title='<b>AI Exposure Score (AIOE)</b>', 
        gridcolor='#eeeeee', 
        zeroline=False,
        range=[-2.5, 2.5] 
    ),
    annotations=annotations,
    font=dict(family="Arial", color="#333333")
)

fig.show()

# ==========================================
# 5. Export to JSON
# ==========================================

def recursive_clean(obj):
    """
    Recursively clean all NumPy and Pandas types to native Python types.
    Convert NaN/Infinity to None for JSON compatibility.
    """
    if isinstance(obj, dict):
        return {k: recursive_clean(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [recursive_clean(x) for x in obj]
    elif isinstance(obj, (np.ndarray, pd.Series, pd.Index)):
        # Convert arrays to native list
        return recursive_clean(obj.tolist())
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        # Handle NaN and Infinity
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif pd.isna(obj):
        return None
    else:
        return obj

# Step 1: Convert Figure to dictionary
fig_dict = fig.to_dict()

# Step 2: Deep clean to remove all NumPy types
fig_clean = recursive_clean(fig_dict)

# Step 3: Export to JSON
with open('Figure1_chart.json', 'w', encoding='utf-8') as f:
    json.dump(fig_clean, f, ensure_ascii=False, indent=2)

print("✅ JSON export successful!")
print("File saved: Figure1_chart.json")