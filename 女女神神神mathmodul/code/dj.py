# -*- coding: utf-8 -*-
"""
Created on Mon May  1 14:02:23 2023

@author: wangyufan
"""

import networkx as nx
import pandas as pd
import multiprocessing

# 读取位置表单
locations = pd.read_excel("data1.xlsx", sheet_name="位置", header=0,index_col=0)

# 读取连接道路表单
roads = pd.read_excel("data.xlsx", sheet_name="连接道路")

# 创建空图
G = nx.Graph()

# 添加节点
for node in locations.index:
    G.add_node(node, pos=(locations.loc[node, "X"], locations.loc[node, "Y"]))

# 添加边
for i, row in roads.iterrows():
    G.add_edge(row["起点"], row["终点"], weight=row["距离"])
    
import matplotlib.pyplot as plt

# 获取节点位置
pos = nx.get_node_attributes(G, "pos")

# 绘制节点和边
nx.draw_networkx_nodes(G, pos, node_size=20)
nx.draw_networkx_edges(G, pos, width=1)

# 显示图
plt.axis("off")
plt.show()

shortest_paths_10 = nx.shortest_path(G, target=10)
shortest_paths_50 = nx.shortest_path(G, target=50)
shortest_paths_57 = nx.shortest_path(G, target=57)
# 计算每个节点到10、50、57节点的实际最短距离和路径
# 计算每个节点到10、50、57节点的实际最短距离和路径
result = {}
for node in G.nodes():
    shortest_distance_10 = nx.shortest_path_length(G, source=node, target=10, weight='weight')
    shortest_path_10 = shortest_paths_10[node]

    shortest_distance_50 = nx.shortest_path_length(G, source=node, target=50, weight='weight')
    shortest_path_50 = shortest_paths_50[node]

    shortest_distance_57 = nx.shortest_path_length(G, source=node, target=57, weight='weight')
    shortest_path_57 = shortest_paths_57[node]
    print("======================================")
    print(shortest_distance_10, shortest_distance_50, shortest_distance_57)
    print(shortest_path_10)
    shortest_distance = min(shortest_distance_10, shortest_distance_50, shortest_distance_57)
    shortest_target = None
    shortest_path = []
    if shortest_distance == shortest_distance_10:
        shortest_target = 10
        shortest_path = shortest_path_10
    elif shortest_distance == shortest_distance_50:
        shortest_target = 50
        shortest_path = shortest_path_50
    elif shortest_distance == shortest_distance_57:
        shortest_target = 57
        shortest_path = shortest_path_57

    # 计算路径上的权重之和

    print(shortest_distance,shortest_path)
    weight_sum = 0
    for i in range(len(shortest_path)-1):
       
        u, v = shortest_path[i], shortest_path[i+1]
    
    
        weight_sum += G[u][v]['weight']
    print(weight_sum)
    result[node] = {'target': shortest_target, 'distance': shortest_distance, 'path': shortest_path, 'weight': weight_sum}

# 将结果存储到Excel文件中
