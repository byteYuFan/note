# -*- coding: utf-8 -*-



import random
import networkx as nx
import pandas as pd

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

T = nx.minimum_spanning_tree(G)

# 获取最小生成树的边
tree_edges = list(T.edges())

# 绘制节点和边，并将最小生成树的边标记为红色
nx.draw_networkx_nodes(G, pos, node_size=20)
nx.draw_networkx_edges(G, pos, width=1)
nx.draw_networkx_edges(G, pos, edgelist=tree_edges, edge_color='r', width=2)

# 显示图
plt.axis("off")
plt.show()


import itertools
def get_next_center(G, nodes, centers):
    """
    获取下一个医疗站
    """
    distances = {}
    for node in nodes:
        if node in centers:
            continue
        # 计算该节点到所有已选医疗站的距离，并取最小值
        min_dist = float('inf')
        for center in centers:
            if G.has_edge(node, center):
                dist = G[node][center]['weight']
                if dist < min_dist:
                    min_dist = dist
        dist = min_dist
        distances[node] = dist
    print(distances)
    # 根据距离排序，并返回最小距离的节点
    sorted_nodes = sorted(distances.items(), key=lambda x: x[1])
    return sorted_nodes[0][0]

def get_total_distance(G, centers):
    """
    获取所有村庄到医疗站的距离总和
    """
    total_distance = 0
    for center in centers:
        shortest_paths = nx.shortest_path_length(G, source=center, weight='weight')
        total_distance += sum(shortest_paths.values())
    return total_distance

def repair_roads(G, centers):
    """
    获取需要维修的道路
    """
    repaired_edges = set()
    for center in centers:
        shortest_paths = nx.shortest_path(G, source=center, weight='weight')
        for start_node, paths in shortest_paths.items():
            if start_node == center:
                continue
            # 找到该路径经过的所有边，并添加到需要维修的道路集合中
            for i in range(len(paths)-1):
                edge = (paths[i], paths[i+1])
                repaired_edges.add(edge)
    return repaired_edges

def run_greedy_algorithm(G, num_centers):
    nodes = list(G.nodes)
    centers = []
    # 随机选择一个节点作为第一个医疗站
    centers.append(random.choice(nodes))
    # 选择剩下的医疗站
    while len(centers) < num_centers:
        next_center = get_next_center(G, nodes, centers)
        centers.append(next_center)
    total_distance = get_total_distance(G, centers)
    repaired_edges = repair_roads(G, centers)
    return centers, total_distance, repaired_edges

# 使用贪心算法求解最小距离和的医疗站组合、需要维修的道路集合以及总距离和
centers, total_distance, repaired_edges = run_greedy_algorithm(G, num_centers=3)

print("最优医疗站组合：", centers)
print("总距离和：", total_distance)
#print("需要维修的道路集合：", repaired_edges)

print()
