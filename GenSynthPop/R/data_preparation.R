####### Preparing stratified datasets
# crosstabular stratified format to single sided variable combination format

# nrow_var = number of rows corresponding to variable names 
# ncol_var = number of columns corresponding to variable names 


crosstabular_stratfieddf_to_singleside_df =  function(df, nrow_var, ncol_var, row_var_names, col_var_names){
  len_rowvar_combi = ncol(df) - ncol_var # how many classes of the row variables are there
  len_colvar_combi = nrow(df) - nrow_var # how many classes of the column variables are there
  df_len = len_rowvar_combi * len_colvar_combi
  df_colvar = as.data.frame(df[(nrow_var+1):nrow(df),1:ncol_var])
  colnames(df_colvar) = col_var_names
  df_new = df_colvar
  for(i in 1:(len_rowvar_combi-1)){
    df_new = rbind(df_new, df_colvar)
  }
  for(x in row_var_names){
    df_new[,c(x)] = ""
  }
  df_new$counts = NA
  print(nrow(df_new))
  for(i in 1:len_rowvar_combi){
    # print(i)
    # print(nrow(df_new))
    for(x in (1:len_colvar_combi)){
      df_new[((i-1)*len_colvar_combi)+x,c(row_var_names)]=df[1:nrow_var,i+ncol_var]
    }
    df_new[((i-1)*len_colvar_combi)+1:(i*len_colvar_combi),c("counts")] = df[(1+nrow_var):(len_colvar_combi+nrow_var),i+ncol_var]
  }
  return(df_new[1:df_len,])
}

# this function restructures the dataframe so that the classes of one column/variable are seperate columns
restructure_one_var_marginal = function(df, variable){
  classes = unique(df[,c(variable)])
  restColumns = colnames(df)[(colnames(df) != variable) & (colnames(df) != "counts")]
  df_new = unique(df[, c(restColumns)])
  for(x in classes){
    df_new[, c(x)] = as.numeric(df[df[,c(variable)] == x, "counts"])
  }
  df_new[,c("total")] = rowSums(df_new[,c(classes)])
  return(df_new)
}


## this function creates a stratified probability table from single attribute propensities

create_stratified_prob_table = function(nested_cond_attr_list, column_names, orig_df, strat_var, var_for_pred, total_population){
  ncondVar = length(column_names)
  attr_length = c()
  for(i in 1:ncondVar){
    attr_length = append(attr_length, length(nested_cond_attr_list[[i]]))
  }
  new_strat_df = as.data.frame(matrix(nrow = prod(attr_length), ncol = (ncondVar + length(var_for_pred))))
  for(i in 1:ncondVar){
    if(i == ncondVar){
      new_strat_df[,i] = rep(nested_cond_attr_list[[i]], times =  (prod(attr_length)/attr_length[i]))
    }
    else{
      var_comb = c()
      for(n in 1:attr_length[i]){
        var_comb = append(var_comb, rep(nested_cond_attr_list[[i]][n], times = prod(attr_length[(i+1):ncondVar])))
      }
      new_strat_df[,i] = rep(var_comb, times = prod(attr_length)/prod(attr_length[(i):ncondVar]))
    }
    
  }
  colnames(new_strat_df) = c(column_names, paste("prop_",var_for_pred, sep = ""))
  if(missing(total_population)){
    for(i in 1:nrow(new_strat_df)){
      for(n in 1:length(var_for_pred)){
        new_strat_df[i,n+ncondVar] = sum(orig_df[which(orig_df[,c(strat_var)] %in% c(new_strat_df[i,1:ncondVar])),c(var_for_pred[n])])/ncondVar
      }
    }
  }
  else{
    for(i in 1:length(var_for_pred)){
      orig_df[,c(paste("prop_",var_for_pred[i], sep = ""))] = orig_df[,c(var_for_pred[i])]/orig_df[, c(total_population)]
    }
    for(i in 1:nrow(new_strat_df)){
      for(n in 1:length(var_for_pred)){
        new_strat_df[i,n+ncondVar] = sum(orig_df[which(orig_df[,c(strat_var)] %in% c(new_strat_df[i,1:ncondVar])),c(paste("prop_",var_for_pred[n], sep = ""))])/ncondVar
      }
    }
  }
  return(new_strat_df)
}


