import rasterio
from rasterio.windows import from_bounds
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pyproj import Transformer

# File path
tif_path = "../data/LIDAR_Composite_10m_DTM_2022.tif"

# Define locations with coordinates (lon, lat)
locations = {
    "Shaftesbury": (-2.1987, 51.0053),
    "Petworth": (-0.6093, 50.9856),
    "Oakham (Rutland)": (-0.7323, 52.6700),
}

# Load raster and set up color map
with rasterio.open(tif_path) as src:
    raster_crs = src.crs
    transformer = Transformer.from_crs("EPSG:4326", raster_crs, always_xy=True)

    # Custom colormap: magma + blue sea
    magma = plt.get_cmap("magma", 256)
    newcolors = magma(np.linspace(0, 1, 256))
    sea_blue = np.array([0/255, 105/255, 148/255, 1])
    newcolors[0] = sea_blue
    custom_cmap = mcolors.ListedColormap(newcolors)

    # Create 1x3 subplot
    fig, axs = plt.subplots(1, 3, figsize=(18, 6))

    for ax, (label, (lon, lat)) in zip(axs, locations.items()):
        # Convert coordinates to raster CRS
        x_center, y_center = transformer.transform(lon, lat)
        buffer = 20_000  # 50 km in meters

        # Define bounding box
        left = x_center - buffer
        right = x_center + buffer
        bottom = y_center - buffer
        top = y_center + buffer

        # Read elevation window
        window = from_bounds(left, bottom, right, top, transform=src.transform)
        elevation = src.read(1, window=window)

        # Set sea (elevation < 0) to 0 index for blue
        elevation[elevation < 0] = 0

        # Plot map
        ax.imshow(elevation, cmap=custom_cmap)
        ax.set_title(label, fontsize=14)
        ax.axis("off")

# Clean layout and show
plt.tight_layout()
plt.savefig("elevation_panels.png", dpi=300, bbox_inches="tight")


