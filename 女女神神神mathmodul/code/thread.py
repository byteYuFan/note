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

T = nx.minimum_spanning_tree(G)
file = open('file.txt', 'aw') # 打开文件
# 获取最小生成树的边
tree_edges = list(T.edges())

# 绘制节点和边，并将最小生成树的边标记为红色
nx.draw_networkx_nodes(G, pos, node_size=20)
nx.draw_networkx_edges(G, pos, width=1)
nx.draw_networkx_edges(G, pos, edgelist=tree_edges, edge_color='r', width=2)

# 显示图
plt.axis("off")
plt.show()
# 获取最小生成树的边信息
mst_edges = T.edges()

import itertools

# 定义函数，计算每个村庄到其对应医疗点的距离，并计算距离总和S1
def calculate_distance_sum(G, medical_centers):
    distance_sum = 0
    for node in G.nodes:
        min_distance = float("inf")
        for center in medical_centers:
            distance = nx.shortest_path_length(G, source=node, target=center, weight="weight")
            if distance < min_distance:
                min_distance = distance
        distance_sum += min_distance
    return distance_sum


def calculate_distance_sum_partial(G, medical_centers, start, end):
    print("=======================================================",start,end)
    distance_sum = 0
    for node in G.nodes[start:end]:
    
        min_distance = float("inf")
        for center in medical_centers:
            distance = nx.shortest_path_length(G, source=node, target=center, weight="weight")
            if distance < min_distance:
                min_distance = distance
                distance_sum += min_distance
                data=str(center)+str(distance_sum)+'\n'
                file.write(data)
    return distance_sum
def find_best_medical_centers_parallel(G):
    nodes = list(G.nodes)
    min_distance_sum = float("inf")
    best_centers = None
    # 枚举所有可能的组合情况
    for centers in itertools.combinations(nodes, 3):
        # 创建多个进程执行子任务
        with multiprocessing.Pool() as pool:
            num_processes = 10
            batch_size = len(nodes) // num_processes + 1
            results = []
            for i in range(num_processes):
                start = i * batch_size
                end = min(start + batch_size, len(nodes))
                result = pool.apply_async(calculate_distance_sum_partial, args=(G, centers, start, end))
                results.append(result)
            # 合并子任务的结果
            distance_sum = sum(result.get() for result in results)
       
        # 记录距离总和最小的组合
        if distance_sum < min_distance_sum:
            min_distance_sum = distance_sum
            best_centers = centers
    return best_centers, min_distance_sum

# 定义函数，找到距离总和S1最小的医疗点组合
def find_best_medical_centers(G):
    nodes = list(G.nodes)
    min_distance_sum = float("inf")
    best_centers = None
    # 枚举所有可能的组合情况
    for centers in itertools.combinations(nodes, 3):
        distance_sum = calculate_distance_sum(G, centers)
        data=str(centers)+str(distance_sum)+'\n'
        file.write(data)
        # 记录距离总和最小的组合
        if distance_sum < min_distance_sum:
            min_distance_sum = distance_sum
            best_centers = centers
    return best_centers, min_distance_sum

# 调用函数，找到最优的医疗点组合和距离总和
#best_centers, min_distance_sum = find_best_medical_centers(G)
#file.close()
# 输出最优的医疗点组合和距离总和
#print("最优的医疗点组合为：", best_centers)
#print("距离总和为：", min_distance_sum)

best_centers, min_distance_sum = find_best_medical_centers_parallel(G)
print("最优的医疗点组合为：", best_centers)
print("距离总和为：", min_distance_sum)