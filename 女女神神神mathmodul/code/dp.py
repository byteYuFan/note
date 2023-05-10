# -*- coding: utf-8 -*-
"""
Created on Mon May  1 09:19:16 2023

@author: wangyufan
"""


import pandas as pd
import networkx as nx
import numpy as np

# 读取数据
position = pd.read_excel('data1.xlsx', header=0,sheet_name='位置',skiprows=1)
edges = pd.read_excel('data.xlsx', header=0,sheet_name='连接道路')
# 创建图
G = nx.Graph()
print(position)
# 添加节点
for i, row in position.iterrows():
    G.add_node(i, pos=(row['X'], row['Y']))

# 添加边
for i, row in edges.iterrows():
    G.add_edge(row['起点'], row['终点'], weight=row['距离'])

# 动态规划寻找三个医疗站
n = len(position)
print(G.nodes())
print(n)
k = 3
dp = np.zeros((n+1, k+1))
for i in range(1, n+1):
    dp[i][1] = np.inf
    for j in range(2, k+1):
        dp[i][j] = np.inf
        for p in range(j-1, i):
            tmp = dp[p][j-1]
            for q in range(p+1, i+1):
                tmp += nx.dijkstra_path_length(G, q-1, p-1)
            dp[i][j] = min(dp[i][j], tmp)

# 获取结果
res = dp[n][k]

# 打印结果
print(f"动态规划方法计算得到的最小距离和为：{res:.2f}")
