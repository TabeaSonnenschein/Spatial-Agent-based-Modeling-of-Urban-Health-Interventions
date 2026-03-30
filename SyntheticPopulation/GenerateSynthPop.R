# # if running for the first time, uncomment the following lines to install required packages
# install.packages(c("devtools", "tidyr", "dplyr","sf", "httr", "cbsodataR", "ggspatial", "ggplot2"))
# library(devtools)
# install_github("TabeaSonnenschein/GenSynthPop", dependencies = TRUE, force = TRUE)

library(GenSynthPop)
library(tidyr)
library(dplyr)
library(cbsodataR)
library(sf)
library(httr)
library(ggplot2)
library(ggspatial)

# read the CBSfetchingAndPrepFunctions.R
get_script_dir <- function() {
  if (!is.null(sys.frame(1)$ofile)) {
    return(dirname(normalizePath(sys.frame(1)$ofile)))
  }
  if (requireNamespace("rstudioapi", quietly = TRUE) && rstudioapi::isAvailable()) {
    return(dirname(rstudioapi::getActiveDocumentContext()$path))
  }
  getwd()
}

script_dir <- get_script_dir()
source(file.path(script_dir, "CBSfetchingAndPrepFunctions.R"))


###########################################################################
####### COLLECTING THE DATA FOR THE SYNTHETIC POPULATION ##################
###########################################################################

municipalities = c("Amsterdam", "Ouder-Amstel", "Diemen", "Amstelveen")
regionfilesuffix = "Amsterdam"
year = 2025
PopDataFolder = "D:\\OneDrive - Universiteit Utrecht\\Documents\\Utrecht Postdoc\\EXPOSOME-NL Postdoc\\AmsterdamCaseStudy\\Data\\Population"
# PopDataFolder = "C:\\Users\\6513301\\OneDrive - Universiteit Utrecht\\Documents\\Utrecht Postdoc\\EXPOSOME-NL Postdoc\\AmsterdamCaseStudy\\Data\\Population"
setwd(PopDataFolder)
set.seed(123)  # for reproducibility  
CRS = 28992  # Amersfoort / RD New


####################################
##### Retrieving neighborhoods #####
####################################
neighborhood_stats <- get_cbs_neighborhoods("86165NED", municipalities, "Buurt")
neighborhood_dflist <- rename_cbs_columns(neighborhood_stats)
neighborhood_stats = neighborhood_dflist$df
renaming_table = neighborhood_dflist$old_new_names
write.csv(neighborhood_stats, paste0("CBS_", regionfilesuffix, "_Neighborhoods_", year, ".csv"), row.names = FALSE)
write.csv(renaming_table, paste0("CBS_", regionfilesuffix, "_Neighborhoods_", year, "_RenamingTable.csv"), row.names = FALSE)

###################################
##### Get population totals ##########
###################################

# Explore the table structure to see available filters
meta_info <- cbs_get_meta("03759NED")
print(names(meta_info))  # See what metadata is available

# Check available regions - show only Key and Title
regions <- meta_info$RegioS
regions_simple <- regions[, c("Key", "Title")]
print(regions_simple)  # See region codes and names
periods <- meta_info$Perioden
print(tail(periods, 10))  # See recent

# find the keys for the municipalities of interest
municipality_keys <- sapply(municipalities, function(mun) {
  key <- regions$Key[regions$Title == mun]
  if (length(key) == 0) {
    warning(paste("Municipality", mun, "not found in CBS regions."))
    return(NA)
  }
  return(key)
})

# Now fetch data with filters
# Filter by period (year) and region (Amsterdam)
pop_totals_regio = cbs_get_data("03759NED", 
                                Perioden = paste0(year, "JJ00"),  # Year format
                                RegioS = municipality_keys)  # Region filter

# Clean and translate the population data
pop_totals_clean <- clean_cbs_population_data(pop_totals_regio)
pop_totals_regio_clean <- pop_totals_clean$df
# replace the municipality column with names instead of codes using the municipality_keys
pop_totals_regio_clean$municipality <- sapply(pop_totals_regio_clean$municipality, function(code) {
  name <- names(municipality_keys)[municipality_keys == code]
  if (length(name) == 0) {
    return(code)  # return code if not found
  }
  return(name)
})
renaming_table <- pop_totals_clean$translation_map
print(head(pop_totals_regio_clean))

write.csv(pop_totals_regio_clean, paste0("CBS_", regionfilesuffix, "_Population_Totals_", year, ".csv"), row.names = FALSE)
write.csv(renaming_table, paste0("CBS_", regionfilesuffix, "_Population_Totals_", year, "_RenamingTable.csv"), row.names = FALSE)


# cbs_get_meta("83502NED")
# pop_totals_postcode <- cbs_get_data("83502NED", Perioden = paste0(year, "JJ00"))                                    )  


################################################
##### Initiating the synthetic population ######
################################################

setwd(PopDataFolder)

## Initialize the agent_df
neigh_df = read.csv(paste0("CBS_", regionfilesuffix, "_Neighborhoods_", year, ".csv"))
agent_neighborhoods = rep(neigh_df$NeighbCode, times = neigh_df$PopulationTotal)
agent_count = sum(neigh_df$PopulationTotal)
agent_ids = paste0("Agent_", 0:(agent_count - 1))
agent_df = data.frame(agent_id = agent_ids, 
                      NeighbCode = agent_neighborhoods)


## add age group attribute
agecols = c("age0_15", "age15_25", "age25_45", "age45_65", "age65plus")
ageneigh_df = as.data.frame(neigh_df[unlist(c("NeighbCode", agecols))] %>%
  pivot_longer(cols = all_of(agecols), 
               names_to = "age_group", 
               values_to = "count"))    # Create a new column for counts

agent_df = Conditional_attribute_adder(df = agent_df, 
                            df_contingency = ageneigh_df, 
                            target_attribute = "age_group", 
                            group_by = c("NeighbCode"))

agent_df = agent_df[sample(nrow(agent_df)), ] #shuffle the agent_df to randomize the order
print(head(agent_df, 10))
write.csv(agent_df, paste0(regionfilesuffix,"SynthPop", year, ".csv"), row.names = FALSE)


## add municipality attribute (Optional if multiple municipalities) 
neighMunicipal_df = neigh_df[, c("NeighbCode", "municipality")]
agent_df = merge(agent_df, neighMunicipal_df, by = "NeighbCode", all.x = TRUE)
print(head(agent_df, 10))
write.csv(agent_df, paste0(regionfilesuffix,"SynthPop", year, ".csv"), row.names = FALSE)


## add age year attribute
sex_age_df = read.csv(paste0("CBS_", regionfilesuffix, "_Population_Totals_", year, ".csv")) # columns integer age, sex, counts
age_df = sex_age_df[sex_age_df$sex == "total" & sex_age_df$maritalStatus == "total" & !(sex_age_df$age %in% c("Total", "95 or older")), c("age", "municipality", "population")] 
age_df$age_group = cut(as.numeric(age_df$age),
                       breaks = c(-1, 14, 24, 44, 64, Inf),
                       labels = c("age0_15", "age15_25", "age25_45", "age45_65", "age65plus"))
age_df$age_group[age_df$age == "105 or older"] <- "age65plus"
age_df$age[age_df$age == "105 or older"] <- "105"
summary(age_df$age_group) # check if there are any NAs and solve if the case
print(head(age_df, 10))
colnames(age_df)[colnames(age_df) == "population"] <- "count"

agent_df$municipality_age_group <- paste(agent_df$municipality, agent_df$age_group, sep = "__")
age_df$municipality_age_group <- paste(age_df$municipality, age_df$age_group, sep = "__")
agent_df = Conditional_attribute_adder(df = agent_df,
                            df_contingency = age_df,
                            target_attribute = "age",
                            group_by = c("municipality_age_group"))
agent_df$municipality_age_group <- NULL
agent_df = agent_df[sample(nrow(agent_df)), ] #shuffle the agent_df to randomize the order
print(head(agent_df, 10))
write.csv(agent_df, paste0(regionfilesuffix,"SynthPop", year, ".csv"), row.names = FALSE)


## add sex attribute
sex_age_df = read.csv(paste0("CBS_", regionfilesuffix, "_Population_Totals_", year, ".csv")) # columns integer age, sex, counts
sex_df = sex_age_df[sex_age_df$sex != "total" & sex_age_df$maritalStatus == "total" & !(sex_age_df$age %in% c("Total", "95 or older")), c("municipality", "age", "sex", "population")] 
sex_df$age[sex_df$age == "105 or older"] <- "105"
colnames(sex_df)[colnames(sex_df) == "population"] <- "count"
sex_df <- sex_df %>%
  group_by(age, sex) %>% 
  summarise(count = sum(count), .groups = "drop")


sexcols = c("male", "female")

sexneigh_df <- neigh_df[unlist(c("NeighbCode", sexcols))] %>%
  pivot_longer(cols = all_of(sexcols), 
               names_to = "sex", 
               values_to = "count")  
sexneigh_df <- as.data.frame(sexneigh_df)

   
agent_df = Conditional_attribute_adder(df = agent_df, 
                            df_contingency = sex_df , 
                            target_attribute = "sex", 
                            group_by = c("NeighbCode"),
                            margins= list( sexneigh_df),
                            margins_names= c("sex"))
agent_df = agent_df[sample(nrow(agent_df)), ] #shuffle the agent_df to randomize the order
print(head(agent_df, 10))
write.csv(agent_df, paste0(regionfilesuffix,"SynthPop", year, ".csv"), row.names = FALSE)


####################################
# download the postcode4 shapefile
postcode4 <- download_cbs_postcode4(2024, save_to_file = FALSE, geometry_only = TRUE)
postcode4 <- st_transform(postcode4, CRS)
# saving the postcode4 shapefile
st_write(postcode4, "Postcode4_2024.shp")

# download the buurt shapefile
buurten_2024 <- download_cbs_wijken_buurten(2024, spatial_level = "buurt",  save_to_file = FALSE, geometry_only = TRUE)
# find the neighborhoods in the region of interest
buurten_2024 <- st_transform(buurten_2024, CRS)
region_buurten_2024 <- buurten_2024[buurten_2024$buurtcode %in% unique(neigh_df$NeighbCode), ]
st_write(region_buurten_2024, paste0("CBS_", regionfilesuffix, "_Buurten_2024.shp"))


plot(st_geometry(region_buurten_2024), col = NA, border = "blue", lwd = 2)
plot(st_geometry(postcode4), col = NA, border = "red", add = TRUE)



ggplot(region_buurten_2024) + 
  geom_sf() +
  theme_minimal()


                      





### add migration background attribute
agent_df = read.csv(paste0(regionfilesuffix,"SynthPop", year, ".csv"))
neigh_df = read.csv(paste0("CBS_", regionfilesuffix, "_Neighborhoods_", year, ".csv"))

#     "Born_Netherlands" = "Nederland_17",
#     "Born_EuropeExclNL" = "EuropaExclusiefNederland_18",
#     "Born_OutsideEurope" = "BuitenEuropa_19",
#     "Nationality_Netherlands" = "Nederland_20",
#     "Nationality_EuropeExclNL" = "EuropaExclusiefNederland_21",
#     "Nationality_OutsideEurope" = "BuitenEuropa_22",


# 85384NED Bevolking leeftijd, herkomstland, geboorteland (ouders)
# 85458NED Bevolking; geslacht, leeftijd, herkomstland, geboorteland, regio
# 85640NED Bevolking 1 januari Herkomstland, geslacht, viercijferige postcode

           


# 84910NED 2020 age, sex, migration background, HH composition
# migration background age, sex
# 71493ned 2018 sex, age, absolved education,
# migration background
# absolved education
# level
# age, sex,
# migration
# background
# 71450ned 2019 sex, age, current education,
# migration background
# current education level age, sex,
# migration
# background
# 84640NED 2018 sex, age, migration background, people with income
# income decile age, sex,
# migration
# background
# 83931NED 2020 sex, age, migration background, income decile
# income decile age, sex,
# migration
# background
# 50052NED 2016 neighborhood, BMI class BMI class neighborhood
# 83021NED 2020 sex, age, HH position, migration background, BMI class
# BMI class age, sex,
# migration
# background,
# HH position
# 71486ned 2020 education type, age Nr children, HH size age
# ODIN2018 2018 car access, drive habit, bike
# habit, transit habit, education,
# age, sex, HH type
# car access, drive habit,
# bike habit, transit
# habit
# education, age,
# sex, HH type
# https://www.cb
# s.nl/nl-nl/long
# read/statistis
# che-trends/2023
# /wie-rijdt-er-e
# lektrisch2023 EV-ownership, sex, age, region, income, HH type
# EV access 2025, 2030 sex, age region,
# income, H

edu_age_sex_df = read.csv(paste0("CBS_", regionfilesuffix, "_Edu_Sex_Age_Statistics_", year, ".csv")) # columns age_group, sex, education_level counts

educols = c("high", "middle", "low")

eduneigh_df <- neigh_df[unlist(c("NeighbCode", educols))] %>%
  pivot_longer(cols = all_of(educols), 
               names_to = "education_level", 
               values_to = "count")  
eduneigh_df <- as.data.frame(eduneigh_df)

neighwithmissingdata = unique(eduneigh_df$NeighbCode[is.na(eduneigh_df$count)])
eduneigh_df = eduneigh_df[!eduneigh_df$NeighbCode %in% neighwithmissingdata, ]

agent_df = Conditional_attribute_adder(df = agent_df, 
                            df_contingency = edu_age_sex_df , 
                            target_attribute = "education_level", 
                            group_by = c("NeighbCode"),
                            margins= list(ageneigh_df, sexneigh_df, eduneigh_df),
                            margins_names= c("age_group", "sex", "education_level"))
print(head(agent_df))

write.csv(agent_df, paste0(regionfilesuffix,"SynthPop", year, ".csv"), row.names = FALSE)
