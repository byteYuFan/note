# -*- coding: utf-8 -*-
"""
Created on Mon May  1 08:04:01 2023

@author: wangyufan
"""

import numpy as np
from sklearn.cluster import KMeans
import pandas as pd

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

# 使用K-means算法进行聚类，得到三个医疗点的位置
kmeans = KMeans(n_clusters=3).fit(locations[["X", "Y"]])
med_locs = kmeans.cluster_centers_

# 计算每个村庄到最近医疗点的距离，并计算距离总和S1
min_dists = np.zeros((len(locations)))
for i, loc in enumerate(locations[["X", "Y"]].values):
    dists = np.linalg.norm(med_locs - loc, axis=1)
    min_dists[i] = np.min(dists)
S1 = np.sum(min_dists)
# 打印结果
print("选中的医疗点：")
for i, loc in enumerate(med_locs):
    print(f"医疗点{i+1}: ({loc[0]:.2f}, {loc[1]:.2f})")

print("选中的医疗点位置：")
for i in range(len(med_locs)):
    print(f"医疗点{i + 1}：({med_locs[i][0]:.2f}, {med_locs[i][1]:.2f})")

print(f"\n所有村庄到最近医疗点的距离：\n{min_dists}")
print(f"\n距离总和S1：{S1:.2f}")
