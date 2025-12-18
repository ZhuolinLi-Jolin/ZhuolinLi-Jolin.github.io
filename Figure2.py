import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt

# ==========================================
# 1. 数据加载 (Data Loading)
# ==========================================
# 加载数据源
file_aiie = "project/Combined_AIIE.csv"  # 包含 Image Generation AIIE 和 Language Modeling AIIE 两列
file_f7 = "project/TBL_F7.csv"

# 加载数据
# Combined_AIIE.csv 包含两个 AIIE 列 (Image Generation AIIE 和 Language Modeling AIIE)
df_aiie = pd.read_csv(file_aiie)
# F7 文件前 5 行是元数据，所以需要跳过 (skiprows=5)
df_f7 = pd.read_csv(file_f7, skiprows=5)

# ==========================================
# 2. 行业映射函数 (NAICS Mapping Logic)
# ==========================================
# 将细分的 NAICS 代码映射到 F7 表格中的 10 大宽泛行业板块
def map_naics_to_sector(naics_code):
    try:
        # 提取前两位数字作为大类标识
        code = str(naics_code)[:2]
        code_int = int(code)
    except:
        return None
    
    # 映射规则
    if code_int in [11, 21]: return "Natural Resources and Mining"
    if code_int == 23: return "Construction"
    if 31 <= code_int <= 33: return "Manufacturing"
    if code_int in [22, 42, 44, 45, 48, 49]: return "Trade, Transportation, and Utilities"
    if code_int == 51: return "Information"
    if code_int in [52, 53]: return "Financial Activities"
    if code_int in [54, 55, 56]: return "Professional and Business Services"
    if code_int in [61, 62]: return "Education and Health Services"
    if code_int in [71, 72]: return "Leisure and Hospitality"
    if code_int == 81: return "Other Services"
    return None

# ==========================================
# 3. 数据处理与聚合 (Data Processing)
# ==========================================

# --- 处理图像生成 (IG) 数据 ---
df_aiie['Broad_Sector'] = df_aiie['NAICS'].apply(map_naics_to_sector)
# 按大板块计算平均暴露度
df_ig_agg = df_aiie.dropna(subset=['Image Generation AIIE']).groupby('Broad_Sector')['Image Generation AIIE'].mean().reset_index()
df_ig_agg.rename(columns={'Image Generation AIIE': 'IG_Exposure'}, inplace=True)

# --- 处理语言模型 (LM) 数据 ---
# 按大板块计算平均暴露度
df_lm_agg = df_aiie.dropna(subset=['Language Modeling AIIE']).groupby('Broad_Sector')['Language Modeling AIIE'].mean().reset_index()
df_lm_agg.rename(columns={'Language Modeling AIIE': 'LM_Exposure'}, inplace=True)

# --- 处理结构变动 (Structural Change - F7) 数据 ---
# F7 表格包含随时间变化的异质性指数。
# 我们取最近 12 个月（最后 12 行）的平均值，代表该行业当前的“变动程度”。
industry_columns = df_f7.columns[1:] # 跳过第一列时间列
latest_change = df_f7.iloc[-12:][industry_columns].mean()
df_change = pd.DataFrame({'Broad_Sector': latest_change.index, 'Dissimilarity_Index': latest_change.values})

# ==========================================
# 4. 数据合并 (Data Merging)
# ==========================================
# 将三个处理好的数据框按 'Broad_Sector' 合并
df_merged = pd.merge(df_change, df_ig_agg, on='Broad_Sector', how='inner')
df_merged = pd.merge(df_merged, df_lm_agg, on='Broad_Sector', how='inner')

# 计算综合暴露度 (Combined Exposure)
# 这里使用简单的算术平均。您也可以根据需要调整权重，例如 0.7*LM + 0.3*IG
df_merged['Combined_Exposure'] = (df_merged['IG_Exposure'] + df_merged['LM_Exposure']) / 2

print("合并后的最终数据预览：")
print(df_merged[['Broad_Sector', 'Combined_Exposure', 'Dissimilarity_Index']])

# ==========================================
# 5. 可视化绘图 (Plotting)
# ==========================================
plt.figure(figsize=(14, 6))
sns.set_style("whitegrid")

# --- 子图 1: 仅看语言模型暴露度 ---
plt.subplot(1, 2, 1)
sns.scatterplot(
    data=df_merged,
    x='LM_Exposure',
    y='Dissimilarity_Index',
    s=200,
    color='darkorange',
    edgecolor='black',
    alpha=0.8
)
# 添加标签
for i in range(df_merged.shape[0]):
    row = df_merged.iloc[i]
    plt.text(row['LM_Exposure']+0.02, row['Dissimilarity_Index'], row['Broad_Sector'], fontsize=9)

plt.title('Language Modeling (Text) AI Exposure\nvs. Industry Structural Change', fontsize=12, fontweight='bold')
plt.xlabel('Avg Language Modeling Exposure (LM AIIE)', fontsize=10)
plt.ylabel('Occupational Mix Change Index (Churn)', fontsize=10)

# --- 子图 2: 仅看图像生成 ---
plt.subplot(1, 2, 2)
sns.scatterplot(
    data=df_merged,
    x='IG_Exposure',
    y='Dissimilarity_Index',
    s=200,
    color='seagreen',
    edgecolor='black',
    alpha=0.8
)
# 添加标签
for i in range(df_merged.shape[0]):
    row = df_merged.iloc[i]
    plt.text(row['IG_Exposure']+0.02, row['Dissimilarity_Index'], row['Broad_Sector'], fontsize=9)
plt.title('Image Generation AI Exposure\nvs. Industry Structural Change', fontsize=12, fontweight='bold')
plt.xlabel('Avg Image Generation Exposure (IG AIIE)', fontsize=10)
plt.ylabel('Occupational Mix Change Index (Churn)', fontsize=10)
plt.tight_layout()
plt.show() # 如果在脚本中运行，可以使用 plt.savefig('separate_analysis.png

# --- 子图 3: 综合暴露度 (文本+图像) ---
plt.subplot(1, 2, 2)
sns.scatterplot(
    data=df_merged,
    x='Combined_Exposure',
    y='Dissimilarity_Index',
    s=250, # 气泡稍微大一点
    color='purple',
    edgecolor='black',
    alpha=0.8
)
# 添加标签
for i in range(df_merged.shape[0]):
    row = df_merged.iloc[i]
    plt.text(row['Combined_Exposure']+0.02, row['Dissimilarity_Index'], row['Broad_Sector'], fontsize=9)

# 添加辅助线 (均值线)
plt.axvline(x=df_merged['Combined_Exposure'].mean(), color='gray', linestyle='--', alpha=0.5)
plt.axhline(y=df_merged['Dissimilarity_Index'].mean(), color='gray', linestyle='--', alpha=0.5)

plt.title('Combined AI Exposure (Text + Image)\nvs. Industry Structural Change', fontsize=12, fontweight='bold')
plt.xlabel('Combined AI Exposure Index (Avg of LM & IG)', fontsize=10)
plt.ylabel('Occupational Mix Change Index (Churn)', fontsize=10)

plt.tight_layout()
plt.show() # 如果在脚本中运行，可以使用 plt.savefig('combined_analysis.png') 保存

# ==========================================
# 6. 交互式 Vega-Lite/Altair 图表制作
# ==========================================
# 1. 定义下拉菜单
input_dropdown = alt.binding_select(
    options=['Text Generation', 'Image Generation', 'Combined'],
    name='Select AI Exposure Type: '
)

# 2. 创建参数
selection = alt.selection_point(
    fields=['Label'],
    bind=input_dropdown,
    value='Text Generation'
)

# 3. 基础图表定义 (注意：这里不要加 add_params)
# 我们在这里只做数据转换和过滤
base = alt.Chart(df_merged).transform_fold(
    ['LM_Exposure', 'IG_Exposure', 'Combined_Exposure'],
    as_=['Metric_Key', 'Exposure_Value']
).transform_calculate(
    Label="datum.Metric_Key == 'LM_Exposure' ? 'Text Generation' : (datum.Metric_Key == 'IG_Exposure' ? 'Image Generation' : 'Combined')"
).transform_filter(
    selection  # 过滤器必须保留在这里，因为所有图层都需要根据它来改变数据
)

# --- 定义颜色 ---
color_scale = alt.Scale(
    domain=['Text Generation', 'Image Generation', 'Combined'],
    range=['darkorange', 'seagreen', 'purple']
)

# --- 图层 A: 散点 ---
points = base.mark_circle(
    size=250,
    stroke='black',
    strokeWidth=1,
    opacity=0.8
).encode(
    x=alt.X('Exposure_Value:Q', 
            title='AI Exposure Index',
            scale=alt.Scale(zero=False, padding=1)),
    y=alt.Y('Dissimilarity_Index:Q', 
            title='Occupational Mix Change Index (Churn)',
            scale=alt.Scale(zero=False, padding=1)),
    color=alt.Color('Label:N', scale=color_scale, legend=None),
    tooltip=[
        alt.Tooltip('Broad_Sector:N', title='Sector'),
        alt.Tooltip('Exposure_Value:Q', title='Exposure', format='.2f'),
        alt.Tooltip('Dissimilarity_Index:Q', title='Churn Index', format='.2f')
    ]
)

# --- 图层 B: 标签 ---
text = base.mark_text(
    align='left', dx=12, fontSize=10
).encode(
    x='Exposure_Value:Q',
    y='Dissimilarity_Index:Q',
    text='Broad_Sector:N'
)

# --- 图层 C: 均值线 ---
rule_x = base.mark_rule(
    color='gray', strokeDash=[4, 4], opacity=0.5
).encode(
    x='mean(Exposure_Value):Q'
)

rule_y = base.mark_rule(
    color='gray', strokeDash=[4, 4], opacity=0.5
).encode(
    y='mean(Dissimilarity_Index):Q'
)

# --- 组合 ---
# ！！！关键修改！！！
# add_params(selection) 必须加在这里，确保只添加一次
final_chart = (rule_x + rule_y + points + text).add_params(
    selection
).properties(
    width=600,
    height=450,
    title='AI Exposure vs. Industry Structural Change (Interactive)'
)

# final_chart.save('interactive_chart.html')
# print("成功！已生成 interactive_chart.html")
print(final_chart.to_json())