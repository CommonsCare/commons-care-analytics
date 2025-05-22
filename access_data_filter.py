from pyrosm import OSM
import geopandas as gpd
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Point, box
from scipy.spatial import cKDTree
import contextily as ctx
import osmnx as ox

# Define bounding box
bbox = [-81.040, 34.000, -81.020, 34.020]
bbox_geom = box(*bbox)

# ----------------------------
# 1. Load hospitals
# ----------------------------
osm_hospital = OSM("health_filtered.osm.pbf", bounding_box=bbox)
pois = osm_hospital.get_pois()
pois = pois[pois.geometry.type == "Point"]

# ----------------------------
# 2. Road network (projected)
# ----------------------------
G = ox.graph_from_bbox(bbox, network_type="drive")
G_proj = ox.project_graph(G)
nodes_proj, edges_proj = ox.graph_to_gdfs(G_proj)
pois = pois.to_crs(nodes_proj.crs)


import osmnx as ox
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point
from scipy.spatial import cKDTree
from scipy.interpolate import griddata

# Step 1: Get nearest graph nodes to hospitals
hospital_points = pois.geometry
G_proj = ox.project_graph(G)
nodes_proj, edges_proj = ox.graph_to_gdfs(G_proj)

node_coords = np.array(
    [(data["x"], data["y"]) for node, data in G_proj.nodes(data=True)]
)
node_ids = list(G_proj.nodes)
kdtree = cKDTree(node_coords)


def nearest_node(point):
    idx = kdtree.query([point.x, point.y])[1]
    return node_ids[idx]


hospital_nodes = [nearest_node(p) for p in hospital_points]

# Step 2: Calculate shortest path distances to all nodes from all hospitals
all_lengths = {}
for hn in hospital_nodes:
    lengths = nx.single_source_dijkstra_path_length(
        G_proj, hn, weight="length", cutoff=3000
    )  # up to 3 km
    for node, dist in lengths.items():
        if node in all_lengths:
            all_lengths[node] = min(
                all_lengths[node], dist
            )  # keep shortest among hospitals
        else:
            all_lengths[node] = dist

# Step 3: Prepare coordinate and distance arrays
xs, ys, ds = [], [], []
for node, dist in all_lengths.items():
    x = G_proj.nodes[node]["x"]
    y = G_proj.nodes[node]["y"]
    xs.append(x)
    ys.append(y)
    ds.append(dist)

# Step 4: Interpolate over grid
grid_x, grid_y = np.mgrid[min(xs) : max(xs) : 500j, min(ys) : max(ys) : 500j]
grid_z = griddata((xs, ys), ds, (grid_x, grid_y), method="cubic")

# Step 5: Plot smooth heatmap
fig, ax = plt.subplots(figsize=(10, 10))
heatmap = ax.imshow(
    grid_z.T,
    extent=(min(xs), max(xs), min(ys), max(ys)),
    origin="lower",
    cmap="hot",
    alpha=0.7,
)

edges_proj.plot(ax=ax, linewidth=0.3, color="gray")
pois.plot(ax=ax, color="blue", markersize=30, label="Hospitals")

cbar = plt.colorbar(heatmap, ax=ax, fraction=0.036, pad=0.04)
cbar.set_label("Driving Distance (meters)")

ax.set_title("Smooth Heatmap of Driving Distance from Hospitals", fontsize=14)
ax.set_axis_off()
plt.tight_layout()
plt.show()
