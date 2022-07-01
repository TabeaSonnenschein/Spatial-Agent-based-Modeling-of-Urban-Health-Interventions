
#### cross validation with the neighborhood and stratified marginal distributions #######################

### EXPLANATION
# This function generates a table for validation that compares the original marginal distributions to the generated distributions of the agent dataset.
# valid_df is the dataset that contains the marginal distributions, this can be the neighborhood totals dataset or the stratified dataset
# agent_df is the agent dataset, which now contains the newly generated variable
# join_var is the variable or variables on which basis the datasets should be joined/ compared. 
# For a neighborhood totals dataset this would be the neighborhood code, while for a stratified dataset this would be all the conditional variables.
# list_valid_var lists the variables in the valid_df that should be compared to the newly generated variable. 
# (e.g when having generated the variable sex, then the variables we want to compare would be perhaps c("men", "women", "non_binary"))
# agent_var states the newly generated variable in the agent_df that should be validated
# list_agent_attr lists the generated attributes of this agent_var (e.g. c("male", "female", "non_binary"))
# Attention: the order of the list_valid_var and list_agent_attr needs to be equal.

crossvalid = function(valid_df, agent_df, join_var, list_valid_var, agent_var, list_agent_attr ){
  output = valid_df[,c(join_var, list_valid_var)]
  for(i in 1:length(list_agent_attr)){
    output[, c(paste("agent_",list_agent_attr[i], sep = ""))]= NA
  }
  if(length(join_var) > 1){
    valid_df$ID = paste("ID",1:nrow(valid_df), sep="")
    interm = merge(agent_df[, c(join_var, agent_var)], valid_df[, c(join_var, "ID")], by = join_var, all.x= T, all.y= F)
  }
  for(n in 1:nrow(output)){
    for(i in 1:length(list_agent_attr)){
      if(length(join_var) == 1){
        output[n, c(paste("agent_",list_agent_attr[i], sep = ""))]= nrow(agent_df[which(agent_df[, c(join_var)] == valid_df[n, c(join_var)] & agent_df[, c(agent_var)] == list_agent_attr[i]),])
        output[n, c(paste("diff_",list_agent_attr[i], sep = ""))]= output[n, c(paste("agent_",list_agent_attr[i], sep = ""))] - output[n, c(list_valid_var[i])]
      }
      else{
        output[n, c(paste("agent_",list_agent_attr[i], sep = ""))]= nrow(interm[which(interm[, c("ID")] == valid_df[n, c("ID")] & interm[, c(agent_var)] == list_agent_attr[i]),])
        output[n, c(paste("diff_",list_agent_attr[i], sep = ""))]= output[n, c(paste("agent_",list_agent_attr[i], sep = ""))] - output[n, c(list_valid_var[i])]
      }
    }
  }
  return(output)
}


#' Cross validation with the neighborhood and stratified marginal distributions
#'
#' This function generates a table for validation that compares the original marginal distributions to the generated distributions of the agent dataset.
#' @param valid_df the dataset that contains the marginal distributions, this can be the neighborhood totals dataset or the stratified dataset
#' @param agent_df is the agent dataset, which now contains the newly generated variable
#' @param join_var is the variable or variables on which basis the datasets should be joined/ compared. For a neighborhood totals dataset this would be the neighborhood code, while for a stratified dataset this would be all the conditional variables.
#' @param list_valid_var lists the variables in the valid_df that should be compared to the newly generated variable.(e.g when having generated the variable sex, then the variables we want to compare would be perhaps c("men", "women", "non_binary"))
#' @param agent_var states the newly generated variable in the agent_df that should be validated
#' @param list_agent_attr lists the generated attributes of this agent_var (e.g. c("male", "female", "non_binary")). Attention: the order of the list_valid_var and list_agent_attr needs to be equal.

#' @return orginal distribution dataset, agent distribution and difference
#' @examples 
#' temp1 <- F_to_C(50);
#' temp2 <- F_to_C( c(50, 63, 23) );
#' @export
F_to_C <- function(F_temp){
  C_temp <- (F_temp - 32) * 5/9;
  return(C_temp);
}
