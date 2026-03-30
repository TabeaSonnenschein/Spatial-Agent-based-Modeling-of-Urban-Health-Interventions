# Load necessary libraries
library(tidyverse)
library(sf)
library(raster)
library(terra)
library(doParallel)
library(foreach)
library(progress)  
library(SpaDES)


# Retrieve data with municipal boundaries from PDOK
municipalBoundaries <- st_read("https://service.pdok.nl/cbs/gebiedsindelingen/2024/wfs/v1_0?request=GetFeature&service=WFS&version=1.1.0&outputFormat=application%2Fjson&typeName=gebiedsindelingen:gemeente_gegeneraliseerd")

# Retrieve data with population density per municiplaties from CBS
bevolkingdichtheid <- read.csv("/path/to/Bevolkingsdichtheid2024.csv", sep = ";")

# urban density - rename Gemeente to be able to perform merging
bevolkingdichtheid <- bevolkingdichtheid %>%
  rename(statnaam = Gemeente)

# Merge municipalBoundaries with bevolkingdichtheid
municipalBoundaries_merged <- inner_join(municipalBoundaries, bevolkingdichtheid, by="statnaam")

missing <- c("'s-Gravenhage", "Utrecht", "Groningen")

municipalBoundaries_missing <- municipalBoundaries %>%
  filter(statnaam %in% missing) %>%
  mutate(Inwonersperkmsqland = c(6868, 3991, 1314)) %>%
  relocate(Inwonersperkmsqland, .before = geometry)

# remove the gap in Inwonersperkmsqland
municipalBoundaries_merged <- municipalBoundaries_merged %>%
  mutate(Inwonersperkmsqland = as.numeric(gsub(" ", "", Inwonersperkmsqland)))

municipalBoundaries_merged <- rbind(municipalBoundaries_merged, municipalBoundaries_missing)

municipalBoundaries<- municipalBoundaries_merged %>%
  filter(Inwonersperkmsqland > 1000)

urban_list <- municipalBoundaries$statnaam

rm(municipalBoundaries_merged,municipalBoundaries_missing,missing,bevolkingdichtheid)

# load datasets:
raster_fvc <- raster("/path/to/fvc_test.tif")
merged_svf <- raster("/path/to/merged_svf_all.tif")

# Clip sky view factor
# Set output directory
output_directory <- "/path/to/"

# Loop through each city in the urban_list
for (city in urban_list) {
  
  # Filter the municipal boundaries for the current city
  boundary <- municipalBoundaries %>% 
    filter(statnaam == city)
  
  # Crop the merged_svf to the bounding box of the current city's boundary
  cropped_svf <- crop(merged_svf, st_bbox(boundary))
  
  # Clip the cropped SVF using the current city's boundary
  clipped_urban <- mask(cropped_svf, boundary)
  
  # Define the file name based on the current city's name
  output_file <- paste0(output_directory, city, ".tif")
  
  # Write the clipped urban SVF to a file
  writeRaster(clipped_urban, output_file, overwrite = TRUE)
  
  # Optionally print a message to monitor progress
  message(paste("Processed:", city))
}

# Set up parallel processing
num_cores <- 8
cl <- makeCluster(num_cores)
registerDoParallel(cl)

# Define the function for tile processing (same as before)
process_tile <- function(tile, raster_fvc) {
  ext <- tile@extent
  offset_x <- 50
  offset_y <- 50
  
  xmin <- as.numeric(ext@xmin)
  xmax <- as.numeric(ext@xmax)
  ymin <- as.numeric(ext@ymin)
  ymax <- as.numeric(ext@ymax)
  
  new_ext <- raster::extent(xmin - offset_x, xmax + offset_x, ymin - offset_y, ymax + offset_y)
  
  fvc <- crop(raster_fvc, new_ext)
  fvc <- as(fvc, "Raster")
  
  ncol_base <- ceiling((xmax(fvc) - xmin(fvc)) / 5)
  nrow_base <- ceiling((ymax(fvc) - ymin(fvc)) / 5)
  
  base <- raster(nrows = nrow_base, ncols = ncol_base,
                 xmn = xmin(fvc), xmx = xmax(fvc),
                 ymn = ymin(fvc), ymx = ymax(fvc),
                 crs = crs(fvc))
  
  fvc_resampled <- resample(fvc, base, method = "ngb")
  
  focal_window <- focalMat(fvc_resampled, 50, type = "circle")
  
  mean_veg_cover <- focal(fvc_resampled, w = focal_window, fun = sum, na.rm = TRUE) / sum(focal_window)
  
  mean_veg_cover_cropped <- crop(mean_veg_cover, ext)
  UHI <- (2 - tile - mean_veg_cover_cropped) * (1)
  
  return(UHI)
}

# Progress bar setup
pb <- progress_bar$new(
  format = "  Processing [:bar] :percent in :elapsed | Remaining: :eta",
  total = length(urban_list),   # Total number of cities
  width = 60                    # Width of the progress bar
)

# Main loop to process each urban area
for (city in urban_list) {
  
  # Construct the file path dynamically for each city
  urban_file <- paste0("/path/to/", city, ".tif")
  
  if (file.exists(urban_file)) {
    # Read the Urban raster for the current city
    UrbanCL <- raster(urban_file)
    
    # Set the CRS for both rasters
    crs(UrbanCL) <- CRS('+init=EPSG:28992')
    crs(raster_fvc) <- CRS('+init=EPSG:28992')
    
    # Split the UrbanCL raster into tiles (8x8 grid)
    tiles <- splitRaster(UrbanCL, nx = 8, ny = 8)  # Create 64 tiles
    
    # Process tiles in parallel
    results <- foreach(i = seq_along(tiles), .packages = c("raster", "terra")) %dopar% {
      process_tile(tiles[[i]], raster_fvc)
    }
    
    # Combine the processed tiles into one raster
    UHI_combined <- do.call(merge, results)
    
    # Save the result for the current city
    output_file <- paste0("/path/to/", city, ".tif")
    writeRaster(UHI_combined, filename = output_file, format = "GTiff", overwrite = TRUE)
    
    message(paste("Processed and saved UHI raster for:", city))
  } else {
    warning(paste("File not found for:", city))
  }
  
  # Update the progress bar after each city is processed
  pb$tick()
}

# Stop the cluster after processing all cities
stopCluster(cl)

########## INSERTING RURAL MEASUREMENTS ##########
# Define paths
rural_measurements_path <- "/path/to/UHImax_allSTN.csv"
uhi_base_path <- "/path/to/"
output_path <- "/path/to/"

# Read the rural measurements CSV
rural_measurements <- read.csv(rural_measurements_path)

# Cities you want to process (ensure the city names in this list match exactly with your file names)
cities <- urban_list

# Loop through each city
for (city in cities) {
  
  # Create the corresponding UHI raster file path
  uhi_file <- file.path(uhi_base_path, paste0(city, ".tif"))
  
  # Check if the file exists (skip the city if the file doesn't exist)
  if (file.exists(uhi_file)) {
    
    # Load the UHI raster
    uhi_raster <- raster(uhi_file)
    
    # Get the corresponding rural value from the CSV
    rural_value <- rural_measurements %>% filter(urban_area == city) %>% pull(rural)
    
    # If the rural value exists, multiply the UHI raster by the rural value
    if (length(rural_value) > 0) {
      uhi_raster_modified <- uhi_raster * rural_value
      
      # Save the modified raster to the output directory
      output_file <- file.path(output_path, paste0("UHImax_", city, ".tif"))
      writeRaster(uhi_raster_modified, output_file, format="GTiff", overwrite=TRUE)
    }
  }
}


