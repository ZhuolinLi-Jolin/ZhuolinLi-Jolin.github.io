from bs4 import BeautifulSoup
import pandas as pd

# 读取HTML文件
with open('Bureau of Labor Statistics Data.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# 解析HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 找到所有catalog表格（包含元数据的表）
catalog_tables = soup.find_all('table', class_='catalog')

# 提取数据
data_list = []

for catalog_table in catalog_tables:
    # 初始化一个字典来存储每个series的信息
    series_info = {}
    
    rows = catalog_table.find_all('tr')
    
    for row in rows:
        th = row.find('th', class_='catalog')
        td = row.find('td', class_='catalog')
        
        if th and td:
            label = th.get_text(strip=True)
            value = td.get_text(strip=True)
            
            # 根据标签名提取相应信息
            if 'Series Id' in label:
                series_info['series_id'] = value
            elif 'Series title' in label:
                series_info['series_title'] = value
            elif 'Labor force status' in label:
                series_info['labor_force_status'] = value
            elif 'Type of data' in label:
                series_info['type_of_data'] = value
            elif 'Age' in label:
                series_info['age'] = value
            elif 'Class of worker' in label:
                series_info['class_of_worker'] = value
            elif 'Labor force experience' in label:
                series_info['labor_force_experience'] = value
            elif 'Industry' in label:
                series_info['industry'] = value
    
    # 只有当有series_id时才添加到列表
    if 'series_id' in series_info and series_info['series_id']:
        data_list.append(series_info)

# 创建DataFrame
df = pd.DataFrame(data_list)

# 按列重新排序
columns = ['series_id', 'series_title', 'labor_force_status', 'type_of_data', 
           'age', 'class_of_worker', 'labor_force_experience', 'industry']
df = df.reindex(columns=columns, fill_value='')

# 保存为CSV
df.to_csv('series_name.csv', index=False, encoding='utf-8-sig')

print("数据已成功提取！")
print(f"共提取 {len(df)} 条数据")
print("\n前几行数据预览：")
print(df.head(10))
print("\n数据统计：")
print(df.info())
import pandas as pd

# 读取CSV文件
df = pd.read_csv('series_name.csv')

# 基于series_id去重，保留第一次出现的记录
df_deduplicated = df.drop_duplicates(subset=['series_id'], keep='first')

# 保存去重后的数据
df_deduplicated.to_csv('series_name.csv', index=False, encoding='utf-8-sig')

print(f"原始数据：{len(df)} 行")
print(f"去重后：{len(df_deduplicated)} 行")
print(f"删除了 {len(df) - len(df_deduplicated)} 条重复记录")