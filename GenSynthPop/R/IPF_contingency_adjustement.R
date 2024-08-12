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