#!/usr/bin/env python

import pandas as pd

import math
import matplotlib.pyplot as plt

import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans # FIXME: or KMeansMiniBatch or something

# df = pd.read_csv("wine-clustering.csv")
raw_df = pd.read_csv("housing.csv")
unique_values = raw_df['ocean_proximity'].unique()
mapping = { unique_values[i]: i for i in range(len(unique_values))}
df = raw_df.replace({ 'ocean_proximity': mapping })

total_bedrooms_mean = df['total_bedrooms'].mean()
df['total_bedrooms'].fillna(total_bedrooms_mean, inplace = True)

scaler = StandardScaler()
scaler.fit(df)

scaled_data = scaler.transform(df)

# if 1:
#     pca = PCA()
#     pca.fit(scaled_data)
#     print(df)
#     print(pca.explained_variance_ratio_)
#     cumsum = np.cumsum(pca.explained_variance_ratio_)
#     d = np.argmax(cumsum >= 0.80) + 1
#     print("d is", d)
#     exit(1)

pca = PCA(n_components=3)
pca.fit(scaled_data)

X = pca.transform(scaled_data)

kmeans = KMeans(n_init='auto', n_clusters=2)
kmeans.fit(X)

centroids = kmeans.cluster_centers_
labels = kmeans.labels_

colors = ['red', 'green', 'blue', 'yellow', 'cyan']
color_maps = [colors[i] for i in labels]

plt.scatter(X[:,0], X[:,1], c=color_maps)
plt.scatter(centroids[:,0], centroids[:,1], marker = 'x', s = 150, linewidths =
            5, zorder = 10, color = 'black')
plt.show()

fig = plt.figure(figsize=(26,6))
ax = fig.add_subplot(111, projection='3d')

ax.scatter(X[:,0], X[:,1], X[:,2], c=color_maps)
plt.show()
