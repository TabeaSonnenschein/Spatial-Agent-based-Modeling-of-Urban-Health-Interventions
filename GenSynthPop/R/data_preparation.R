####### Preparing stratified datasets

#' @title Crosstabular Stratified Table to Single Sided Variable Combination - Counts Table
#' @description In order to facilitate the data preparation, this function can transform any stratified dataset structure in terms of number of row variables and column variable combinations into a dataset structure of all variable combinations as columns in the left and a single "counts" column on the right.
#' @param df The stratified dataset that you want to process
#' @param nrow_var number of rows corresponding to variable names
#' @param ncol_var number of columns corresponding to variable names
#' @param row_var_names The variable names that you want to use to describe the variables in the rows. This will be used as variable column name for the output dataset.The order needs to be from top row to lower row variables.
#' @param col_var_names The variable names that you want to use to describe the variables in the columns. This will be used as variable column name for the output dataset. The order needs to be from left column to right column variables.
#' @return Returns a processed stratefied dataframe with all variables as columns on the left. There will be all unique variable combinations. Additionally there will be the counts variable that shows how many people there are for the respective variable combination.
#' @details
#' #Example Tables (random numbers)
#' ## Turns a crosstabular stratified dataframe, such as this:
#' ### *note that it can have any number of row variables (here 2) or column variables (here 1)
#' | age_groups | male | male | female | female | non-binary | non-binary |
#' |:----:|:----:|:----:|:----:|:----:|:----:|:----:|
#' |  |employed | unemployed | employed | unemployed | employed | unemployed |
#' | A1 | 25 | 133 | 175 | 389 | 196 | 203 |
#' | A2 | 132 | 323 | 275 | 206 | 248 | 270 |
#' | A3 | 122 | 360 | 394 | 25 | 137 | 34 |
#'
#' ## Into a single side stratified dataframe such as this:
#' |age_group |sex | employ_status | counts |
#' |:----:|:-----:|:----:|:---:|
#' | A1 | male | employed | 25 |
#' | A2 | male | employed | 132 |
#' | A3 | male | employed | 122 |
#' | A1 | male | unemployed | 133 |
#' | A2 | male | unemployed | 323 |
#' | A3 | male | unemployed | 360 |
#' | A1 | female | employed | 175 |
#' | A2 | female | employed | 275 |
#' | A3 | female | employed | 394 |
#' | A1 | female | unemployed | 389 |
#' | A2 | female | unemployed | 206 |
#' | A3 | female | unemployed |  25 |
#' | A1 | non-binary | employed | 196 |
#' | A2 | non-binary | employed | 248 |
#' | A3 | non-binary | employed | 137 |
#' | A1 | non-binary | unemployed | 203 |
#' | A2 | non-binary | unemployed | 270 |
#' | A3 | non-binary | unemployed |  34 |
#' @md
#' @examples
#' # some example mock data
#' # crosstabular stratified dataframe mock data
#' row1 = c("age_groups","male","male", "female", "female", "non-binary", "non-binary" )
#' row2 = c("", "employed", "unemployed", "employed", "unemployed", "employed", "unemployed")
#' row3 = c("A1", sample(1:400,6))
#' row4 = c("A2", sample(1:400,6))
#' row5 = c("A3", sample(1:400,6))
#' cross_tab_stratified_df = as.data.frame(rbind(row1, row2, row3, row4, row5))
#' print(cross_tab_stratified_df)
#'
#' # function application
#' ## the number of row variables are 2 (the sex and the employment status), while only age is a column variable, hence ncol_var = 1
#' singleside_df = crosstabular_to_singleside_df(df = cross_tab_stratified_df, nrow_var = 2, ncol_var = 1, row_var_names = c("sex", "employ_status"), col_var_names = c("age_group"))
#' print(singleside_df)
#'
#' @export
crosstabular_to_singleside_df =  function(df, nrow_var, ncol_var, row_var_names, col_var_names){
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
#' @title Restructures a single-sided stratified dataframe so that the classes of one column/variable of interest are seperate columns
#' @description This function takes a single-sided stratified dataframe, such as the output of the crosstabular_to_singleside_df function and restructures it as such that the unique classes of one variable of interest (any of the variablecolumns), will become seperate columns. Hence the output will be a dataframe of all variable combinations excluding the variable of interest and the marginal distributions of the variable combinations along the classes of the variable of interest.
#' @param df The original stratified dataframe with all varable combinations as columns on the left side.
#' @param variable The variable of interest, for which on wants to generate seperate columns of the subclasses.
#' @param countsname The columnname of the column in the original datafram, which indicates the counts for all variable combinations.
#' @return the output will be a dataframe of all variable combinations excluding the variable of interest and the marginal distributions of the variable combinations along the classes of the variable of interest.
#' @details
#' # Example Tables (random numbers)
#' ## Turns a single side stratified dataframe such as this:
#' |age_group |sex | employ_status | counts |
#' |:----:|:-----:|:----:|:---:|
#' | A1 | male | employed | 25 |
#' | A2 | male | employed | 132 |
#' | A3 | male | employed | 122 |
#' | A1 | male | unemployed | 133 |
#' | A2 | male | unemployed | 323 |
#' | A3 | male | unemployed | 360 |
#' | A1 | female | employed | 175 |
#' | A2 | female | employed | 275 |
#' | A3 | female | employed | 394 |
#' | A1 | female | unemployed | 389 |
#' | A2 | female | unemployed | 206 |
#' | A3 | female | unemployed |  25 |
#' | A1 | non-binary | employed | 196 |
#' | A2 | non-binary | employed | 248 |
#' | A3 | non-binary | employed | 137 |
#' | A1 | non-binary | unemployed | 203 |
#' | A2 | non-binary | unemployed | 270 |
#' | A3 | non-binary | unemployed |  34 |
#'
#' ## into a one variable marginal distribution table for a specified variable of interest, and adds a total for the population of the attribute combination
#' |age_group |sex | employed | un-employed | total |
#' |:----:|:-----:|:----:|:---:|:---:|
#' | A1 | male | 25 | 133 | 158 |
#' | A2 | male | 132 | 323 | 455 |
#' | A3 | male | 122 | 360 | 482 |
#' | A1 | female | 175 | 389 | 564 |
#' | A2 | female | 275 | 206 |481 |
#' | A3 | female | 394 |  25 | 419 |
#' | A1 | non-binary | 196 | 203 | 399 |
#' | A2 | non-binary | 248 | 270 | 518 |
#' | A3 | non-binary | 137 |  34 | 171 |
#' @md
#' @examples
#' ## generating some example mock data ##
#' # stratified dataframe mock data, can be output of function: crosstabular_to_singleside_df
#' age_group = c("A1", "A2", "A3", "A4", "A1", "A2", "A3", "A4", "A1", "A2", "A3", "A4", "A1", "A2", "A3", "A4", "A1", "A2", "A3", "A4", "A1", "A2", "A3", "A4")
#' sex = c("male","male","male","male", "female","female","female","female", "non-binary", "non-binary", "non-binary","non-binary", "male","male","male","male", "female","female","female","female", "non-binary", "non-binary", "non-binary","non-binary")
#' employ_status = c("employed", "employed", "employed", "employed", "employed", "employed", "employed", "employed", "employed", "employed", "employed", "employed", "unemployed", "unemployed", "unemployed", "unemployed", "unemployed", "unemployed", "unemployed", "unemployed", "unemployed", "unemployed", "unemployed", "unemployed")
#' counts = sample(1:400,length(age_group))
#' singleside_stratified_df = data.frame(age_group, sex , employ_status, counts)
#'
#' # function application
#' one_var_marginal_df = restructure_one_var_marginal(singleside_stratified_df, "employ_status", "counts")
#' print(one_var_marginal_df)
#'
#' @export
restructure_one_var_marginal = function(df, variable, countsname){
  classes = unique(df[,c(variable)])
  restColumns = colnames(df)[(colnames(df) != variable) & (colnames(df) != countsname)]
  df_new = unique(as.data.frame(df[, c(restColumns)]))
  colnames(df_new) = restColumns
  for(x in classes){
    df_new[, c(x)] = as.numeric(df[df[,c(variable)] == x, c(countsname)])
  }
  df_new[,c("total")] = rowSums(df_new[,c(classes)])
  return(df_new)
}


