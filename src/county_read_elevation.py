import rasterio
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from rasterio.mask import mask
import os

tif_path = "../data/LIDAR_Composite_10m_DTM_2022.tif"
shapefile_path = "../data/counties/CTYUA_MAY_2023_UK_BGC.shp"
output_folder = "county_elevation_maps"

# Load county boundaries
counties = gpd.read_file(shapefile_path)

# Filter for Rutland

# Open the elevation .tif file
# Create output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Load county boundaries
counties = gpd.read_file(shapefile_path)

# Loop through each county and generate maps
for index, county in counties.iterrows():
    county_name = county["CTYUA23NM"].replace(" ", "_")  # Clean name for file saving
    print(f"Processing: {county_name}")  # Debugging output

    # Open the elevation .tif file
    with rasterio.open(tif_path) as src:
        try:
            # Mask the raster to include only this county
            out_image, out_transform = mask(src, [county.geometry], crop=True, nodata=np.nan)

            # Extract elevation data
            elevation_data = out_image[0]

            # Set negative elevations to -1
            elevation_data[elevation_data < 0] = -1

            # Create figure
            fig, ax = plt.subplots(figsize=(8, 6))

            # Plot the elevation inside the county
            img = ax.imshow(elevation_data, cmap="terrain")

            # Add a buffer around the county for better visualization
            buffer = 0.05
            ax.set_xlim(-buffer, elevation_data.shape[1] + buffer)
            ax.set_ylim(elevation_data.shape[0] + buffer, -buffer)

            # Set background (non-county areas) to white
            ax.set_facecolor("white")

            # Add colorbar and title
            plt.colorbar(img, label="Elevation (m)")
            plt.title(f"Elevation Map of {county['CTYUA23NM']}")

            # Save the figure
            output_path = os.path.join(output_folder, f"{county_name}.png")
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()  # Close the figure to free memory

        except Exception as e:
            print(f"Error processing {county_name}: {e}")

print(f"Maps saved in '{output_folder}' folder.")
