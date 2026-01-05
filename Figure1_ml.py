import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression  # [New] 引入 sklearn
from scipy import stats
import json

# ==========================================
# 1. Data Preparation
# ==========================================
try:
    df_aioe = pd.read_csv('project/dataset/AIOE_DataAppendix__Appendix_A.csv')
    df_bls = pd.read_csv('project/dataset/national_M2024_dl__national_M2024_dl.csv')
except FileNotFoundError:
    print("Warning: Data files not found. Please ensure files are in the working directory.")
    df_aioe = pd.DataFrame(columns=['SOC Code', 'AIOE'])
    df_bls = pd.DataFrame(columns=['OCC_CODE', 'TOT_EMP', 'A_MEAN', 'O_GROUP', 'OCC_TITLE'])

# Data cleaning logic
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
# 2. Calculate Regression Line & Confidence Interval (Using sklearn)
# ==========================================

# 准备数据 (sklearn 需要 2D 数组作为 X)
# Prepare data (sklearn requires 2D array for X)
X = np.log10(merged_df[['A_MEAN']].values)  # Shape: (n, 1)
y = merged_df['AIOE'].values                # Shape: (n,)

# [Change] 使用 sklearn 进行线性回归
# [Change] Use sklearn for Linear Regression
model = LinearRegression()
model.fit(X, y)

# 获取系数和截距
slope = model.coef_[0]
intercept = model.intercept_

# 生成预测用的 X 范围 (Log space)
x_range_log = np.linspace(X.min(), X.max(), 100)
X_pred_range = x_range_log.reshape(-1, 1) # Reshape for sklearn prediction

# 获取预测值 (回归线)
y_pred_line = model.predict(X_pred_range)
x_range_real = 10**x_range_log 

# --- 计算置信区间 (Confidence Interval) ---
# sklearn 不直接提供置信区间，需要手动计算统计量
# sklearn doesn't provide CI directly, need manual statistical calculation

# 1. 在训练集上进行预测以计算残差
y_train_pred = model.predict(X)
residuals = y - y_train_pred

# 2. 计算自由度和标准误差
n = len(X)
dof = n - 2  # Degrees of Freedom
sum_squared_residuals = np.sum(residuals**2)
std_error_estimate = np.sqrt(sum_squared_residuals / dof) # Standard deviation of residuals

# 3. 计算预测的标准误 (Standard Error of Prediction)
mean_x = np.mean(X)
sum_sq_diff_x = np.sum((X.flatten() - mean_x)**2)

# 计算每个预测点的标准误
se_pred = std_error_estimate * np.sqrt(1/n + (x_range_log - mean_x)**2 / sum_sq_diff_x)

# 4. 计算置信区间 (95%)
t_score = stats.t.ppf(0.975, dof)
ci_upper = y_pred_line + t_score * se_pred
ci_lower = y_pred_line - t_score * se_pred

# ==========================================
# 3. Plotting - Visual Refinement Version
# ==========================================

color_map_fixed = {
    'Business & Admin': '#6A4C93',
    'STEM & Tech': '#395D9C',       
    'Edu, Health & Arts': '#2A9D8F',
    'Services': '#55C667',          
    'Manual & Trades': '#DCE319'    
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
    fillcolor='rgba(200, 200, 200, 0.3)', 
    showlegend=False, hoverinfo='skip'
))

# --- Layer 2: Dashed regression line ---
fig.add_trace(go.Scatter(
    x=x_range_real, y=y_pred_line, # Updated variable name
    mode='lines', name='Trend Line',
    line=dict(color='#555555', width=2, dash='dash'), 
    showlegend=False, hoverinfo='skip'
))

# --- Layer 3: Bubble chart ---
scatter_fig = px.scatter(
    merged_df,
    x='A_MEAN', y='AIOE', size='TOT_EMP', color='Sector',
    hover_name='OCC_TITLE', 
    log_x=True, 
    size_max=60, 
    color_discrete_map=color_map_fixed,
    category_orders={"Sector": list(color_map_fixed.keys())},
    hover_data={
        'Sector': True,   
        'TOT_EMP': True,  
        'A_MEAN': False,  
        'AIOE': False     
    }
)

target_max_diameter = 55

for trace in scatter_fig.data:
    trace.marker.opacity = 0.75 
    trace.marker.line.width = 0.5 
    trace.marker.line.color = 'white'
    trace.marker.sizemode = 'area' 
    if len(merged_df['TOT_EMP']) > 0:
        trace.marker.sizeref = 2.0 * merged_df['TOT_EMP'].max() / (45**2)
    
    trace.hovertemplate = (
        '<b>%{hovertext}</b><br><br>' +
        'Job Sector: %{customdata[0]}<br>' +
        'Annual Salary: %{x:$,.0f}<br>' +  
        'AIOE Score: %{y:.3f}<br>' +       
        'Total Employment: %{customdata[1]:,.0f}' + 
        '<extra></extra>' 
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
    if isinstance(obj, dict):
        return {k: recursive_clean(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [recursive_clean(x) for x in obj]
    elif isinstance(obj, (np.ndarray, pd.Series, pd.Index)):
        return recursive_clean(obj.tolist())
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif pd.isna(obj):
        return None
    else:
        return obj

fig_dict = fig.to_dict()
fig_clean = recursive_clean(fig_dict)

with open('Figure1_chart.json', 'w', encoding='utf-8') as f:
    json.dump(fig_clean, f, ensure_ascii=False, indent=2)

print("✅ JSON export successful!")
print("File saved: Figure1_chart.json")