import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


# Base path (script directory)
BASE = Path(__file__).resolve().parent


# Load data
df_aiie = pd.read_csv(BASE / 'Combined_AIIE.csv')
df_f7 = pd.read_csv(BASE / 'TBL_F7.csv', skiprows=5)


# --- Process F7 (Industry Change) ---
industry_columns = df_f7.columns[1:]
latest_change = df_f7.iloc[-12:][industry_columns].mean()
df_change = pd.DataFrame({'Industry': latest_change.index, 'Dissimilarity_Index': latest_change.values})


# --- Map NAICS -> Broad Sector ---
def map_naics_to_sector(naics_code):
    try:
        code = str(naics_code)[:2]
        code_int = int(code)
    except Exception:
        return None

    if code_int in [11, 21]:
        return 'Natural Resources and Mining'
    if code_int == 23:
        return 'Construction'
    if 31 <= code_int <= 33:
        return 'Manufacturing'
    if code_int in [22, 42, 44, 45, 48, 49]:
        return 'Trade, Transportation, and Utilities'
    if code_int == 51:
        return 'Information'
    if code_int in [52, 53]:
        return 'Financial Activities'
    if code_int in [54, 55, 56]:
        return 'Professional and Business Services'
    if code_int in [61, 62]:
        return 'Education and Health Services'
    if code_int in [71, 72]:
        return 'Leisure and Hospitality'
    if code_int == 81:
        return 'Other Services'
    return None


df_aiie['Broad_Sector'] = df_aiie['NAICS'].apply(map_naics_to_sector)


# Aggregate exposure by broad sector for a given column
def aggregate_exposure(col_name):
    return (
        df_aiie.dropna(subset=[col_name])
        .groupby('Broad_Sector')[col_name]
        .mean()
        .reset_index()
        .rename(columns={col_name: 'Exposure'})
    )


# Prepare aggregated exposures for both measures
df_exposure_img = aggregate_exposure('Image Generation AIIE')
df_exposure_lm = aggregate_exposure('Language Modeling AIIE')


# Merge with structural-change data
df_img = pd.merge(df_change, df_exposure_img, left_on='Industry', right_on='Broad_Sector', how='inner')
df_lm = pd.merge(df_change, df_exposure_lm, left_on='Industry', right_on='Broad_Sector', how='inner')


def plot_exposure_vs_change(df, outpath, title, xlabel):
    sns.set_style('whitegrid')
    plt.figure(figsize=(12, 8))

    ax = sns.scatterplot(
        data=df,
        x='Exposure',
        y='Dissimilarity_Index',
        s=200,
        color='dodgerblue',
        edgecolor='black',
        linewidth=1.2,
        alpha=0.85
    )

    for i in range(df.shape[0]):
        row = df.iloc[i]
        plt.text(row['Exposure'] + 0.02, row['Dissimilarity_Index'], row['Industry'], fontsize=10)

    plt.axhline(df['Dissimilarity_Index'].mean(), color='gray', linestyle='--', alpha=0.6)
    plt.axvline(df['Exposure'].mean(), color='gray', linestyle='--', alpha=0.6)

    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel('Occupational Mix Change Index (Structural Churn)', fontsize=12)
    plt.tight_layout()
    plt.savefig(outpath, dpi=300)
    plt.close()


# Plot and save two figures
out_img = BASE / 'industry_structure_vs_image_generation.png'
out_lm = BASE / 'industry_structure_vs_language_modeling.png'

plot_exposure_vs_change(
    df_img,
    out_img,
    'Image Generation Exposure vs Industry Structural Change',
    'Average Image Generation AI Exposure (IG AIIE)'
)

plot_exposure_vs_change(
    df_lm,
    out_lm,
    'Language Modeling Exposure vs Industry Structural Change',
    'Average Language Modeling AI Exposure (LMAIIE)'
)

print(f'Saved: {out_img}')
print(f'Saved: {out_lm}')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df_aiie = pd.read_csv("project/Combined_AIIE.csv")
df_f7 = pd.read_csv("project/TBL_F7.csv", skiprows=5)

# --- Process F7 (Industry Change) ---
# Goal: Get the total magnitude of change (Dissimilarity Index) for each industry sector.
# We'll take the mean of the last 12 months to smooth out noise and get the "current" state of change/churn.
# F7 structure: "Months from Jan 2003" and then columns for industries.
# We need to ensure we get the latest data.
print("--- F7 Tail ---")
print(df_f7.tail())

# Calculate the average of the last year of data (last 12 rows) for each industry column
# Columns 1 to end are industries (Column 0 is 'Months from...')
industry_columns = df_f7.columns[1:]
latest_change = df_f7.iloc[-12:][industry_columns].mean()
df_change = pd.DataFrame({'Industry': latest_change.index, 'Dissimilarity_Index': latest_change.values})


# --- Process IG AIIE (Industry Exposure) ---
# Goal: Aggregate NAICS-based exposure to the broad sectors in F7.
# We need a mapping function from NAICS code (first 2 digits) to F7 Sectors.

def map_naics_to_sector(naics_code):
    try:
        code = str(naics_code)[:2]
        code_int = int(code)
    except:
        return None
    
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

df_aiie['Broad_Sector'] = df_aiie['NAICS'].apply(map_naics_to_sector)

# Group by Broad Sector and take the MEAN of IG AIIE
# We should probably weight this by employment size, but we don't have that in IG AIIE. 
# Simple mean is an acceptable proxy for "Average exposure of sub-industries".
df_exposure_agg = df_aiie.groupby('Broad_Sector')['Image Generation AIIE'].mean().reset_index()

# --- Merge ---
df_final = pd.merge(df_change, df_exposure_agg, left_on='Industry', right_on='Broad_Sector', how='inner')

print("\n--- Merged Data ---")
print(df_final)

# --- Plotting ---
plt.figure(figsize=(12, 8))
sns.set_style("whitegrid")

# Scatter plot
ax = sns.scatterplot(
    data=df_final,
    x='Image Generation AIIE',
    y='Dissimilarity_Index',
    s=200,
    color='dodgerblue',
    edgecolor='black',
    linewidth=1.5,
    alpha=0.8
)

# Add labels
for i in range(df_final.shape[0]):
    row = df_final.iloc[i]
    plt.text(
        row['Image Generation AIIE'] + 0.02, 
        row['Dissimilarity_Index'], 
        row['Industry'], 
        fontsize=11, 
        fontweight='medium',
        va='center'
    )

# Add quadrant lines (Mean or Median lines)
plt.axhline(df_final['Dissimilarity_Index'].mean(), color='gray', linestyle='--', alpha=0.5)
plt.axvline(df_final['Image Generation AIIE'].mean(), color='gray', linestyle='--', alpha=0.5)

# Annotations for quadrants (Optional but helpful)
# Top Right
plt.text(df_final['Image Generation AIIE'].max(), df_final['Dissimilarity_Index'].max(), "High Exposure\nHigh Struct. Change", ha='right', va='top', fontsize=10, color='gray')
# Bottom Right
plt.text(df_final['Image Generation AIIE'].max(), df_final['Dissimilarity_Index'].min(), "High Exposure\nStable Structure", ha='right', va='bottom', fontsize=10, color='gray')


plt.title('Relationship Between Image Gen AI Exposure and Industry Structural Change\n(Sources: IG AIIE & F7)', fontsize=15, fontweight='bold')
plt.xlabel('Average Image Generation AI Exposure (IG AIIE)', fontsize=12)
plt.ylabel('Occupational Mix Change Index (Structural Churn)', fontsize=12)
plt.tight_layout()

plt.savefig('industry_structure_vs_ai.png', dpi=300)