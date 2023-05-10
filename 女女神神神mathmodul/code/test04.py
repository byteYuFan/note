import numpy as np
import pandas as pd
import heapq

# 读取位置表单
locations = pd.read_excel("data1.xlsx", sheet_name="位置", header=0, index_col=0)

# 读取连接道路表单
roads = pd.read_excel("data1.xlsx", sheet_name="连接道路")

# 构建邻接表
adj_list = {}
for i, row in roads.iterrows():
    start_loc = row["起点"]
    end_loc = row["终点"]
    distance = row["距离"]
    if start_loc not in adj_list:
        adj_list[start_loc] = {}
    if end_loc not in adj_list:
        adj_list[end_loc] = {}
    adj_list[start_loc][end_loc] = distance
    adj_list[end_loc][start_loc] = distance

# Dijkstra算法求最短路径
def dijkstra(start, end):
    # 初始化距离列表和前驱节点列表
    dist = {}
    prev = {}
    for loc in locations.index:
        dist[loc] = np.inf
        prev[loc] = None
    dist[start] = 0
    
    # 初始化堆和visited集合
    heap = [(0, start)]
    visited = set()
    
    while heap:
        # 取出堆中距离最小的节点
        (d, u) = heapq.heappop(heap)
        # 如果已经访问过，跳过
        if u in visited:
            continue
        visited.add(u)
        # 更新与节点u相邻的节点的距离
        for v, w in adj_list[u].items():
            if v not in visited:
                new_dist = dist[u] + w
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    prev[v] = u
                    heapq.heappush(heap, (new_dist, v))
    
    # 回溯得到最短路径
    path = []
    u = end
    while prev[u] is not None:
        path.insert(0, u)
        u = prev[u]
    path.insert(0, start)
    
    return path, dist[end]

# 计算每个村庄到其对应医疗点的距离
med_locs = [(29.013454, 105.399356), (30.039822, 105.533722), (30.694444, 105.186944)]
min_dists = np.zeros((len(locations)))
for i, loc in enumerate(locations[["X", "Y"]].values):
    dists = []
    for med_loc in med_locs:
        path, dist = dijkstra(locations.index[i], med_loc)
        dists.append(dist)
    min_dists[i] = np.min(dists)
S1 = np.sum(min_dists)

# 打印结果
print("选中的医疗点：")
for med_loc in med_locs:
    print("({:.6f}, {:.6f})".format(med_loc[0], med_loc[1]))
print("距离总和S1：{:.6f}".format(S1))
