import pandas as pd
import os

# 获取当前脚本所在的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 拼接出 Excel 文件的完整路径
xlsx_path = os.path.join(current_dir, 'Image Generation AIOE and AIIE.xlsx')

print(f"正在读取文件: {xlsx_path} ...") # 加个打印提示，知道程序走到哪了

# 读取
df = pd.read_excel(xlsx_path, sheet_name='IG AIIE')

# 保存 CSV 也建议用完整路径
csv_path = os.path.join(current_dir, 'IGAIIE.csv')
df.to_csv(csv_path, index=False, encoding='utf-8')

print("完成！")
print(f"数据形状: {df.shape}")
print(f"\n前几行数据:")
print(df.head())

xlsx_path = os.path.join(current_dir, 'Language Modeling AIOE and AIIE.xlsx')

print(f"正在读取文件: {xlsx_path} ...") # 加个打印提示，知道程序走到哪了

# 读取
df = pd.read_excel(xlsx_path, sheet_name='LM AIIE')

# 保存 CSV 也建议用完整路径
csv_path = os.path.join(current_dir, 'LMAIIE.csv')
df.to_csv(csv_path, index=False, encoding='utf-8')

print("完成！")
print(f"数据形状: {df.shape}")
print(f"\n前几行数据:")
print(df.head())
# 合并两个csv
df_ig = pd.read_csv(os.path.join(current_dir, 'IGAIIE.csv'))
df_lm = pd.read_csv(os.path.join(current_dir, 'LMAIIE.csv'))
df_combined = pd.concat([df_ig, df_lm], ignore_index=True)
combined_csv_path = os.path.join(current_dir, 'Combined_AIIE.csv')
df_combined.to_csv(combined_csv_path, index=False, encoding='utf-8')
print("已合并IGAIIE和LMAIIE为Combined_AIIE.csv")
