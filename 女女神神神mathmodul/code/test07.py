# -*- coding: utf-8 -*-
"""
Created on Mon May  1 15:11:20 2023

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
print("Nodes:", G.nodes)
print("Edges:", G.edges(data=True))
# 将图转换为矩阵
matrix = nx.to_numpy_matrix(G)

# 打印矩阵
print(matrix)
import numpy as np

def floyd(graph):
    n = len(graph)
    dist = np.copy(graph)
    next = np.empty((n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            if i != j and dist[i][j] < float('inf'):
                next[i][j] = j
            else:
                next[i][j] = -1
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next[i][j] = next[i][k]
    paths = {}
    for i in range(n):
        path = []
        for j in range(n):
            if j != i:
                curr = j
                while curr != i:
                    path.append(curr)
                    curr = next[i][curr]
                path.append(i)
                paths[(i, j)] = list(reversed(path))
    return dist, paths

dist, paths = floyd(matrix)
print(dist)
print(paths)