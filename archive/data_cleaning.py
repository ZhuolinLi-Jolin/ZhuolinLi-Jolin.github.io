import pandas as pd
import os

# Get the absolute path of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the Excel file
xlsx_path = os.path.join(current_dir, 'Image Generation AIOE and AIIE.xlsx')

print(f"Reading file: {xlsx_path} ...") # Print a prompt to track program progress

# Read the file
df = pd.read_excel(xlsx_path, sheet_name='IG AIIE')

# Save CSV with full path as well
csv_path = os.path.join(current_dir, 'IGAIIE.csv')
df.to_csv(csv_path, index=False, encoding='utf-8')

print("Completed!")
print(f"Data shape: {df.shape}")
print(f"\nFirst few rows:")
print(df.head())

xlsx_path = os.path.join(current_dir, 'Language Modeling AIOE and AIIE.xlsx')

print(f"Reading file: {xlsx_path} ...") # Print a prompt to track program progress

# Read the file
df = pd.read_excel(xlsx_path, sheet_name='LM AIIE')

# Save CSV with full path as well
csv_path = os.path.join(current_dir, 'LMAIIE.csv')
df.to_csv(csv_path, index=False, encoding='utf-8')

print("Completed!")
print(f"Data shape: {df.shape}")
print(f"\nFirst few rows:")
print(df.head())

# Merge the two CSV files
df_ig = pd.read_csv(os.path.join(current_dir, 'IGAIIE.csv'))
df_lm = pd.read_csv(os.path.join(current_dir, 'LMAIIE.csv'))
df_combined = pd.concat([df_ig, df_lm], ignore_index=True)
combined_csv_path = os.path.join(current_dir, 'Combined_AIIE.csv')
df_combined.to_csv(combined_csv_path, index=False, encoding='utf-8')
print("Merged IGAIIE and LMAIIE into Combined_AIIE.csv")
