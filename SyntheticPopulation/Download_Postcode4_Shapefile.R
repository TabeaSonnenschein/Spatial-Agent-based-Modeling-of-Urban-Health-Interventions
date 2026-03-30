# Download CBS Postcode4 Shapefile from PDOK
# This script downloads the postcode4 statistical data from CBS via WFS service

library(sf)
library(httr)

# WFS URL for CBS Postcode4 2024 statistics
wfs_url <- "https://service.pdok.nl/cbs/postcode4/2024/wfs/v1_0"

# Get capabilities to see available layers
capabilities_url <- paste0(wfs_url, "?request=GetCapabilities&service=WFS")
print("Fetching WFS capabilities...")

# Read the postcode4 layer
# The layer name is typically something like "postcode4"
print("Downloading postcode4 data (this may take a few minutes)...")

# Download the data
postcode4 <- st_read(
  dsn = wfs_url,
  layer = "postcode4",  # Adjust layer name if needed
  quiet = FALSE
)

# Create output directory if it doesn't exist
output_dir <- "SyntheticPopulation/Data"
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

# Save as shapefile
output_file <- file.path(output_dir, "CBS_Postcode4_2024.shp")
st_write(postcode4, output_file, delete_dsn = TRUE)

print(paste("Shapefile saved to:", output_file))
print(paste("Number of features:", nrow(postcode4)))
print("Column names:")
print(names(postcode4))

# Display basic statistics
print("Summary of the data:")
print(summary(postcode4))
