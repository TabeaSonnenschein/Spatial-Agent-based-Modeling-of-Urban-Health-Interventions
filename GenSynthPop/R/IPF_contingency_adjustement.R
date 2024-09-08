library(mipfp)

ipf_fit_contingency_table <- function(group_name) {
  # Check if margins are provided
  if (is.null(self$margins) || length(self$margins) == 0) {
    mask <- _get_group_mask(self$df_contingency, group_name, self$group_by)
    return(self$df_contingency[mask, ])
  }
  
  aggregates <- list()
  # Iterate over each margin and dimension
  for (i in seq_along(self$margins)) {
    df <- self$margins[[i]]
    dimension <- self$margins_names[[i]]
    mask <- _get_group_mask(df, group_name, self$group_by)
    df_masked <- df[mask, ]
    count <- as.numeric(df_masked[[dimension]])
    names(count) <- df_masked[["count"]]
    aggregates[[i]] <- count
  }
  
  df_to_fit <- self$df_contingency
  ipf <- ipfn(df_to_fit, aggregates, self$margins_names, weight_col = "count")
  df_fitted <- ipf$iteration()
  
  return(df_fitted)
}


# Helper function to create group mask (analogous to _get_group_mask in Python)
get_group_mask <- function(df, group_name, group_by) {
  mask <- rep(TRUE, nrow(df))
  for (i in seq_along(group_by)) {
    mask <- mask & (df[[group_by[i]]] == group_name[i])
  }
  return(mask)
}

# Main function translated from Python to R
ipf_fit_contingency_table <- function(df_contingency, margins, margins_names, group_by, group_name) {
  # Check if margins are provided
  if (is.null(margins) || length(margins) == 0) {
    # Apply mask to contingency table
    mask <- get_group_mask(df_contingency, group_name, group_by)
    return(df_contingency[mask, ])
  }

  # Create list of aggregates
  aggregates <- list()
  for (i in seq_along(margins)) {
    df <- margins[[i]]
    dimension <- margins_names[[i]]
    mask <- get_group_mask(df, group_name, group_by)
    df_masked <- df[mask, ]
    count <- as.numeric(df_masked[["count"]])
    names(count) <- df_masked[[dimension]]
    aggregates[[i]] <- count
  }

  # Set up the IPFP
  df_to_fit <- df_contingency
  observed <- df_to_fit[["count"]]

  # Define target margins for each dimension
  target_margins <- aggregates

  # Perform IPFP using mipfp
  ipf_result <- Ipfp(
    seed = observed,
    target.list = lapply(margins_names, function(d) as.numeric(df_to_fit[[d]])),
    target.data = target_margins
  )

  # Retrieve fitted counts
  fitted_counts <- ipf_result$x.hat

  # Add fitted counts back to the data frame
  df_fitted <- df_to_fit
  df_fitted[["fitted_count"]] <- fitted_counts

  return(df_fitted)
}

# Example usage (assuming you have appropriate data):
# df_contingency <- ...  # Data frame for contingency table
# margins <- ...         # List of margin data frames
# margins_names <- ...   # Names of the margins/dimensions
# group_by <- ...        # Group by dimensions
# group_name <- ...      # Group name tuple
# fitted_table <- ipf_fit_contingency_table(df_contingency, margins, margins_names, group_by, group_name)


library(mipfp)
library(dplyr)
library(tidyr)

# Helper functions

get_group_mask <- function(df, group_name, group_by) {
  mask <- rep(TRUE, nrow(df))
  for (i in seq_along(group_by)) {
    if (group_by[i] %in% names(df)) {
      mask <- mask & (df[[group_by[i]]] == group_name[i])
    }
  }
  return(mask)
}

calculate_group_counts <- function(df_fractions, n_agents_total) {
  counts <- round(df_fractions * n_agents_total)
  
  while ((group_total <- sum(counts)) != n_agents_total) {
    differences <- t(t(counts / n_agents_total) - df_fractions)
    correction_target <- if (group_total < n_agents_total) which.min(differences) else which.max(differences)
    
    if (group_total < n_agents_total) {
      counts[correction_target] <- counts[correction_target] + 1
    } else {
      counts[correction_target] <- counts[correction_target] - 1
    }
  }
  
  return(counts)
}

get_agent_values_from_fractions <- function(group_fractions, group_agent_count) {
  group_counts <- calculate_group_counts(group_fractions, group_agent_count)
  group_values <- vector()
  
  for (attr_value in names(group_counts)) {
    if (!is.na(group_counts[[attr_value]])) {
      group_values <- c(group_values, rep(attr_value, group_counts[[attr_value]]))
    }
  }
  
  return(group_values)
}

# Main class

ConditionalAttributeAdder <- setRefClass(
  "ConditionalAttributeAdder",
  fields = list(
    df = "data.frame",
    df_contingency = "data.frame",
    target_attribute = "character",
    group_by = "character",
    margins = "list",
    margins_names = "list",
    margins_group = "character"
  ),
  methods = list(
    initialize = function(df_synthetic_population, df_contingency, target_attribute, group_by = character()) {
      df <<- df_synthetic_population
      df_contingency <<- df_contingency
      target_attribute <<- target_attribute
      group_by <<- group_by
      margins <<- list()
      margins_names <<- list()
      margins_group <<- group_by
    },
    
    add_margins = function(margins, margins_names) {
      if (is.null(margins) || is.null(margins_names)) {
        stop("When either margins_names or margins_data_frames argument is provided, the other is required as well")
      }
      if (length(margins) != length(margins_names)) {
        stop("margins_data_frames and margins_names have to be the same length")
      }
      
      margins <<- margins
      margins_names <<- margins_names
      margins_group <<- unique(unlist(lapply(margins_names, function(m_list) {
        m_list[sapply(m_list, function(m) m %in% names(df))]
      })))
    },
    
    run = function() {
      df[[target_attribute]] <<- NA
      
      for (group_name in unique(df[group_by])) {
        group_name <- as.character(group_name)
        group <- df[get_group_mask(df, group_name, group_by), ]
        
        df_contingency_group <- .self$ipf_fit_contingency_table(group_name)
        group_fractions <- .self$get_group_fractions(df_contingency_group)
        
        if (length(margins) == 0) {
          group_values <- get_agent_values_from_fractions(group_fractions, nrow(group))
          mask <- get_group_mask(df, group_name, group_by)
          df[mask, target_attribute] <<- group_values
        } else {
          sub_group_by <- setdiff(margins_group, c(group_by, target_attribute))
          for (sub_group_name in unique(df[sub_group_by])) {
            sub_group_name <- as.character(sub_group_name)
            mask <- get_group_mask(df, group_name, group_by)
            mask <- mask & get_group_mask(df, sub_group_name, sub_group_by)
            
            if (!any(mask)) {
              next
            }
            
            group_fractions_df <- as.data.frame(group_fractions)
            other_mask <- get_group_mask(group_fractions_df, sub_group_name, sub_group_by)
            sub_group_fractions <- group_fractions_df[other_mask, target_attribute]
            
            if (any(duplicated(names(sub_group_fractions)))) {
              cat(sprintf("Attribute %s is not unique. Grouping.\n", names(sub_group_fractions)))
              sub_group_fractions <- tapply(sub_group_fractions, names(sub_group_fractions), sum)
            }
            
            group_values <- get_agent_values_from_fractions(sub_group_fractions, sum(mask))
            df[mask, target_attribute] <<- group_values
          }
        }
      }
      
      .self$verify_target_attribute()
      
      return(df)
    },
    
    ipf_fit_contingency_table = function(group_name) {
      if (length(margins) == 0) {
        mask <- get_group_mask(df_contingency, group_name, group_by)
        return(df_contingency[mask, ])
      }
      
      aggregates <- list()
      for (i in seq_along(margins)) {
        df <- margins[[i]]
        dimension <- margins_names[[i]]
        mask <- get_group_mask(df, group_name, group_by)
        df_masked <- df[mask, ]
        count <- as.numeric(df_masked[["count"]])
        names(count) <- df_masked[[dimension]]
        aggregates[[i]] <- count
      }
      
      df_to_fit <- df_contingency
      observed <- df_to_fit[["count"]]
      
      ipf_result <- Ipfp(
        seed = observed,
        target.list = lapply(margins_names, function(d) as.numeric(df_to_fit[[d]])),
        target.data = aggregates
      )
      
      fitted_counts <- ipf_result$x.hat
      df_fitted <- df_to_fit
      df_fitted[["fitted_count"]] <- fitted_counts
      
      return(df_fitted)
    },
    
    get_group_fractions = function(df) {
      df_fractions <- .self$calculate_fractions(df)
      index <- unique(c(target_attribute, unlist(margins_names)))
      df_fractions <- df_fractions %>% select(all_of(index)) %>% pull(fraction)
      return(df_fractions)
    },
    
    calculate_fractions = function(df) {
      df_fractions <- df
      group_by_columns <- intersect(names(df), setdiff(c(group_by, margins_group), target_attribute))
      
      df_fractions <- df %>%
        group_by(across(all_of(group_by_columns))) %>%
        mutate(fraction = ifelse(sum(count) != 0, count / sum(count), 0)) %>%
        ungroup()
      
      return(df_fractions)
    },
    
    verify_target_attribute = function() {
      if (any(is.na(df[[target_attribute]]))) {
        warning(sprintf(
          "There was an issue conditionally assigning the %s value that caused not all agents having been assigned a value. Please refrain from using the result",
          target_attribute
        ))
      }
      
      group_by_check <- unique(c(margins_group, target_attribute))
      merged_df <- merge(df, df_contingency, by = group_by_check, all.x = TRUE)
      z_squared_score <- chisq.test(merged_df$count.x, merged_df$count.y)
      
      if (z_squared_score$p.value < 0.05) {
        warning(sprintf(
          "The attribute %s was added, but its distribution in the synthetic population does not statistically match the contingency table this attribute was added from. P-value was %.4f. Caution advised when using this fitted distribution",
          target_attribute, z_squared_score$p.value
        ))
      }
    }
  )
)

# Example usage:
# df_synthetic_population <- data.frame(...)  # Data frame for synthetic population
# df_contingency <- data.frame(...)           # Contingency table
# target_attribute <- "your_target_attribute" # Target attribute to add
# group_by <- c("group1", "group2")           # Grouping attributes
# margins <- list(...)                        # Margins data frames
# margins_names <- list(...)                  # Margins names

# adder <- ConditionalAttributeAdder$new(df_synthetic_population, df_contingency, target_attribute, group_by)
# adder$add_margins(margins, margins_names)
# fitted_df <- adder$run()
