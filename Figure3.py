import pandas as pd
import json

# 1. 读取更新后的 CSV 文件
df = pd.read_csv('project/dataset/Updated_Unemployment_industry.csv')

# 2. 数据清洗：筛选失业人数 (LNU03)
# 排除总计类行业，只保留细分行业以确保堆叠图不重复计数
excluded_industries = ['Nonagriculture industries', 'Manufacturing']
df_vol = df[df['Series ID'].str.startswith('LNU03', na=False)].copy()
df_vol = df_vol[~df_vol['industry'].isin(excluded_industries)]

# 剔除行业缺失或 AI 分数缺失的无效行
df_vol = df_vol.dropna(subset=['industry', 'AI_Exposure_Score'])

# 3. 动态识别月份列
# 排除掉非时间的属性列
metadata_cols = ['Series ID', 'Annual 2022', 'Annual 2023', 'Annual 2024', 
                 'labor_force_status', 'type_of_data', 'age', 'class_of_worker', 
                 'industry', 'AI_Exposure_Score']
month_cols = [c for c in df_vol.columns if c not in metadata_cols]

# 4. 转换数据为长格式 (Melt)
df_long = df_vol.melt(
    id_vars=['industry', 'AI_Exposure_Score'],
    value_vars=month_cols,
    var_name='Month_Str',
    value_name='Unemployed_Count'
)

# 5. 时间处理与排序
df_long['Date'] = pd.to_datetime(df_long['Month_Str'], format='%b %Y')
# 只保留2022年12月及之后的数据
# df_long = df_long[df_long['Date'] >= pd.Timestamp('2022-12-01')]
# 按照时间升序，AI暴露分降序排列（确保堆叠顺序美观且逻辑一致）
df_long = df_long.sort_values(['Date', 'AI_Exposure_Score'], ascending=[True, False])
df_long['Date_ISO'] = df_long['Date'].dt.strftime('%Y-%m-%d')

# 6. 生成 Vega-Lite JSON 配置
vega_data = df_long[['industry', 'AI_Exposure_Score', 'Unemployed_Count', 'Date_ISO', 'Month_Str']].to_dict(orient='records')

stacked_area_spec = {
    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
    "title": {
        "text": "Composition of US Unemployment by AI Exposure",
        "subtitle": "Stacked by unemployment volume (thousands), sorted by AI Exposure Score",
        "anchor": "start"
    },
    "width": 800,
    "height": 450,
    "data": {"values": vega_data},
    "mark": {
        "type": "area",
        "line": {"strokeWidth": 1, "opacity": 0.5},
        "interpolate": "monotone"
    },
    "encoding": {
        "x": {
            "field": "Date_ISO",
            "type": "temporal",
            "title": "Timeline (2022-2025)",
            "axis": {"format": "%b %Y", "labelAngle": -45}
        },
        "y": {
            "aggregate": "sum",
            "field": "Unemployed_Count",
            "type": "quantitative",
            "title": "Total Unemployed (Thousands)",
            "stack": "zero"
        },
        "color": {
            "field": "AI_Exposure_Score",
            "type": "quantitative",
            "title": "AI Exposure Score",
            "scale": {"scheme": "viridis"},
            "legend": {"gradientLength": 200}
        },
        "order": {
            "field": "AI_Exposure_Score",
            "type": "quantitative",
            "sort": "descending"
        },
        "tooltip": [
            {"field": "industry", "type": "nominal", "title": "Industry"},
            {"field": "Month_Str", "type": "nominal", "title": "Month"},
            {"field": "AI_Exposure_Score", "type": "quantitative", "title": "AI Exposure", "format": ".2f"},
            {"field": "Unemployed_Count", "type": "quantitative", "title": "Unemployed (K)"}
        ]
    },
    "config": {
        "axis": {"grid": False},
        "view": {"stroke": "transparent"}
    }
}

# 导出 JSON
with open('F3_unemployment_stacked_area_final.json', 'w') as f:
    json.dump(stacked_area_spec, f, indent=2)