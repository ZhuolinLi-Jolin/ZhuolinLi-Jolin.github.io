import requests
from bs4 import BeautifulSoup
import pandas as pd

# 1. 目标网页 URL
url = "https://statswales.gov.wales/Catalogue/Business-Economy-and-Labour-Market/Regional-Accounts/Gross-Value-Added-GDP/gva-by-component-welshnuts2areas-year" 

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_and_clean():
    try:
        print("正在请求网页...")
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            return
        
        print("网页获取成功，开始解析原始数据...")
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", id="pivotGrid_MT")
        
        if not table:
            print("未找到表格，请检查网页结构。")
            return

        data_list = []
        rows = table.find_all("tr")

        for row in rows:
            header_cells = row.find_all("td", class_="dxpgRowFieldValue")
            data_cells = row.find_all("td", class_=lambda x: x and ("dxpgCell" in x or "dxpgTotalCell" in x))

            if data_cells and len(data_cells) >= 2:
                # 获取区域名称
                area_name = header_cells[-1].get_text(strip=True) if header_cells else "Unknown"
                
                # 获取 2022 数据 (倒数第二列)
                target_cell = data_cells[-2] 
                raw_value = target_cell.get_text(strip=True)
                clean_value = raw_value.replace('(p)', '').replace(',', '').strip()
                
                data_list.append({
                    "Area": area_name,
                    "2022_Value": clean_value
                })

        # --- 数据清洗阶段 ---
        if data_list:
            df = pd.DataFrame(data_list)
            print(f"原始抓取完成，共 {len(df)} 行。开始清洗...")

            # 1. 只保留第一组数据：找到第二个 "Wales" 的索引并截断
            wales_indices = df[df['Area'] == 'Wales'].index.tolist()
            if len(wales_indices) > 1:
                df = df.iloc[:wales_indices[1]]
                print(f"已截断第二组及之后的冗余数据。")

            # 2. 剔除汇总行 (Wales 总计及各大区统计)
            summary_terms = ["Wales", "North Wales", "Mid and South West Wales", "South East Wales"]
            cleaned_df = df[~df['Area'].isin(summary_terms)].copy()
            
            # 3. 转换数值类型 (确保是数字)
            cleaned_df['2022_Value'] = pd.to_numeric(cleaned_df['2022_Value'], errors='coerce')

            # --- 保存结果 ---
            print("-" * 30)
            print("清洗后的底层数据预览 (2022年):")
            print(cleaned_df)
            
            filename = "cleaned_wales_gva_2022.csv"
            cleaned_df.to_csv(filename, index=False)
            print(f"\n恭喜！清洗后的数据已保存至: {filename}")
            
        else:
            print("未提取到任何数据。")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    scrape_and_clean()