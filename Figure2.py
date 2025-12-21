import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt

# ==========================================
# 1. Data Loading
# ==========================================
# Load data sources
file_aiie = "project/Combined_AIIE.csv"  # Contains both Image Generation AIIE and Language Modeling AIIE columns
file_f7 = "project/TBL_F7.csv"

# Load data
# Combined_AIIE.csv contains two AIIE columns (Image Generation AIIE and Language Modeling AIIE)
df_aiie = pd.read_csv(file_aiie)
# F7 file has 5 rows of metadata at the beginning, so skip them (skiprows=5)
df_f7 = pd.read_csv(file_f7, skiprows=5)

# ==========================================
# 2. NAICS Mapping Logic
# ==========================================
# Map detailed NAICS codes to 10 broad industry sectors from F7 table
def map_naics_to_sector(naics_code):
    try:
        # Extract first two digits as major category identifier
        code = str(naics_code)[:2]
        code_int = int(code)
    except:
        return None
    
    # Mapping rules
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
# 3. Data Processing & Aggregation
# ==========================================

# --- Process Image Generation (IG) data ---
df_aiie['Broad_Sector'] = df_aiie['NAICS'].apply(map_naics_to_sector)
# Calculate average exposure by broad sector
df_ig_agg = df_aiie.dropna(subset=['Image Generation AIIE']).groupby('Broad_Sector')['Image Generation AIIE'].mean().reset_index()
df_ig_agg.rename(columns={'Image Generation AIIE': 'IG_Exposure'}, inplace=True)

# --- Process Language Modeling (LM) data ---
# Calculate average exposure by broad sector
df_lm_agg = df_aiie.dropna(subset=['Language Modeling AIIE']).groupby('Broad_Sector')['Language Modeling AIIE'].mean().reset_index()
df_lm_agg.rename(columns={'Language Modeling AIIE': 'LM_Exposure'}, inplace=True)

# --- Process Structural Change (F7) data ---
# F7 table contains heterogeneity index over time.
# We take the average of the most recent 12 months (last 12 rows) to represent current "degree of change" for each industry.
industry_columns = df_f7.columns[1:] # Skip first time column
latest_change = df_f7.iloc[-12:][industry_columns].mean()
df_change = pd.DataFrame({'Broad_Sector': latest_change.index, 'Dissimilarity_Index': latest_change.values})

# ==========================================
# 4. Data Merging
# ==========================================
# Merge three processed dataframes by 'Broad_Sector'
df_merged = pd.merge(df_change, df_ig_agg, on='Broad_Sector', how='inner')
df_merged = pd.merge(df_merged, df_lm_agg, on='Broad_Sector', how='inner')

# Calculate combined exposure (Combined Exposure)
# Here we use simple arithmetic mean. You can adjust weights if needed, e.g., 0.7*LM + 0.3*IG
df_merged['Combined_Exposure'] = (df_merged['IG_Exposure'] + df_merged['LM_Exposure']) / 2

print("Preview of merged final data:")
print(df_merged[['Broad_Sector', 'Combined_Exposure', 'Dissimilarity_Index']])

# ==========================================
# 5. Visualization (Plotting)
# ==========================================
plt.figure(figsize=(14, 6))
sns.set_style("whitegrid")

# --- Subplot 1: Language modeling exposure only ---
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
# Add labels
for i in range(df_merged.shape[0]):
    row = df_merged.iloc[i]
    plt.text(row['LM_Exposure']+0.02, row['Dissimilarity_Index'], row['Broad_Sector'], fontsize=9)

plt.title('Language Modeling (Text) AI Exposure\nvs. Industry Structural Change', fontsize=12, fontweight='bold')
plt.xlabel('Avg Language Modeling Exposure (LM AIIE)', fontsize=10)
plt.ylabel('Occupational Mix Change Index (Churn)', fontsize=10)

# --- Subplot 2: Image generation only ---
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
# Add labels
for i in range(df_merged.shape[0]):
    row = df_merged.iloc[i]
    plt.text(row['IG_Exposure']+0.02, row['Dissimilarity_Index'], row['Broad_Sector'], fontsize=9)
plt.title('Image Generation AI Exposure\nvs. Industry Structural Change', fontsize=12, fontweight='bold')
plt.xlabel('Avg Image Generation Exposure (IG AIIE)', fontsize=10)
plt.ylabel('Occupational Mix Change Index (Churn)', fontsize=10)
plt.tight_layout()
plt.show() # If running in script, can use plt.savefig('separate_analysis.png')

# --- Subplot 3: Combined exposure (text+image) ---
plt.subplot(1, 2, 2)
sns.scatterplot(
    data=df_merged,
    x='Combined_Exposure',
    y='Dissimilarity_Index',
    s=250, # Slightly larger bubbles
    color='purple',
    edgecolor='black',
    alpha=0.8
)
# Add labels
for i in range(df_merged.shape[0]):
    row = df_merged.iloc[i]
    plt.text(row['Combined_Exposure']+0.02, row['Dissimilarity_Index'], row['Broad_Sector'], fontsize=9)

# Add auxiliary lines (mean lines)
plt.axvline(x=df_merged['Combined_Exposure'].mean(), color='gray', linestyle='--', alpha=0.5)
plt.axhline(y=df_merged['Dissimilarity_Index'].mean(), color='gray', linestyle='--', alpha=0.5)

plt.title('Combined AI Exposure (Text + Image)\nvs. Industry Structural Change', fontsize=12, fontweight='bold')
plt.xlabel('Combined AI Exposure Index (Avg of LM & IG)', fontsize=10)
plt.ylabel('Occupational Mix Change Index (Churn)', fontsize=10)

plt.tight_layout()
plt.show() # If running in script, can use plt.savefig('combined_analysis.png') to save

# ==========================================
# 6. Interactive Vega-Lite/Altair Chart Creation
# ==========================================
# 1. Define dropdown menu
input_dropdown = alt.binding_select(
    options=['Text Generation', 'Image Generation', 'Combined'],
    name='Select AI Exposure Type: '
)

# 2. Create parameter
selection = alt.selection_point(
    fields=['Label'],
    bind=input_dropdown,
    value='Text Generation'
)

# 3. Base chart definition (note: don't add add_params here)
# We only do data transformation and filtering here
base = alt.Chart(df_merged).transform_fold(
    ['LM_Exposure', 'IG_Exposure', 'Combined_Exposure'],
    as_=['Metric_Key', 'Exposure_Value']
).transform_calculate(
    Label="datum.Metric_Key == 'LM_Exposure' ? 'Text Generation' : (datum.Metric_Key == 'IG_Exposure' ? 'Image Generation' : 'Combined')"
).transform_filter(
    selection  # Filter must stay here as all layers need to change data based on it
)

# --- Define colors ---
color_scale = alt.Scale(
    domain=['Text Generation', 'Image Generation', 'Combined'],
    range=['darkorange', 'seagreen', 'purple']
)

# --- Layer A: Scatter points ---
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

# --- Layer B: Labels ---
text = base.mark_text(
    align='left', dx=12, fontSize=10
).encode(
    x='Exposure_Value:Q',
    y='Dissimilarity_Index:Q',
    text='Broad_Sector:N'
)

# --- Layer C: Mean lines ---
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


final_chart = (rule_x + rule_y + points + text).add_params(
    selection
).properties(
    width=600,
    height=450,
    title='AI Exposure vs. Industry Structural Change (Interactive)'
)

# final_chart.save('interactive_chart.html')
# print("Success! Generated interactive_chart.html")
print(final_chart.to_json())