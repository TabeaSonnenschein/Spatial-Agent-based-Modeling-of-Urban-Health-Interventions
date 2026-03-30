library(cbsodataR)




#' Download CBS neighborhoods for one or more cities
#'
#' @param table_id CBS table ID (e.g., "86165NED" for 2025, "85984NED" for 2024, "85618NED" for 2023)
#' @param municipalities Character vector with one or more municipality names (e.g., "Amsterdam" or c("Amsterdam", "Utrecht"))
#' @param spatial_level Level of spatial detail ("Buurt" or "Wijk"), so neighborhood or district
#' @return data.frame filtered for city/cities and spatial level
#' @examples
#' df <- get_cbs_neighborhoods("86165NED", "Amsterdam", "Buurt")
#' df_multi <- get_cbs_neighborhoods("86165NED", c("Amsterdam", "Utrecht"), "Buurt")
get_cbs_neighborhoods <- function(table_id, municipalities, spatial_level = c("Buurt", "Wijk")) {
  
  spatial_level <- match.arg(spatial_level)  # ensure valid input
  
  # Ensure municipalities is a character vector and trim whitespace
  municipalities <- trimws(as.character(municipalities))
  
  message("Downloading CBS table ", table_id, " …")
  df <- cbs_get_data(table_id)
  
  # Check the relevant column names
  # Some tables use Gemeentenaam_1 / SoortRegio_2
  municipality_col <- grep("Gemeente", names(df), value = TRUE)[1]
  regio_col   <- grep("SoortRegio", names(df), value = TRUE)[1]
  
  if (is.na(municipality_col) || is.na(regio_col)) {
    stop("Could not find required columns for filtering municipality and region type.")
  }
  
  # strip empty space in all columns
  df[] <- lapply(df, function(x) if(is.character(x)) trimws(x) else x)

  # check whether the specified municipalities exist in the data
  missing_municipalities <- setdiff(municipalities, df[[municipality_col]])
  if (length(missing_municipalities) > 0) {
    message("List of available municipalities:")
    message((paste(unique(df[[municipality_col]]), collapse = ", ")))
    stop("Municipality(ies) not found: ", paste(missing_municipalities, collapse = ", "))
  }

  df_filtered <- df %>%
    filter(.data[[municipality_col]] %in% municipalities,
           .data[[regio_col]] == spatial_level)
  
  message("Filtered ", nrow(df_filtered), " rows for ", paste(municipalities, collapse = ", "), " (", spatial_level, ")")
  message("Available columns in the filtered data:")
  message(paste(names(df_filtered), collapse = ", "))
  return(df_filtered)
}


#' Rename CBS neighborhood columns to English
#'
#' @param df A data.frame from CBS WijkenEnBuurten table
#' @return A list containing a data.frame with English column names and a data.frame mapping old to new column names for replication and transparency
#' @examples
#' df_en <- rename_cbs_columns(df)
rename_cbs_columns <- function(df) {
  rename_map <- c(
    "RegionType" = "WijkenEnBuurten",
    "municipality" = "Gemeentenaam_1",
    "RegionLevel" = "SoortRegio_2",
    "NeighbCode" = "Codering_3",
    "MunicipalityChange" = "IndelingswijzigingGemeenteWijkBuurt_4",
    "PopulationTotal" = "AantalInwoners_5",
    "male" = "Mannen_6",
    "female" = "Vrouwen_7",
    "age0_15" = "k_0Tot15Jaar_8",
    "age15_25" = "k_15Tot25Jaar_9",
    "age25_45" = "k_25Tot45Jaar_10",
    "age45_65" = "k_45Tot65Jaar_11",
    "age65plus" = "k_65JaarOfOuder_12",
    "Single" = "Ongehuwd_13",
    "Married" = "Gehuwd_14",
    "Divorced" = "Gescheiden_15",
    "Widowed" = "Verweduwd_16",
    "Born_Netherlands" = "Nederland_17",
    "Born_EuropeExclNL" = "EuropaExclusiefNederland_18",
    "Born_OutsideEurope" = "BuitenEuropa_19",
    "Nationality_Netherlands" = "Nederland_20",
    "Nationality_EuropeExclNL" = "EuropaExclusiefNederland_21",
    "Nationality_OutsideEurope" = "BuitenEuropa_22",
    "Births_Total" = "GeborteTotaal_25",
    "Births_Relative" = "GeboorteRelatief_26",
    "Deaths_Total" = "SterfteTotaal_27",
    "Deaths_Relative" = "SterfteRelatief_28",
    "Households_Total" = "HuishoudensTotaal_29",
    "Households_OnePerson" = "Eenpersoonshuishoudens_30",
    "Households_NoChildren" = "HuishoudensZonderKinderen_31",
    "Households_WithChildren" = "HuishoudensMetKinderen_32",
    "HouseholdSize_Avg" = "GemiddeldeHuishoudensgrootte_33",
    "PopulationDensity" = "Bevolkingsdichtheid_34",
    "HousingStock" = "Woningvoorraad_35",
    "NewHousing" = "NieuwbouwWoningen_36",
    "NonHousingStock" = "NietWoningvoorraad_37",
    "NewNonHousing" = "NieuwbouwNietWoningen_38",
    "AvgPropertyValue" = "GemiddeldeWOZWaardeVanWoningen_39",
    "Pct_SingleFamily" = "PercentageEengezinswoning_40",
    "Pct_TerracedHouse" = "PercentageTussenwoningEengezins_41",
    "Pct_CornerHouse" = "PercentageHoekwoningEengezins_42",
    "Pct_SemiDetached" = "PercentageTweeOnderEenKapWoningEe_43",
    "Pct_Detached" = "PercentageVrijstaandeWoningEengezins_44",
    "Pct_Apartment" = "PercentageMeergezinswoning_45",
    "VacantHousing" = "OnbewoondeWoningen_46",
    "OwnerOccupied" = "Koopwoningen_47",
    "Rented_Total" = "HuurwoningenTotaal_48",
    "Rented_HousingCorp" = "InBezitWoningcorporatie_49",
    "Rented_Other" = "InBezitOverigeVerhuurders_50",
    "Built_10PlusYears" = "BouwjaarMeerDanTienJaarGeleden_51",
    "Built_Last10Years" = "BouwjaarAfgelopenTienJaar_52",
    "ElectricityUsage_Avg" = "GemiddeldeElektriciteitsleveringTotaal_53",
    "ElectricityReturn_Avg" = "GemiddeldeElektriciteitsteruglevering_54",
    "GasUsage_Avg" = "GemiddeldAardgasverbruikTotaal_55",
    "Pct_DistrictHeating" = "PercentageWoningenMetStadsverwarming_56",
    "GasFreeHomes" = "AardgasvrijeWoningen_57",
    "GasHomes" = "Aardgaswoningen_58",
    "HomesWithSolar" = "WoningenMetZonnestroom_59",
    "ElectricHeatedHomes" = "WoningenHoofdzElektrischVerwarmd_60",
    "EV_Chargers" = "AantalPubliekeLaadpalen_61",
    "Students_Primary" = "LeerlingenPo_62",
    "Students_Secondary" = "LeerlingenVoInclVavo_63",
    "Students_MBO" = "StudentenMboExclExtranei_64",
    "Students_HBO" = "StudentenHbo_65",
    "Students_WO" = "StudentenWo_66",
    "Education_Primary_VMBO_MBO1" = "BasisonderwijsVmboMbo1_67",
    "Education_HAVO_VWO_MBO2_4" = "HavoVwoMbo24_68",
    "Education_HBO_WO" = "HboWo_69",
    "LaborForce_Employed" = "WerkzameBeroepsbevolking_70",
    "LaborParticipation_Net" = "Nettoarbeidsparticipatie_71",
    "Pct_Employees" = "PercentageWerknemers_72",
    "Employees_FixedContract" = "WerknemersMetVasteArbeidsr_73",
    "Employees_FlexibleContract" = "WerknemersMetFlexibeleArbe_74",
    "Pct_SelfEmployed" = "PercentageZelfstandigen_75",
    "IncomeRecipients_Total" = "AantalInkomensontvangers_76",
    "Income_AvgPerRecipient" = "GemiddeldInkomenPerInkomensontvanger_77",
    "Income_AvgPerCapita" = "GemiddeldInkomenPerInwoner_78",
    "Lowest40Pct_IncomePersons" = "k_40PersonenMetLaagsteInkomen_79",
    "Highest20Pct_IncomePersons" = "k_20PersonenMetHoogsteInkomen_80",
    "Persons_InPoverty" = "PersonenInArmoede_81",
    "Persons_UpTo25AbovePoverty" = "PersonenTot25BovenArmoedegrens_82",
    "Income_StandardizedAvg" = "GemGestandaardiseerdInkomen_83",
    "Lowest40Pct_IncomeHouseholds" = "k_40HuishoudensMetLaagsteInkomen_84",
    "Highest20Pct_IncomeHouseholds" = "k_20HuishoudensMetHoogsteInkomen_85",
    "MedianWealth_Households" = "MediaanVermogenVanParticuliereHuish_86",
    "Persons_SocialAssistance" = "PersonenPerSoortUitkeringBijstand_87",
    "Persons_DisabilityBenefit" = "PersonenPerSoortUitkeringAO_88",
    "Persons_UnemploymentBenefit" = "PersonenPerSoortUitkeringWW_89",
    "Persons_PensionAOW" = "PersonenPerSoortUitkeringAOW_90",
    "Youth_ReceivingCare" = "JongerenMetJeugdzorgInNatura_91",
    "Pct_YouthWithCare" = "PercentageJongerenMetJeugdzorg_92",
    "WMO_Clients" = "WmoClienten_93",
    "Pct_WMO_Clients" = "WmoClientenRelatief_94",
    "Companies_Total" = "BedrijfsvestigingenTotaal_95",
    "Companies_Agriculture_Forestry_Fishing" = "ALandbouwBosbouwEnVisserij_96",
    "Companies_Industry_Energy" = "BFNijverheidEnEnergie_97",
    "Companies_Trade_Hospitality" = "GIHandelEnHoreca_98",
    "Companies_Transport_InfoComm" = "HJVervoerInformatieEnCommunicatie_99",
    "Companies_Finance_RealEstate" = "KLFinancieleDienstenOnroerendGoed_100",
    "Companies_BusinessServices" = "MNZakelijkeDienstverlening_101",
    "Companies_PublicEducation_Healthcare" = "OQOverheidOnderwijsEnZorg_102",
    "Companies_Culture_Recreation_Other" = "RUCultuurRecreatieOverigeDiensten_103",
    "Cars_Total" = "PersonenautoSTotaal_104",
    "Cars_Petrol" = "PersonenautoSBrandstofBenzine_105",
    "Cars_OtherFuel" = "PersonenautoSOverigeBrandstof_106",
    "Cars_PerHousehold" = "PersonenautoSPerHuishouden_107",
    "Cars_PerArea" = "PersonenautoSNaarOppervlakte_108",
    "Motorcycles" = "Motorfietsen_109",
    "Distance_GP" = "AfstandTotHuisartsenpraktijk_110",
    "Distance_LargeSupermarket" = "AfstandTotGroteSupermarkt_111",
    "Distance_Daycare" = "AfstandTotKinderdagverblijf_112",
    "Distance_School" = "AfstandTotSchool_113",
    "Schools_Within3km" = "ScholenBinnen3Km_114",
    "Area_Total" = "OppervlakteTotaal_115",
    "Area_Land" = "OppervlakteLand_116",
    "Area_Water" = "OppervlakteWater_117",
    "MostCommonPostalCode" = "MeestVoorkomendePostcode_118",
    "CoveragePct" = "Dekkingspercentage_119",
    "UrbanizationLevel" = "MateVanStedelijkheid_120",
    "AddressDensity" = "Omgevingsadressendichtheid_121"
  )
  
  # Only rename columns that exist in df
  rename_map <- rename_map[rename_map %in% names(df)]

  # make a table of old and new names
  old_new_names <- data.frame(
    Old_Name = names(df),
    New_Name = names(df),
    stringsAsFactors = FALSE
  )
  
  df <- df %>% rename(!!!rename_map)
  old_new_names$New_Name = names(df)
  message("Renamed columns to English where columns existed in the dataframe. New column names:")
  message(paste(names(df), collapse = ", "))

  return(list(df = df, old_new_names = old_new_names))
}

#' Clean and translate CBS population data
#'
#' @param df A data.frame from CBS population table (e.g., from cbs_get_data)
#' @return A list containing a cleaned data.frame with English column names and translations, and a mapping table
#' @examples
#' pop_clean <- clean_cbs_population_data(pop_totals_regio)
clean_cbs_population_data <- function(df) {
  
  # Rename columns to English
  column_rename_map <- c(
    "ID" = "ID",
    "municipality" = "RegioS",
    "year" = "Perioden",
    "age" = "Leeftijd",
    "sex" = "Geslacht",
    "maritalStatus" = "BurgerlijkeStaat",
    "migrationBackground" = "Migratieachtergrond",
    "population" = "BevolkingOp1Januari_1"
  )
  
  # Only rename columns that exist in df
  column_rename_map <- column_rename_map[column_rename_map %in% names(df)]
  df <- df %>% rename(!!!column_rename_map)

  # strip empty space in all columns
  df[] <- lapply(df, function(x) if(is.character(x)) trimws(x) else x)
  
  # Strip whitespace from all character columns first (CBS codes often have trailing spaces)
  char_cols <- sapply(df, is.character)
  df[char_cols] <- lapply(df[char_cols], trimws)
  
  # Translate age codes (Leeftijd) to English - individual
  if ("age" %in% names(df)) {
    age_translation <- c(
      "10000" = "Total",
      "10010" = "0", "10100" = "1", "10200" = "2", "10300" = "3", 
      "10400" = "4", "10500" = "5", "10600" = "6", "10700" = "7",
      "10800" = "8", "10900" = "9", "11000" = "10", "11100" = "11",
      "11200" = "12", "11300" = "13", "11400" = "14", "11500" = "15",
      "11600" = "16", "11700" = "17", "11800" = "18", "11900" = "19",
      "12000" = "20", "12100" = "21", "12200" = "22", "12300" = "23",
      "12400" = "24", "12500" = "25", "12600" = "26", "12700" = "27",
      "12800" = "28", "12900" = "29", "13000" = "30", "13100" = "31",
      "13200" = "32", "13300" = "33", "13400" = "34", "13500" = "35",
      "13600" = "36", "13700" = "37", "13800" = "38", "13900" = "39",
      "14000" = "40", "14100" = "41", "14200" = "42", "14300" = "43",
      "14400" = "44", "14500" = "45", "14600" = "46", "14700" = "47",
      "14800" = "48", "14900" = "49", "15000" = "50", "15100" = "51",
      "15200" = "52", "15300" = "53", "15400" = "54", "15500" = "55",
      "15600" = "56", "15700" = "57", "15800" = "58", "15900" = "59",
      "16000" = "60", "16100" = "61", "16200" = "62", "16300" = "63",
      "16400" = "64", "16500" = "65", "16600" = "66", "16700" = "67",
      "16800" = "68", "16900" = "69", "17000" = "70", "17100" = "71",
      "17200" = "72", "17300" = "73", "17400" = "74", "17500" = "75",
      "17600" = "76", "17700" = "77", "17800" = "78", "17900" = "79",
      "18000" = "80", "18100" = "81", "18200" = "82", "18300" = "83",
      "18400" = "84", "18500" = "85", "18600" = "86", "18700" = "87",
      "18800" = "88", "18900" = "89", "19000" = "90", "19100" = "91",
      "19200" = "92", "19300" = "93", "19400" = "94", "19500" = "95",
      "19600" = "96", "19700" = "97", "19800" = "98", "19900" = "99",
      "19901" = "100", "19902" = "101", "19903" = "102", "19904" = "103",
      "19905" = "104", "22000" = "95 or older", "22300" = "105 or older"
    )
    
    df$age <- ifelse(df$age %in% names(age_translation),
                           age_translation[df$age],
                           df$age)
  }
  
  # Translate Gender codes (Geslacht) to English
  if ("sex" %in% names(df)) {
    gender_translation <- c(
      "T001038" = "total",
      "3000" = "male",
      "4000" = "female"
    )
    
    df$sex <- ifelse(df$sex %in% names(gender_translation),
                        gender_translation[df$sex],
                        df$sex)
  }
  
  # Translate Marital Status codes (BurgerlijkeStaat) to English
  if ("maritalStatus" %in% names(df)) {
    marital_translation <- c(
      "T001019" = "total",
      "1010" = "never married",
      "1020" = "married",
      "1050" = "widowed",
      "1080" = "divorced"
    )
    
    df$maritalStatus <- ifelse(df$maritalStatus %in% names(marital_translation),
                                 marital_translation[df$maritalStatus],
                                 df$maritalStatus)
  }
  
  # Create translation mapping table
  translation_map <- data.frame(
    Dutch_Column = c("RegioS", "Perioden", "Leeftijd", "Geslacht", "BurgerlijkeStaat", "BevolkingOp1Januari_1"),
    English_Column = c("municipality", "year", "age", "sex", "maritalStatus", "population"),
    stringsAsFactors = FALSE
  )
  
  message("Cleaned and translated CBS population data.")
  message("Columns in cleaned data: ", paste(names(df), collapse = ", "))
  
  return(list(df = df, translation_map = translation_map))
}



#' Download CBS Postcode4 Shapefile from PDOK
#'
#' This function downloads the postcode4 statistical data from CBS via WFS service for a specified year
#'
#' @param year Year of the data to download (2018-2024)
#' @param output_dir Directory where the shapefile will be saved (default: "SyntheticPopulation/Data")
#' @param save_to_file Whether to save the data to a shapefile (default: TRUE)
#' @param geometry_only Whether to keep only postcode and geometry columns (default: FALSE)
#' @return sf object containing the postcode4 data
#' @examples
#' postcode4_2024 <- download_cbs_postcode4(2024)
#' postcode4_2023 <- download_cbs_postcode4(2023, output_dir = "Data/CBS")
#' postcode4_shapes <- download_cbs_postcode4(2024, save_to_file = FALSE, geometry_only = TRUE)
download_cbs_postcode4 <- function(year = 2024, output_dir = "SyntheticPopulation/Data", save_to_file = TRUE, geometry_only = FALSE) {
  
  # Validate year
  if (!year %in% 2015:2024) {
    message("currently available years: 2015-2024")
  }
  
  # Construct WFS URL for the specified year
  wfs_url <- paste0("WFS:https://service.pdok.nl/cbs/postcode4/", year, "/wfs/v1_0")

  message("Fetching WFS capabilities for year ", year, "...")
  
  # Download the postcode4 data
  message("Downloading postcode4 data for ", year, " (this may take a few minutes)...")
  
  postcode4 <- st_read(
    dsn = wfs_url,
    layer = "postcode4:postcode4",
    quiet = FALSE
  )
  
  # If geometry_only is TRUE, keep only postcode identifier and geometry
  if (geometry_only) {
    postcode_col <- grep("postcode", names(postcode4), value = TRUE)[1]
    geometry_col <- attr(postcode4, "sf_column")
    if (is.na(postcode_col)) {
      message("Could not find postcode identifier column in the data.")
    }
    else {
      names(postcode4)[names(postcode4) == postcode_col] <- "postcode"  
      names(postcode4)[names(postcode4) == geometry_col] <- "geometry"
      st_geometry(postcode4) <- "geometry"
      postcode4 <- postcode4[, c("postcode", "geometry")]
      message("Keeping only postcode identifier and geometry columns")
    }
  }
  
  if (save_to_file) {
    # Create output directory if it doesn't exist
    if (!dir.exists(output_dir)) {
      dir.create(output_dir, recursive = TRUE)
      message("Created directory: ", output_dir)
    }
    
    # Save as shapefile
    filename_suffix <- if(geometry_only) "_shapes" else ""
    output_file <- file.path(output_dir, paste0("CBS_Postcode4_", year, filename_suffix, ".shp"))
    st_write(postcode4, output_file, delete_dsn = TRUE)
    
    message("Shapefile saved to: ", output_file)
  }
  
  message("Downloaded ", nrow(postcode4), " postcode4 areas for year ", year)
  message("Available columns: ", paste(names(postcode4), collapse = ", "))
  
  return(postcode4)
}


#' Download CBS Wijken en Buurten (Neighborhoods and Districts) from PDOK
#'
#' This function downloads the CBS Wijken en Buurten data via WFS service for a specified year.
#' The dataset contains geometries for all municipalities, districts (wijken), and neighborhoods (buurten) in the Netherlands.
#'
#' @param year Year of the data to download (2022-2024)
#' @param spatial_level Spatial level to download: "gemeente" (municipality), "wijk" (district), "buurt" (neighborhood), or "all" (default: "all")
#' @param output_dir Directory where the shapefile will be saved (default: "SyntheticPopulation/Data")
#' @param save_to_file Whether to save the data to a shapefile (default: TRUE)
#' @param geometry_only Whether to keep only identifier and geometry columns (default: FALSE)
#' @return sf object containing the wijken en buurten data
#' @examples
#' # Download all levels for 2024
#' wb_2024 <- download_cbs_wijken_buurten(2024)
#' 
#' # Download only neighborhoods for 2023
#' buurten_2023 <- download_cbs_wijken_buurten(2023, spatial_level = "buurt")
#' 
#' # Download only geometries without saving
#' wijken_shapes <- download_cbs_wijken_buurten(2024, spatial_level = "wijk", save_to_file = FALSE, geometry_only = TRUE)
download_cbs_wijken_buurten <- function(year = 2024, 
                                        spatial_level = c("all", "gemeente", "wijk", "buurt"), 
                                        output_dir = "SyntheticPopulation/Data", 
                                        save_to_file = TRUE, 
                                        geometry_only = FALSE) {
  
  # Validate year
  if (!year %in% 2012:2024) {
    message(" currently available years: 2012-2024")
  }
  
  # Match spatial level argument
  spatial_level <- match.arg(spatial_level)
  
  # Construct WFS URL for the specified year
  wfs_url <- paste0("WFS:https://service.pdok.nl/cbs/wijkenbuurten/", year, "/wfs/v1_0")
  
  message("Fetching WFS capabilities for year ", year, "...")
  
  # Map spatial level to layer names
  layer_map <- list(
    "gemeente" = "gemeenten",
    "wijk" = "wijken",
    "buurt" = "buurten"
  )
  
  # Download based on spatial level
  if (spatial_level == "all") {
    message("Downloading all spatial levels (gemeente, wijk, buurt) for ", year, " (this may take several minutes)...")
    
    result_list <- list()
    for (level in c("gemeente", "wijk", "buurt")) {
      layer_name <- paste0("wijkenbuurten:", layer_map[[level]])
      message("  Downloading ", level, " layer...")
      
      result_list[[level]] <- st_read(
        dsn = wfs_url,
        layer = layer_name,
        quiet = FALSE
      )
      
      if (geometry_only) {
        # Keep only key identifier columns and geometry
        id_cols <- c("buurtcode", "wijkcode", "gemeentecode")
        # Only keep columns that exist in the data
        id_cols <- id_cols[id_cols %in% names(result_list[[level]])]
        if (length(id_cols) > 0) {
          result_list[[level]] <- result_list[[level]][, id_cols]
          message("    Keeping only ", paste(id_cols, collapse = ", "), " and geometry for ", level)
        }
      }
    }
    
    wb_data <- result_list
    total_features <- sum(sapply(result_list, nrow))
    
  } else {
    # Download single spatial level
    layer_name <- paste0("wijkenbuurten:", layer_map[[spatial_level]])
    message("Downloading ", spatial_level, " data for ", year, " (this may take a few minutes)...")
    
    wb_data <- st_read(
      dsn = wfs_url,
      layer = layer_name,
      quiet = FALSE
    )
    
    if (geometry_only) {
      # Keep only key identifier columns and geometry
      id_cols <- c("buurtcode", "wijkcode", "gemeentecode", "gemeentenaam", "wijknaam", "buurtnaam")
      # Only keep columns that exist in the data
      id_cols <- id_cols[id_cols %in% names(wb_data)]
      if (length(id_cols) > 0) {
        wb_data <- wb_data[, id_cols]
        message("Keeping only ", paste(id_cols, collapse = ", "), " and geometry columns")
      }
    }
    
    total_features <- nrow(wb_data)
  }
  
  if (save_to_file) {
    # Create output directory if it doesn't exist
    if (!dir.exists(output_dir)) {
      dir.create(output_dir, recursive = TRUE)
      message("Created directory: ", output_dir)
    }
    
    # Save as shapefile
    filename_suffix <- if(geometry_only) "_shapes" else ""
    
    if (spatial_level == "all") {
      # Save each level separately
      for (level in names(wb_data)) {
        output_file <- file.path(output_dir, paste0("CBS_", level, "_", year, filename_suffix, ".shp"))
        st_write(wb_data[[level]], output_file, delete_dsn = TRUE)
        message("Shapefile saved to: ", output_file)
      }
    } else {
      output_file <- file.path(output_dir, paste0("CBS_", spatial_level, "_", year, filename_suffix, ".shp"))
      st_write(wb_data, output_file, delete_dsn = TRUE)
      message("Shapefile saved to: ", output_file)
    }
  }
  
  message("Downloaded ", total_features, " features for year ", year)
  
  if (spatial_level != "all") {
    message("Available columns: ", paste(names(wb_data), collapse = ", "))
  }
  
  return(wb_data)
}
