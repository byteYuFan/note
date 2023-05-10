# -*- coding: utf-8 -*-
"""
Created on Tue May  2 08:53:24 2023

@author: wangyufan
"""

import pandas as pd

# 读取 excel 文件
df = pd.read_excel('result.xlsx', sheet_name='Sheet1')

# 按照 target 分组
grouped = df.groupby('target')

# 遍历每个分组，将分组数据保存为单独的 Excel 文件
for target, group in grouped:
    # 构造文件名
    filename = f'target_{target}.xlsx'
    # 保存数据
    group.to_excel(filename, index=False)