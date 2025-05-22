import osmnx as ox
import networkx as nx
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import Point
from scipy.spatial import cKDTree
from scipy.interpolate import griddata
import os
from pyrosm import OSM

# Parameters
tile_size_deg = 1.0  # 1 degree tiles
cutoff_meters = 50000  # 50 km max driving distance
resolution = 200  # interpolation resolution (number of pixels per side)
data_dir = "./access_tiles"
os.makedirs(data_dir, exist_ok=True)

# Load OSM PBF once
osm = OSM("health_filtered.osm.pbf")
all_pois = osm.get_pois()
all_pois = all_pois[all_pois.geometry.type == "Point"]

# Tile generator for USA bounding box
min_lon, min_lat, max_lon, max_lat = -125, 24, -66, 50


def generate_tiles():
    lon = min_lon
    while lon < max_lon:
        lat = min_lat
        while lat < max_lat:
            yield (lon, lat, lon + tile_size_deg, lat + tile_size_deg)
            lat += tile_size_deg
        lon += tile_size_deg


def nearest_node_from_point(G, point, kdtree, node_ids, coords):
    idx = kdtree.query([point.x, point.y])[1]
    return node_ids[idx]


def process_tile(bbox):
    tile_name = f"{bbox[0]:.2f}_{bbox[1]:.2f}"
    out_path = os.path.join(data_dir, tile_name + ".tif")
    if os.path.exists(out_path):
        print(f"Skipping existing tile: {tile_name}")
        return

    print(f"Processing tile: {tile_name}")
    try:
        G = ox.graph_from_bbox(*bbox[::-1], network_type="drive")
        G_proj = ox.project_graph(G)
        nodes_proj, _ = ox.graph_to_gdfs(G_proj)

        # Filter hospitals within bbox
        pois_within = all_pois.cx[bbox[0] : bbox[2], bbox[1] : bbox[3]]
        if pois_within.empty:
            print("No hospitals in tile")
            return
        hosp_proj = pois_within.to_crs(nodes_proj.crs)

        # KDTree for nearest node
        coords = np.array(
            [(data["x"], data["y"]) for node, data in G_proj.nodes(data=True)]
        )
        node_ids = list(G_proj.nodes)
        kdtree = cKDTree(coords)

        hospital_nodes = [
            nearest_node_from_point(G_proj, pt, kdtree, node_ids, coords)
            for pt in hosp_proj.geometry
        ]

        all_lengths = {}
        for hn in hospital_nodes:
            lengths = nx.single_source_dijkstra_path_length(
                G_proj, hn, weight="length", cutoff=cutoff_meters
            )
            for node, dist in lengths.items():
                if node not in all_lengths or dist < all_lengths[node]:
                    all_lengths[node] = dist

        # Interpolate
        xs, ys, ds = [], [], []
        for node, dist in all_lengths.items():
            x = G_proj.nodes[node]["x"]
            y = G_proj.nodes[node]["y"]
            xs.append(x)
            ys.append(y)
            ds.append(dist)

        if len(xs) < 10:
            print("Too few data points")
            return

        grid_x, grid_y = np.meshgrid(
            np.linspace(min(xs), max(xs), resolution),
            np.linspace(min(ys), max(ys), resolution),
        )
        grid_z = griddata((xs, ys), ds, (grid_x, grid_y), method="cubic")

        transform = from_origin(
            min(xs),
            max(ys),
            (max(xs) - min(xs)) / resolution,
            (max(ys) - min(ys)) / resolution,
        )

        with rasterio.open(
            out_path,
            "w",
            driver="GTiff",
            height=grid_z.shape[0],
            width=grid_z.shape[1],
            count=1,
            dtype=grid_z.dtype,
            crs=nodes_proj.crs.to_string(),
            transform=transform,
        ) as dst:
            dst.write(grid_z, 1)

    except Exception as e:
        print(f"Failed to process tile {tile_name}: {e}")


# Run batch
for bbox in generate_tiles():
    process_tile(bbox)

print("All tiles processed.")
