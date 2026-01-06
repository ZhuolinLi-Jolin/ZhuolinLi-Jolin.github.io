import requests
from bs4 import BeautifulSoup
import pandas as pd

# 1. Target webpage URL
url = "https://statswales.gov.wales/Catalogue/Business-Economy-and-Labour-Market/Regional-Accounts/Gross-Value-Added-GDP/gva-by-component-welshnuts2areas-year" 

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_and_clean():
    try:
        print("Requesting webpage...")
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Request failed, status code: {response.status_code}")
            return
        
        print("Webpage retrieved successfully, parsing raw data...")
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", id="pivotGrid_MT")
        
        if not table:
            print("Table not found, please check webpage structure.")
            return

        data_list = []
        rows = table.find_all("tr")

        for row in rows:
            header_cells = row.find_all("td", class_="dxpgRowFieldValue")
            data_cells = row.find_all("td", class_=lambda x: x and ("dxpgCell" in x or "dxpgTotalCell" in x))

            if data_cells and len(data_cells) >= 2:
                # Get area name
                area_name = header_cells[-1].get_text(strip=True) if header_cells else "Unknown"
                
                # Get 2022 data (second to last column)
                target_cell = data_cells[-2] 
                raw_value = target_cell.get_text(strip=True)
                clean_value = raw_value.replace('(p)', '').replace(',', '').strip()
                
                data_list.append({
                    "Area": area_name,
                    "2022_Value": clean_value
                })

        # --- Data Cleaning Phase ---
        if data_list:
            df = pd.DataFrame(data_list)
            print(f"Raw scraping complete, total {len(df)} rows. Starting cleanup...")

            # 1. Keep only first dataset: find index of second "Wales" and truncate
            wales_indices = df[df['Area'] == 'Wales'].index.tolist()
            if len(wales_indices) > 1:
                df = df.iloc[:wales_indices[1]]
                print(f"Removed duplicate data from second dataset onwards.")

            # 2. Remove summary rows (Wales total and regional statistics)
            summary_terms = ["Wales", "North Wales", "Mid and South West Wales", "South East Wales"]
            cleaned_df = df[~df['Area'].isin(summary_terms)].copy()
            
            # 3. Convert data type to numeric (ensure values are numbers)
            cleaned_df['2022_Value'] = pd.to_numeric(cleaned_df['2022_Value'], errors='coerce')

            # --- Save Results ---
            print("-" * 30)
            print("Cleaned raw data preview (2022):")
            print(cleaned_df)
            
            filename = "cleaned_wales_gva_2022.csv"
            cleaned_df.to_csv(filename, index=False)
            print(f"\nSuccess! Cleaned data has been saved to: {filename}")
            
        else:
            print("No data extracted.")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    scrape_and_clean()