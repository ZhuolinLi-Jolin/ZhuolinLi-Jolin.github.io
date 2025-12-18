import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from scipy import stats
import json

# ==========================================
# 1. 数据准备 (Data Preparation)
# ==========================================
# 模拟数据加载 (为了确保代码可运行，我保留了你的读取逻辑，但增加了容错)
try:
    df_aioe = pd.read_csv('project/dataset/AIOE_DataAppendix__Appendix_A.csv')
    df_bls = pd.read_csv('project/dataset/national_M2024_dl__national_M2024_dl.csv')
except FileNotFoundError:
    print("Warning: Data files not found. Please ensure files are in the working directory.")
    # 为了演示，创建一个空结构，实际运行时需要你的文件
    df_aioe = pd.DataFrame(columns=['SOC Code', 'AIOE'])
    df_bls = pd.DataFrame(columns=['OCC_CODE', 'TOT_EMP', 'A_MEAN', 'O_GROUP', 'OCC_TITLE'])

# 数据清洗逻辑保持不变
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
# 过滤掉没有 Sector 的数据，防止绘图报错
merged_df = merged_df.dropna(subset=['Sector'])

# ==========================================
# 2. 计算回归线与置信区间 (Regression & CI)
# ==========================================
x_data = np.log10(merged_df['A_MEAN'])
y_data = merged_df['AIOE']

slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)

# 生成范围 (log space)
x_range_log = np.linspace(x_data.min(), x_data.max(), 100)
x_range_real = 10**x_range_log 
y_pred = slope * x_range_log + intercept

# 简单的置信区间计算 (Confidence Interval)
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
# 3. 绘图 (Plotting) - 视觉修正版
# ==========================================

# 【关键修正1】从原图提取的精确颜色代码
# 原图不是纯黄，而是偏绿的黄；紫色也不是深紫，是偏亮一点的紫
color_map_fixed = {
    # 'Business & Admin': '#440154',  # 深紫色 (保持深邃)
    'Business & Admin': '#6A4C93',
    'STEM & Tech': '#395D9C',       # 偏蓝 (比之前更柔和)
    'Edu, Health & Arts': '#2A9D8F',# 蓝绿色/青色 (Teal)
    'Services': '#55C667',          # 翠绿色 (Green)
    'Manual & Trades': '#DCE319'    # 【重点】嫩绿色/黄绿色 (不再是刺眼的纯黄)
    # -------------------------------------
    # 'Business & Admin': '#4C72B0',  # 柔和蓝
    # 'STEM & Tech': '#55A868',       # 柔和绿
    # 'Edu, Health & Arts': '#C44E52',# 柔和红
    # 'Services': '#CCB974',          # 芥末金 (完全解决了亮黄刺眼的问题)
    # 'Manual & Trades': '#8172B3'    # 柔和紫

    # 'Business & Admin': '#8172B3',  # 柔和紫
    # 'STEM & Tech': '#55C667',       
    # 'Edu, Health & Arts': '#2A9D8F',
    # 'Services': '#395D9C',          
    # 'Manual & Trades': '#CCB974'

    # 'Business & Admin': '#6A4C93',  
    # 'STEM & Tech': '#395D9C',       # 保持稳重的蓝
    # 'Edu, Health & Arts': '#2A9D8F',# 保持青碧色
    # 'Services': '#55C667',          # 保持翠绿
    # 'Manual & Trades': '#DCE319'    # 保持修正后的嫩绿 (不刺眼)
}

fig = go.Figure()

# --- 层级 1: 灰色误差带 (放在最底层) ---
fig.add_trace(go.Scatter(
    x=x_range_real, y=ci_upper,
    mode='lines', line=dict(width=0),
    showlegend=False, hoverinfo='skip'
))
fig.add_trace(go.Scatter(
    x=x_range_real, y=ci_lower,
    mode='lines', line=dict(width=0),
    fill='tonexty', 
    fillcolor='rgba(200, 200, 200, 0.3)', # 降低不透明度，更像原图的浅灰
    showlegend=False, hoverinfo='skip'
))

# --- 层级 2: 虚线回归线 ---
fig.add_trace(go.Scatter(
    x=x_range_real, y=y_pred,
    mode='lines', name='Trend Line',
    line=dict(color='#555555', width=2, dash='dash'), # 稍微淡一点的黑
    showlegend=False, hoverinfo='skip'
))

# --- 层级 3: 气泡图 (核心视觉修正) ---
# 使用 px 生成数据结构，但手动控制参数
scatter_fig = px.scatter(
    merged_df,
    x='A_MEAN', y='AIOE', size='TOT_EMP', color='Sector',
    hover_name='OCC_TITLE', 
    log_x=True, 
    size_max=60, # 这里只是给 px 一个初始参考，后面我们会手动覆盖
    color_discrete_map=color_map_fixed,
    category_orders={"Sector": list(color_map_fixed.keys())},
    hover_data={
        'Sector': True,   # customdata[0]
        'TOT_EMP': True,  # customdata[1]
        'A_MEAN': False,  # 不需要放入customdata，因为它是坐标轴 x，直接用 %{x}
        'AIOE': False     # 不需要放入customdata，因为它是坐标轴 y，直接用 %{y}
    }
)

# 计算最大就业人数，用于缩放比例
max_emp = merged_df['TOT_EMP'].max()

# 【关键修改】设定预期的最大气泡直径 (像素)
# 之前是 45，现在改为 55，气泡会明显变大
target_max_diameter = 55

# 将 px 的轨迹转移到 go.Figure，并应用透明度
for trace in scatter_fig.data:
    trace.marker.opacity = 0.75  # 【关键修正3】增加透明度，模仿原图质感
    trace.marker.line.width = 0.5 # 给气泡加极其细微的白边，增加分离度
    trace.marker.line.color = 'white'
    # 强制气泡大小计算模式为 'area' (面积)，视觉上更符合人类直觉
    trace.marker.sizemode = 'area' 
    # 稍微放大整体缩放比例 (ref) 以匹配原图的丰满感
    trace.marker.sizeref = 2.0 * max(merged_df['TOT_EMP']) / (45**2)
    trace.hovertemplate = (
        '<b>%{hovertext}</b><br><br>' +
        'Job Sector: %{customdata[0]}<br>' +
        'Annual Salary: %{x:$,.0f}<br>' +  # 格式化：$符号, 千分位逗号, 0位小数
        'AIOE Score: %{y:.3f}<br>' +       # 格式化：3位小数
        'Total Employment: %{customdata[1]:,.0f}' + # 格式化：千分位逗号
        '<extra></extra>' # 隐藏 Plotly 默认的 trace 名称框
    )
    
    # 强制设置 Hover 样式以匹配截图 (背景色自动跟随点的颜色，字体白色)
    trace.hoverlabel = dict(
        font_size=13,
        font_family="Arial",
        font_color="white" # 强制文字变白
    )
    fig.add_trace(trace)

# ==========================================
# 4. 样式与标注 (Styling & Annotations)
# ==========================================
key_occupations = [
    'Chief Executives', 'Software Developers', 'Cashiers', 
    'Registered Nurses', 'Lawyers', 'Waiters and Waitresses', 
    'General and Operations Managers', 'Carpenters'
]

annotations = []
for occ in key_occupations:
    # 查找职业
    row = merged_df[merged_df['OCC_TITLE'].str.contains(occ, case=False, na=False)].sort_values('TOT_EMP', ascending=False).head(1)
    
    if not row.empty:
        # 手动微调某些重叠标签的位置
        ay_val = -30
        ax_val = 0
        if "Waiters" in occ: ay_val = 40 
        if "Carpenters" in occ: ay_val = 25; ax_val = 20
        if "Nurses" in occ: ax_val = -40; ay_val = 10
        
        annotations.append(dict(
            x=row['A_MEAN'].values[0], # 直接用原始值，因为 x轴已经是 log 类型
            y=row['AIOE'].values[0],
            xref="x", yref="y", 
            text=f"<b>{occ}</b>", # 使用简短名字
            showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor="#666666",
            ax=ax_val, ay=ay_val,
            font=dict(size=10, color="#222222", family="Arial"), 
            bgcolor="rgba(255,255,255,0.7)", # 半透明白色背景
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
        yanchor="top", y=0.95, xanchor="right", x=1.15, # 移到图表外右侧
        font=dict(size=12),
        itemsizing='constant'
    ),
    xaxis=dict(
        title='<b>Annual Mean Wage (Log Scale)</b>', 
        gridcolor='#eeeeee', 
        tickprefix='$', 
        type='log', 
        dtick=np.log10(2), # 让网格线稍微密一点，接近原图
        tickvals=[30000, 50000, 75000, 100000, 150000, 250000],
        ticktext=['$30k', '$50k', '$75k', '$100k', '$150k', '$250k'],
        range=[np.log10(25000), np.log10(350000)]
    ),
    yaxis=dict(
        title='<b>AI Exposure Score (AIOE)</b>', 
        gridcolor='#eeeeee', 
        zeroline=False,
        range=[-2.5, 2.5] # 强制固定 Y 轴范围以匹配原图构图
    ),
    annotations=annotations,
    font=dict(family="Arial", color="#333333")
)

fig.show()

# ==========================================
# 5. Export to JSON (JSON导出)
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