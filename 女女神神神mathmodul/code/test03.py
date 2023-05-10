import numpy as np
import pandas as pd
import networkx as nx

# 读取位置表单
locations = pd.read_excel("data1.xlsx", sheet_name="位置", header=0, index_col=0)

# 读取连接道路表单
roads = pd.read_excel("data.xlsx", sheet_name="连接道路")

# 构建距离矩阵
dist_mat = np.zeros((len(locations), len(locations)))
for i, row in roads.iterrows():
    start_loc = row["起点"]
    end_loc = row["终点"]
    distance = row["距离"]
    start_idx = locations.index.get_loc(start_loc)
    end_idx = locations.index.get_loc(end_loc)
    dist_mat[start_idx, end_idx] = distance
    dist_mat[end_idx, start_idx] = distance

# 创建连通图
G = nx.Graph()

# 添加节点
for node in locations.index:
    G.add_node(node, pos=(locations.loc[node, "X"], locations.loc[node, "Y"]))

# 添加边
for i, row in roads.iterrows():
    G.add_edge(row["起点"], row["终点"], weight=row["距离"])
mapping = {node: int(node) for node in G.nodes()}
G = nx.relabel_nodes(G, mapping)
# 找到所有节点到10、50、57节点的最短路径
shortest_paths_10 =  nx.single_source_dijkstra_path_length(G,10)
shortest_paths_50 =  nx.single_source_dijkstra_path_length(G,50)
shortest_paths_57 =  nx.single_source_dijkstra_path_length(G,57)
shortest_path = nx.shortest_path(G, 4, 10, weight='weight')
print(shortest_path)

# 计算每个节点到10、50、57节点的实际最短距离和路径
result = {}
road_map={}
for node in G.nodes():

    shortest_distance_10 =shortest_paths_10[node]
    shortest_path_10 =nx.shortest_path(G,node,10,weight='weight')
    
    shortest_distance_50 =shortest_paths_50[node]
    shortest_path_50 = nx.shortest_path(G,node,50,weight='weight')

    shortest_distance_57 = shortest_paths_57[node]
    shortest_path_57 = nx.shortest_path(G,node,57,weight='weight')

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
    weight_sum = 0
    for i in range(len(shortest_path)-1):
        u, v = shortest_path[i], shortest_path[i+1]
        weight_sum += G[u][v]['weight']
    edges = [(shortest_path[i],shortest_path[i+1]) for i in range(len(shortest_path)-1)]
    sorted_edges = [tuple(sorted(edge)) for edge in edges]

    print(node,sorted_edges)
    for i in range(len(sorted_edges)):
        if sorted_edges[i] not in road_map:
            road_map[sorted_edges[i]] = 1
        else:
            road_map[sorted_edges[i]] += 1
    result[node] = {'target': shortest_target, 'distance': shortest_distance, 'path': shortest_path, 'weight': weight_sum}

# 将结果存储到Excel文件中
df = pd.DataFrame.from_dict(result, orient='index')
df.index.name = 'node'
df.to_excel('result.xlsx')
with open('road_map.txt', 'w') as file:
    for road in road_map:
        file.write(f'{road}:{road_map[road]}\n')
total_distance = 0
for (a, b) in road_map:
    distance =G.get_edge_data(a, b)['weight'] # 获取边的权值
    total_distance += distance
print("total_distance=",total_distance)