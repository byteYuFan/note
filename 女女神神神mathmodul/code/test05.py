import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# 读取村庄坐标数据
village_df = pd.read_excel('data1.xlsx', sheet_name='位置', index_col=0)

# 构建无向图
G = nx.Graph()

# 添加村庄节点
for i, row in village_df.iterrows():
    G.add_node(i, pos=(row['X'], row['Y']))

# 添加道路边
roads_df = pd.read_excel('data.xlsx', sheet_name='连接道路')
for i, row in roads_df.iterrows():
    u, v = row['起点'], row['终点']
    # 计算道路长度
    length = ((village_df.loc[u] - village_df.loc[v]) ** 2).sum() ** 0.5
    G.add_edge(u, v, weight=length, repair=False)

# 初始化医疗点数量和列表
num_hospitals = 3
hospitals = []

# 循环添加医疗点
for i in range(num_hospitals):
    # 计算每个村庄到已有医疗点的最短距离
    distances = nx.shortest_path_length(G, weight='weight')
    if hospitals:
        for j in hospitals:
            distances = {k: min(d, distances[k]) for k, d in distances[j].items()}

    # 选择距离最远的村庄作为新的医疗点
    new_hospital = max(distances, key=distances.get)
    hospitals.append(new_hospital)

    # 把新的医疗点添加到图中
    G.add_node(new_hospital, is_hospital=True)

    # 添加从新医疗点到每个村庄的边
    for j in village_df.index:
        if j != new_hospital:
            # 计算道路长度
            length = ((village_df.loc[j] - village_df.loc[new_hospital]) ** 2).sum() ** 0.5
            # 把边加入图中，确保新边不会破坏连通性
            G.add_edge(j, new_hospital, weight=length, repair=True)
            if not nx.is_connected(G):
                G.remove_edge(j, new_hospital)
                G.add_edge(new_hospital, j, weight=length, repair=True)

# 计算各村庄到医疗点的最短路径
shortest_paths = []
for h in hospitals:
    sp = dict(nx.shortest_path_length(G, h, weight='weight'))
    shortest_paths.append(sp)

# 计算每个村庄到医疗点的距离和，并求和
total_distance = 0
for i, row in village_df.iterrows():
    shortest_dist = min([sp[i] for sp in shortest_paths])
    total_distance += shortest_dist

print(f"医疗点的位置为：{hospitals}")
print(f"各村庄到医疗点的距离总和为：{total_distance:.2f} 米")

# 绘制图形

