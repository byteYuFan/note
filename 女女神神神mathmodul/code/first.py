# -*- coding: utf-8 -*-
"""
Created on Tue May  2 10:03:10 2023

@author: wangyufan
"""


import networkx as nx
import pandas as pd
import numpy as np

res1 = pd.read_excel("target_10.xlsx", sheet_name="Sheet1", header=0,index_col=0).index
locations1 = pd.read_excel("data1.xlsx", sheet_name="位置", header=0,index_col=0)
# 读取连接道路表单
roads1 = pd.read_excel("data.xlsx", sheet_name="连接道路")

# 创建空图
G = nx.Graph()

# 添加节点

for node in locations1.index:
    #if node in res:
        G.add_node(node, pos=(locations1.loc[node, "X"], locations1.loc[node, "Y"]))

# 添加边
nodes1=res1
for i, row in roads1.iterrows():

    if int(row["起点"]) in nodes1 and  int(row["终点"]) in nodes1:
        G.add_edge(row["起点"], row["终点"], weight=row["距离"])
# 对节点进行整数转换
mapping = {node: int(node) for node in G.nodes()}
G = nx.relabel_nodes(G, mapping)

import matplotlib.pyplot as plt

# 获取节点位置
pos = nx.get_node_attributes(G, "pos")
plt.figure(figsize=(15, 15))
# 绘制节点和边
nx.draw_networkx_nodes(G, pos, node_size=20)
nx.draw_networkx_edges(G, pos, width=5)

# 显示图
plt.axis("off")
plt.show()

T = nx.minimum_spanning_tree(G)
# 获取最小生成树的边
plt.figure(figsize=(15, 15))

tree_edges = list(T.edges())
node_colors = ['y' if node != 10 else 'g' for node in G.nodes()]
node_sizes = [1000 if node == 10 else 300 for node in G.nodes()]
# 绘制节点和边，并将最小生成树的边标记为红色
nx.draw_networkx_nodes(G, pos,node_color=node_colors, node_size=node_sizes)
nx.draw_networkx_labels(G, pos, {n: str(n) for n in G.nodes()})
nx.draw_networkx_edges(G, pos, edgelist=tree_edges, edge_color='g', width=5)

# 显示图
plt.axis("off")
plt.show()

s_10=0
for node in nodes1:
    distance = nx.shortest_path_length(T, source=node, target=10, weight='weight')
    s_10+=distance

print("最短距离",s_10)

length=0
for (a,b) in tree_edges:
    length+=G.get_edge_data(a,b)['weight']


print("最小生成树长度：",length)




