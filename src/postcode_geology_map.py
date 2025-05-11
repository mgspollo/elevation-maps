import rasterio
from rasterio.windows import from_bounds
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pyproj import Transformer
import geopandas as gpd
from shapely.geometry import box

# File paths
tif_path = "../data/LIDAR_Composite_10m_DTM_2022.tif"
geology_path = "../data/geology/625k_V5_BEDROCK_Geology_Polygons.shp"

# Define locations: (lon, lat)
locations = {
    "Shaftesbury": (-2.1987, 51.0053),
    "Petworth": (-0.6093, 50.9856),
    "Oakham (Rutland)": (-0.7323, 52.6700),
}

# Read geology shapefile
geology_gdf = gpd.read_file(geology_path)

# Prepare projection transformer
with rasterio.open(tif_path) as src:
    raster_crs = src.crs
    transformer = Transformer.from_crs("EPSG:4326", raster_crs, always_xy=True)

    # Reproject geology to match raster
    if geology_gdf.crs != raster_crs:
        geology_gdf = geology_gdf.to_crs(raster_crs)

    # Color map setup for elevation
    magma = plt.get_cmap("magma", 256)
    newcolors = magma(np.linspace(0, 1, 256))
    sea_blue = np.array([0/255, 105/255, 148/255, 1])
    newcolors[0] = sea_blue
    custom_cmap = mcolors.ListedColormap(newcolors)

    # Create 2x3 subplot grid
    fig, axs = plt.subplots(2, 3, figsize=(18, 12))

    for col_idx, (label, (lon, lat)) in enumerate(locations.items()):
        # Transform coordinates to raster CRS
        x_center, y_center = transformer.transform(lon, lat)
        buffer = 50_000  # 50 km

        # Bounding box
        left, right = x_center - buffer, x_center + buffer
        bottom, top = y_center - buffer, y_center + buffer
        bbox = box(left, bottom, right, top)

        ### Elevation map (top row) ###
        window = from_bounds(left, bottom, right, top, transform=src.transform)
        elevation = src.read(1, window=window)
        elevation[elevation < 0] = 0

        ax_top = axs[0, col_idx]
        ax_top.imshow(elevation, cmap=custom_cmap)
        ax_top.set_title(label, fontsize=14)
        ax_top.axis("off")

        ### Geology map (bottom row) ###
        ax_bottom = axs[1, col_idx]
        # Clip geology to bbox
        clipped_geology = geology_gdf.clip(bbox)
        if clipped_geology.empty:
            ax_bottom.set_title(f"{label} (No geology data)")
        else:
            clipped_geology.plot(ax=ax_bottom, column=None, cmap="tab20", linewidth=0, edgecolor='none')

        ax_bottom.set_xlim(left, right)
        ax_bottom.set_ylim(bottom, top)
        ax_bottom.axis("off")

# Final layout
plt.tight_layout()
plt.savefig("geology_elevation_map.png")
