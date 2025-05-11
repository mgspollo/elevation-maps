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
rivers_path = "../data/rivers/WatercourseLink.shp"

# Define locations: (lon, lat)
locations = {
    "Shaftesbury": (-2.1987, 51.0053),
    "Petworth": (-0.6093, 50.9856),
    "Oakham (Rutland)": (-0.7323, 52.6700),
}

# Read vector data
geology_gdf = gpd.read_file(geology_path)
rivers_gdf = gpd.read_file(rivers_path)

with rasterio.open(tif_path) as src:
    raster_crs = src.crs
    transformer = Transformer.from_crs("EPSG:4326", raster_crs, always_xy=True)

    # Reproject vector layers to match raster
    geology_gdf = geology_gdf.to_crs(raster_crs)
    rivers_gdf = rivers_gdf.to_crs(raster_crs)

    # Create custom colormap (magma with blue sea)
    magma = plt.get_cmap("magma", 256)
    newcolors = magma(np.linspace(0, 1, 256))
    sea_blue = np.array([0/255, 105/255, 148/255, 1])
    newcolors[0] = sea_blue
    custom_cmap = mcolors.ListedColormap(newcolors)

    # Create 3x3 plot grid
    fig, axs = plt.subplots(3, 3, figsize=(18, 18))

    for col_idx, (label, (lon, lat)) in enumerate(locations.items()):
        # Transform point
        x_center, y_center = transformer.transform(lon, lat)
        buffer = 20_000  # 20 km
        left, right = x_center - buffer, x_center + buffer
        bottom, top = y_center - buffer, y_center + buffer
        bbox = box(left, bottom, right, top)

        ### Elevation ###
        window = from_bounds(left, bottom, right, top, transform=src.transform)
        elevation = src.read(1, window=window)
        elevation[elevation < 0] = 0

        axs[0, col_idx].imshow(elevation, cmap=custom_cmap)
        axs[0, col_idx].set_title(label + " – Elevation", fontsize=14)
        axs[0, col_idx].axis("off")

        ### Geology ###
        clipped_geology = geology_gdf.clip(bbox)
        axs[1, col_idx].set_title(label + " – Geology", fontsize=14)
        if not clipped_geology.empty:
            clipped_geology.plot(ax=axs[1, col_idx], column=None, cmap="tab20", linewidth=0, edgecolor='none')
        axs[1, col_idx].set_xlim(left, right)
        axs[1, col_idx].set_ylim(bottom, top)
        axs[1, col_idx].axis("off")

        ### Rivers ###
        clipped_rivers = rivers_gdf.clip(bbox)
        axs[2, col_idx].set_title(label + " – Rivers", fontsize=14)
        if not clipped_rivers.empty:
            clipped_rivers.plot(ax=axs[2, col_idx], color="blue", linewidth=0.7)
        axs[2, col_idx].set_xlim(left, right)
        axs[2, col_idx].set_ylim(bottom, top)
        axs[2, col_idx].axis("off")

# Final layout
plt.tight_layout()
plt.savefig("rivers_geology_elevation_map.png")