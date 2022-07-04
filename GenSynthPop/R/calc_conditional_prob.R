
#' @title Calculating the conditional propensity to have an attribute based on conditional variables

#' @description This is a function to calculate the probability/propensity to have a specific class of a variable conditional on other variables. It requires a stratified dataframe (@dataframe) which includes all combinations of the conditional variables (the ones based on which we want to calculate the propensity), the number of people with the variable class (@variable) for which we want to calculate the propensity, and the total number of people within the combination of conditional variables (@total_population). The function calculates the propensity to have a specific class based on the conditional variables, by dividing the number of people with the class if interest by the total number of people within the combination of conditional variables. Further, the function joins these probabilities with the agent dataset (@agent_df) based on the list of conditional variables (@list_conditional_var). This requires the variable/column names of the conditional variables to be equal for the stratified and the agent dataframe. Finally, it shuffles the agent dataset to avoid biases due to a non random order in the next steps.

#' @param dataframe stratified dataframe which includes all combinations of the conditional variables (the ones based on which we want to calculate the propensity)
#' @param variable the number of people with the variable class for which we want to calculate the propensity
#' @param total_population the total number of people within the combination of conditional variables
#' @param agent_df agent dataset, the full dataset of individual agents that was previously created and that contains the conditional variables
#' @param list_conditional_var list of conditional variables, the variables on which basis the propensity to have an attribute should be created
#'
#' @return The output is the agent dataframe with an additional column of their propensity/probability to have the respective property/attribute.
#' @export
#'
#' @examples
#' # some example mock data
#' # stratified dataframe
#' age_group = c("A1", "A2", "A3", "A4", "A1", "A2", "A3", "A4", "A1", "A2", "A3", "A4")
#' sex = c("male","male","male","male", "female","female","female","female", "non-binary", "non-binary", "non-binary","non-binary")
#' employed = sample(1:400,length(age_group))
#' unemployed = sample(1:400,length(age_group))
#' total_pop = employed + unemployed
#' stratified_df = data.frame(age_group, sex , employed, unemployed, total_pop)
#'
#' # agent dataframe
#' agent_df = as.data.frame(paste("Agent_",1:500, sep="")))
#' agent_df$age_group = age_group[sample(1,len(age_group), lenght(agent_df))]
#' agent_df$sex = sex[sample(1,len(age_group), lenght(agent_df))]
#' colnames(agent_df) = c("agent_id",  "age_group", "sex" )
#'
#' # function application
#' agent_df = calc_propens_agents(stratified_df, "employed", "total_pop", agent_df, c("age_group", "sex"))
#'
calc_propens_agents = function(dataframe, variable, total_population, agent_df, list_conditional_var){
  if(!missing(total_population)){
    dataframe[,c(paste("prop_",variable, sep = ""))] = dataframe[,c(variable)]/dataframe[, c(total_population)]
  }
  order_agent_df = colnames(agent_df)
  if(paste("prop_",variable, sep = "") %in% order_agent_df){
    x = which(order_agent_df == paste("prop_",variable, sep = ""))
    agent_df = subset(agent_df, select = -c(x))
  }
  agent_df = merge(agent_df, dataframe[,c(list_conditional_var, paste("prop_",variable, sep = ""))], all.x = T, all.y= F, by = list_conditional_var)
  agent_df = agent_df[,c(order_agent_df, paste("prop_",variable, sep = ""))]
  random_seq = sample(nrow(agent_df))
  agent_df = agent_df[random_seq,]
  return(agent_df)
}

