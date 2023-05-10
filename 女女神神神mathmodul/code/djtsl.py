# -*- coding: utf-8 -*-
"""
Created on Mon May  1 20:09:40 2023

@author: wangyufan
"""


import networkx as nx
import pandas as pd
import numpy as np
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
# 对节点进行整数转换
mapping = {node: int(node) for node in G.nodes()}
G = nx.relabel_nodes(G, mapping)
# 目标节点
path_lengths = nx.single_source_dijkstra_path_length(G, 10)
for node in path_lengths:
    print(f"Node {node}: {path_lengths[node]}")
shortest_path = nx.shortest_path(G, 4, 10, weight='weight')
print(shortest_path)
