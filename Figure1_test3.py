import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats

# ==========================================
# 1. Data Preparation
# ==========================================
try:
    df_aioe = pd.read_csv('project/dataset/AIOE_DataAppendix__Appendix_A.csv')
    df_bls = pd.read_csv('project/dataset/national_M2024_dl__national_M2024_dl.csv')
except FileNotFoundError:
    print("Warning: Data files not found. Using mock structure.")
    df_aioe = pd.DataFrame(columns=['SOC Code', 'AIOE'])
    df_bls = pd.DataFrame(columns=['OCC_CODE', 'TOT_EMP', 'A_MEAN', 'O_GROUP', 'OCC_TITLE'])

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
merged_df = merged_df.dropna(subset=['Sector'])

# ==========================================
# 2. Calculate Regression
# ==========================================
x_data = np.log10(merged_df['A_MEAN'])
y_data = merged_df['AIOE']

slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
x_range_log = np.linspace(x_data.min(), x_data.max(), 100)
x_range_real = 10**x_range_log 
y_pred = slope * x_range_log + intercept

# CI Calculation
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

# ==========================================
# 3. Plotting Setup
# ==========================================
color_map_fixed = {
    'Business & Admin': '#6A4C93',
    'STEM & Tech': '#395D9C',
    'Edu, Health & Arts': '#2A9D8F',
    'Services': '#55C667',
    'Manual & Trades': '#DCE319'
}

fig = go.Figure()

# Level 1: Gray Bands
fig.add_trace(go.Scatter(
    x=x_range_real, y=ci_upper,
    mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'
))
fig.add_trace(go.Scatter(
    x=x_range_real, y=ci_lower,
    mode='lines', line=dict(width=0), fill='tonexty', 
    fillcolor='rgba(200, 200, 200, 0.3)', showlegend=False, hoverinfo='skip'
))

# Level 2: Trend Line
fig.add_trace(go.Scatter(
    x=x_range_real, y=y_pred,
    mode='lines', name='Trend Line',
    line=dict(color='#555555', width=2, dash='dash'), showlegend=False, hoverinfo='skip'
))

# Level 3: Bubble Chart
scatter_fig = px.scatter(
    merged_df,
    x='A_MEAN', y='AIOE', size='TOT_EMP', color='Sector',
    hover_name='OCC_TITLE', log_x=True, size_max=60,
    color_discrete_map=color_map_fixed,
    category_orders={"Sector": list(color_map_fixed.keys())},
    hover_data={'Sector': True, 'TOT_EMP': True}
)

max_emp = merged_df['TOT_EMP'].max()
target_max_diameter = 55

for trace in scatter_fig.data:
    trace.marker.opacity = 0.75 
    trace.marker.line.width = 0.5 
    trace.marker.line.color = 'white'
    trace.marker.sizemode = 'area'
    trace.marker.sizeref = 2.0 * float(max_emp) / (target_max_diameter**2)
    
    trace.hovertemplate = (
        '<b>%{hovertext}</b><br><br>' +
        'Job Sector: %{customdata[0]}<br>' +
        'Annual Salary: %{x:$,.0f}<br>' + 
        'AIOE Score: %{y:.3f}<br>' + 
        'Total Employment: %{customdata[1]:,.0f}' + 
        '<extra></extra>' 
    )
    trace.hoverlabel = dict(font_size=13, font_family="Arial", font_color="white")
    fig.add_trace(trace)

# Annotations
key_occupations = ['Chief Executives', 'Software Developers', 'Cashiers', 'Registered Nurses', 'Lawyers', 'Waiters and Waitresses', 'General and Operations Managers', 'Carpenters']
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
            x=float(row['A_MEAN'].values[0]), y=float(row['AIOE'].values[0]),
            xref="x", yref="y", text=f"<b>{occ}</b>",
            showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor="#666666",
            ax=ax_val, ay=ay_val,
            font=dict(size=10, color="#222222", family="Arial"), 
            bgcolor="rgba(255,255,255,0.7)", borderpad=2
        ))

fig.update_layout(
    title=dict(text='<b>AI Exposure vs. Wage</b>', x=0.5, xanchor='center'),
    plot_bgcolor='white', width=1100, height=750, showlegend=True,
    xaxis=dict(title='Wage (Log)', type='log', dtick=np.log10(2), range=[np.log10(25000), np.log10(350000)]),
    yaxis=dict(title='AIOE Score', range=[-2.5, 2.5]),
    annotations=annotations, font=dict(family="Arial", color="#333333")
)

# ==========================================
# 4. EXPORT FIX: Deep clean to ensure standard JSON
# ==========================================

# def recursive_clean(obj):
#     """
#     Forces all data types into JSON-compatible Python primitives.
#     Removes any trace of bdata by expanding arrays into lists.
#     """
#     if isinstance(obj, dict):
#         return {k: recursive_clean(v) for k, v in obj.items()}
#     elif isinstance(obj, list):
#         return [recursive_clean(x) for x in obj]
#     elif isinstance(obj, (np.ndarray, pd.Series, pd.Index)):
#         # Convert NumPy/Pandas containers to native lists
#         return recursive_clean(obj.tolist())
#     elif isinstance(obj, (np.integer, int)):
#         return int(obj)
#     elif isinstance(obj, (np.floating, float)):
#         # Handle JSON-incompatible floats
#         if np.isnan(obj) or np.isinf(obj):
#             return None
#         return float(obj)
#     elif pd.isna(obj):
#         return None
#     else:
#         return obj

# # Step 1: Convert Figure to a raw Python dictionary
# fig_raw_dict = fig.to_dict()

# # Step 2: Manually clean the dictionary (converts NumPy -> List, floats -> clean floats)
# fig_clean_dict = recursive_clean(fig_raw_dict)

# # Step 3: Write using the standard JSON library
# with open('clean_chart_data_3.json', 'w', encoding='utf-8') as f:
#     json.dump(fig_clean_dict, f, ensure_ascii=False, indent=2)

# print("✅ SUCCESS: JSON exported without binary compression.")

import json

# ==========================================
# 4. Deep cleaning function to completely eliminate bdata
# ==========================================

def kill_bdata(obj):
    """
    Deep recursive traversal of dictionaries or lists.
    Force convert all NumPy arrays and Pandas Series to native Python lists.
    Convert all NumPy numbers to native float/int.
    """
    if isinstance(obj, dict):
        # Special handling for Plotly: if bdata key is found, ignore it and try other sources
        # But usually running this function after fig.to_dict() will prevent it from being generated
        return {k: kill_bdata(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [kill_bdata(x) for x in obj]
    elif isinstance(obj, (np.ndarray, pd.Series, pd.Index)):
        # Key point: completely convert arrays to native lists
        return kill_bdata(obj.tolist())
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        # Handle invalid numbers, JSON doesn't support NaN or Infinity
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif pd.isna(obj):
        return None
    else:
        return obj

# --- Execute export steps ---

# 1. Convert to base dictionary first
raw_dict = fig.to_dict()

# 2. Run deep cleaning (this step converts all residual NumPy arrays to plain [1, 2, 3])
clean_dict = kill_bdata(raw_dict)

# 3. Save using native json library (don't use fig.write_json)
with open('clean_chart_data_4.json', 'w', encoding='utf-8') as f:
    json.dump(clean_dict, f, ensure_ascii=False, indent=2)

print("✅ Export complete!")