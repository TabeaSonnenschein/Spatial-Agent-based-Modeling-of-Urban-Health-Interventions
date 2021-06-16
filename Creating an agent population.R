
## This script generates a set of agents based on statistical data that is 
## representative for a population of a city and can be used for simulation purposes, such as an agent-based model.

########################################################################################################
############### Generic Functions to generate a synthetic agent population #############################
########################################################################################################

####### Generating an agent dataframe of the population size and assigning a unique ID

gen_agent_df = function(pop_size){
  agent_ID = paste("Agent_",1:pop_size, sep="")
  agent_df = as.data.frame(agent_ID)
  return(agent_df)
}


####### Calculating the conditional probabilities to have an attribute

### EXPLANATION
# This is a function to calculate the probability/propensity to have a specific class of a variable conditional on other variables.
# It requires a stratified dataframe (@dataframe) which includes all combinations of the conditional variables (the ones based on which we want to calculate the propensity), 
# the number of people with the variable class (@variable) for which we want to calculate the propensity, 
# and the total number of people within the combination of conditional variables (@total_population).
# The function calculates the propensity to have a specific class based on the conditional variables, 
# by dividing the number of people with the class if interest by the total number of people within the combination of conditional variables.
# Further, the function joins these probabilities with the agent dataset (@agent_df) 
# based on the list of conditional variables (@list_conditional_var).
# This requires the variable/column names of the conditional variables to be equal for the stratified and the agent dataframe.
# Finally, it shuffles the agent dataset to avoid biases due to a non random order in the next steps.

calc_propens_agents = function(dataframe, variable, total_population, agent_df, list_conditional_var){
  dataframe[,c(paste("prop_",variable, sep = ""))] = dataframe[,c(variable)]/dataframe[, c(total_population)]
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

####### distributing attributes across agent population based on conditional proabilities and neighborhood totals 

### EXPLANATION
# This function distributes attribute classes in the agent population based on the conditional propensities and the neighborhood statistics
# agent_df = Dataframe of the unique agents with their attributes
# neigh_df = Dataframe of aggregate statistical data per neighborhood, specifically the total population 
# per neighborhood and the counts per variable class.
# variable = the new variable that we want to add based on the stratified and neighborhood marginal distributions
# list_var_classes_neigh_df = a list of the column names in the Neighborhood dataset with 
# the classes of the variable that will be modeled (e.g. c("Men", "Women", "Non-Binary"), which are the classes of sex). 
# list_agent_propens = A list of the columns in the agent dataset that contain the propensities for the classes of the variable based on the other agents conditional attributes.
# This list has to be in the same order as the list_var_classes_neigh_df, but can leave out the last propensity as it is 1 minus the other propensities.
# The list_class_names is optional and contains the values that the new created agent variable should have for the different variable classes.
# It has to be in the same order and of the same length as the list_var_classes_neigh_df. If left empty, the list_var_classes_neigh_df will become the default values for the classes.
# agent_exclude = an optional variable containing one or multiple variable names of the agent dataset on which basis agents should be excluded from the attribute assignment
# if that variable(s) is/are 1, then the agents will be excluded

## distr_bin_attr_strat_n_neigh_stats is for binary attributes

distr_bin_attr_strat_n_neigh_stats = function(agent_df, neigh_df, neigh_ID, variable, list_var_classes_neigh_df, list_agent_propens, list_class_names, agent_exclude){
  print(Sys.time())
  agent_df[, c(variable, "random_scores")] = 0
  if(missing(list_class_names)){
    list_class_names = list_var_classes_neigh_df
  }
  if(!missing(agent_exclude)){
    agent_df[, c("excluded")] = 0
    for(i in 1:length(agent_exclude)){
      agent_df[which(agent_df[, c(agent_exclude[i])] == 1) , c("excluded")] =  1
    }
  }
  for (i in 1:nrow(neigh_df)){
    if(!missing(agent_exclude)){
        x = which(agent_df[, c(neigh_ID)] == neigh_df[i, c(neigh_ID)] & agent_df[, c("excluded")] != 1)
    }
    else{
        x = which(agent_df[, c(neigh_ID)] == neigh_df[i, c(neigh_ID)])
    }
    tot__var_class_neigh = neigh_df[i, list_var_classes_neigh_df]
    agent_df[x, c("random_scores")] = sample(x= seq(from= 0, to = 1, by= 0.01), size = length(x), replace = T)
    fitness = 0
    if(length(x) != 0){
      while(fitness == 0){
        if(length(list_var_classes_neigh_df)== 2){
          agent_df[x[which(agent_df[x, c(list_agent_propens[1])] >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[1]
          agent_df[x[which(agent_df[x, c(list_agent_propens[1])] < agent_df[x,c("random_scores")])], c(variable)] = list_class_names[2]
            if(length(which(agent_df[x, c(variable)] == list_class_names[1])) >= tot__var_class_neigh[1] & length(which(agent_df[x, c(variable)] == list_class_names[2])) >= tot__var_class_neigh[2]){
              fitness = 1
            }
            else if(sum(tot__var_class_neigh) <= length(x)){
              agent_df[x, c("random_scores")] = sample(x= seq(from= 0, to = 1, by= 0.01), size = length(x), replace = T)
              agent_df[x[which(agent_df[x, c(list_agent_propens[1])] >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[1]
              agent_df[x[which(agent_df[x, c(list_agent_propens[1])] < agent_df[x,c("random_scores")])], c(variable)] = list_class_names[2]
              if(length(which(agent_df[x, c(variable)] == list_class_names[1])) >= tot__var_class_neigh[1] & length(which(agent_df[x, c(variable)] == list_class_names[2])) >= tot__var_class_neigh[2]){
                fitness = 1
              }
              else if(length(which(agent_df[x, c(variable)] == list_class_names[1])) < tot__var_class_neigh[1]){
                abs_diff = as.integer(as.numeric(tot__var_class_neigh[1]) - length(which(agent_df[x, c(variable)] == list_class_names[1])))
                if(abs_diff <= 1|is.na(abs_diff)){
                  fitness = 1
                }
                else{
                 class = which(agent_df[x, c(variable)] == list_class_names[2])[1:as.numeric(abs_diff)]
                 class = class[!is.na(class)]
                 if(length(class) == 0){
                   fitness = 1
                 }
                 agent_df[x[class], c(list_agent_propens[1])] = agent_df[x[class], c(list_agent_propens[1])] + 0.5
                }
              }
              else if(length(which(agent_df[x, c(variable)] == list_class_names[2])) < tot__var_class_neigh[2]){
                abs_diff = as.integer(as.numeric(tot__var_class_neigh[2]) - length(which(agent_df[x, c(variable)] == list_class_names[2])))
                if(abs_diff <= 1|is.na(abs_diff)){
                  fitness = 1
                }
                else{
                  class = which(agent_df[x, c(variable)] == list_class_names[1])[1:as.numeric(abs_diff)]
                  class = class[!is.na(class)]
                  if(length(class) == 0){
                    fitness = 1
                  }
                  agent_df[x[class], c(list_agent_propens[1])] = agent_df[x[class], c(list_agent_propens[1])] - 0.5
                }
              }
            }
            else if(length(x) < 10){
             fitness = 1
            }
            else if(sum(tot__var_class_neigh) > length(x)){
              percent_diff1 = length(which(agent_df[x, c(variable)] == list_class_names[1]))/as.numeric(tot__var_class_neigh[1])
              percent_diff2 = length(which(agent_df[x, c(variable)] == list_class_names[2]))/as.numeric(tot__var_class_neigh[2])
              percent_diff_diff = percent_diff1 - percent_diff2
              if(abs(percent_diff_diff) < 0.02|is.na(percent_diff_diff)){
                fitness = 1
              }
              else{
                if( percent_diff_diff < 0){
                  abs_diff = as.integer((((as.numeric(abs(percent_diff_diff)))/2) * as.numeric(tot__var_class_neigh[1]))/3)
                  if(abs_diff <= 1|is.na(abs_diff)){
                    fitness = 1
                  }
                  else{
                    class = which(agent_df[x, c(variable)] == list_class_names[2])[1:abs_diff]
                    class = class[!is.na(class)]
                    if(length(class) == 0){
                      fitness = 1
                    }
                    agent_df[x[class], c(list_agent_propens[1])] = agent_df[x[class], c(list_agent_propens[1])] + 0.3
                  }
                }
                else{
                  abs_diff = as.integer((((as.numeric(abs(percent_diff_diff)))/2) * as.numeric(tot__var_class_neigh[2]))/3)
                  if(abs_diff <= 1|is.na(abs_diff)){
                    fitness = 1
                  }
                  else{
                    class = which(agent_df[x, c(variable)] == list_class_names[1])[1:abs_diff]
                    class = class[!is.na(class)]
                    if(length(class) == 0){
                      fitness = 1
                    }
                     agent_df[x[class], c(list_agent_propens[1])] = agent_df[x[class], c(list_agent_propens[1])] - 0.3
                  }
                }
              }
            }
        }
      }
    } 
    print(paste("neighborhood:", i))
  }
  random_seq = sample(nrow(agent_df))
  agent_df = agent_df[random_seq,]
  print(Sys.time())
  return(agent_df)
}

## distr_attr_strat_n_neigh_stats_3plus is for attributes with three or more values

distr_attr_strat_n_neigh_stats_3plus = function(agent_df, neigh_df, neigh_ID, variable, list_var_classes_neigh_df, list_agent_propens, list_class_names, agent_exclude){
  print(Sys.time())
  agent_df[, c(variable, "random_scores")] = 0
  if(missing(list_class_names)){
    list_class_names = list_var_classes_neigh_df
  }
  if(!missing(agent_exclude)){
    agent_df[, c("excluded")] = 0
    for(i in 1:length(agent_exclude)){
      agent_df[which(agent_df[, c(agent_exclude[i])] == 1) , c("excluded")] =  1
    }
  }
  lvar = length(list_var_classes_neigh_df)
  for (i in 1:nrow(neigh_df)){
    if(!missing(agent_exclude)){
      x = which(agent_df[, c(neigh_ID)] == neigh_df[i, c(neigh_ID)] & agent_df[, c("excluded")] != 1)
    }
    else{
      x = which(agent_df[, c(neigh_ID)] == neigh_df[i, c(neigh_ID)])
    }
    tot__var_class_neigh = neigh_df[i, list_var_classes_neigh_df]
    agent_df[x, c("random_scores")] = sample(x= seq(from= 0, to = 1, by= 0.01), size = length(x), replace = T)
    fitness = 0
    if(length(x) != 0){
      while(fitness == 0){
        if(lvar > 2){
          agent_df[x[which(agent_df[x, c(list_agent_propens[1])] >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[1]
          agent_df[x[which(agent_df[x, c(list_agent_propens[1])] < agent_df[x,c("random_scores")] & rowSums(agent_df[x, c(list_agent_propens[1:2])]) >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[2]
          if(lvar >3){
            for(n in 3:(lvar -1)){
              agent_df[x[which(rowSums(agent_df[x, c(list_agent_propens[1:(n-1)])]) < agent_df[x,c("random_scores")] & rowSums(agent_df[x, c(list_agent_propens[1:n])]) >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[n]
            }
          }
          agent_df[x[which(rowSums(agent_df[x, c(list_agent_propens[1:(lvar -1)])]) < agent_df[x,c("random_scores")])], c(variable)] = list_class_names[lvar]
          if((length(which(agent_df[x, c(variable)] == list_class_names[1])) >= tot__var_class_neigh[1] & length(which(agent_df[x, c(variable)] == list_class_names[2])) >= tot__var_class_neigh[2] & length(which(agent_df[x, c(variable)] == list_class_names[3])) >= tot__var_class_neigh[3]) | sum(tot__var_class_neigh) == 0 | is.na(sum(tot__var_class_neigh))){
            fitness = 1
          }
          else if(sum(tot__var_class_neigh) <= length(x)){
            agent_df[x, c("random_scores")] = sample(x= seq(from= 0, to = 1, by= 0.01), size = length(x), replace = T)
            agent_df[x[which(agent_df[x, c(list_agent_propens[1])] >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[1]
            agent_df[x[which(agent_df[x, c(list_agent_propens[1])] < agent_df[x,c("random_scores")] & rowSums(agent_df[x, c(list_agent_propens[1:2])]) >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[2]
            if(lvar>3){
              for(n in 3:(lvar-1)){
                agent_df[x[which(rowSums(agent_df[x, c(list_agent_propens[1:(n-1)])]) < agent_df[x,c("random_scores")] & rowSums(agent_df[x, c(list_agent_propens[1:n])]) >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[n]
              }
            }
            agent_df[x[which(rowSums(agent_df[x, c(list_agent_propens[1:(lvar -1)])]) < agent_df[x,c("random_scores")])], c(variable)] = list_class_names[lvar]
            if(length(which(agent_df[x, c(variable)] == list_class_names[1])) >= tot__var_class_neigh[1] & length(which(agent_df[x, c(variable)] == list_class_names[2])) >= tot__var_class_neigh[2] & length(which(agent_df[x, c(variable)] == list_class_names[3])) >= tot__var_class_neigh[3]){
              fitness = 1
            }
            else{
              underrepresented = c()
              for(n in 1:(lvar)){
                 if(length(which(agent_df[x, c(variable)] == list_class_names[n])) < tot__var_class_neigh[n]){
                   underrepresented = append(underrepresented, 1)
                 }
                else{
                  underrepresented = append(underrepresented, 0)
                }
              }
              for(n in 1:(lvar)){
                if(underrepresented[n] == 1){
                  abs_diff = (tot__var_class_neigh[n] - length(which(agent_df[x, c(variable)] == list_class_names[n])))
                  class = which(agent_df[x, c(variable)] %in% list_class_names[which(underrepresented == 0)])[1:as.numeric(abs_diff)]
                  class = class[!is.na(class)]
                  agent_df[x[class], c(variable)] = list_class_names[n]
                  agent_df[x[class], c(list_agent_propens[n])] = agent_df[x[class], c(list_agent_propens[n])] + 0.5
                  agent_df[x[class], c(list_agent_propens[which(underrepresented == 0)])] = agent_df[x[class], c(list_agent_propens[which(underrepresented == 0)])] - (0.5/length(which(underrepresented == 0)))
                }
              }
              if(length(which(agent_df[x, c(variable)] == list_class_names[1])) >= tot__var_class_neigh[1] & length(which(agent_df[x, c(variable)] == list_class_names[2])) >= tot__var_class_neigh[2] & length(which(agent_df[x, c(variable)] == list_class_names[3])) >= tot__var_class_neigh[3]){
                fitness = 1
              }
            }  
          }
          else if(sum(tot__var_class_neigh) > length(x)){
            percent_diff = c()
            for(n in 1:(lvar)){
              if(tot__var_class_neigh[n] != 0){
                percent_diff = append(percent_diff, length(which(agent_df[x, c(variable)] == list_class_names[n]))/as.numeric(tot__var_class_neigh[n]))
              }
              else{
                percent_diff = append(percent_diff, NA)
              }
            }
            print(percent_diff)
            percent_diff_diff = as.data.frame(matrix(data = NA, nrow = length(list_var_classes_neigh_df), ncol = length(list_var_classes_neigh_df)))
            for(n in 1:(lvar)){
              for(k in 1:(lvar)){
                percent_diff_diff[n, k] = percent_diff[n] - percent_diff[k]
              }
            }
            if(all(abs(na.omit(percent_diff_diff)) < 0.03)){
              fitness = 1
            }
            else{
              tot_abs_diff = c()
              for(n in 1:(lvar)){
                m = which(percent_diff_diff[n,] < (-0.03))
                if(length(m)> 0){
                  abs_diff = as.numeric(((sum(as.numeric(abs(percent_diff_diff[n, m])))/length(m)) * as.numeric(tot__var_class_neigh[n])))
                  tot_abs_diff = append(tot_abs_diff, abs_diff )
                  for(l in m){
                    class = which(agent_df[x, c(variable)] %in% list_class_names[l])[1:as.integer((abs_diff/3)*(as.numeric(tot__var_class_neigh[l])/sum(as.numeric(tot__var_class_neigh[m]))))]
                    class = class[!is.na(class)]
                    agent_df[x[class], c(variable)] = list_class_names[n]
                    agent_df[x[class], c(list_agent_propens[n])] = agent_df[x[class], c(list_agent_propens[n])] + 0.3
                    agent_df[x[class], c(list_agent_propens[m])] = agent_df[x[class], c(list_agent_propens[m])] - (0.3/length(m))
                  }
                }
              }
              if(all(abs(tot_abs_diff) < 3)){
                fitness = 1
              }
              else{
                percent_diff = c()
                for(n in 1:(lvar)){
                  if(tot__var_class_neigh[n] != 0){
                    percent_diff = append(percent_diff, length(which(agent_df[x, c(variable)] == list_class_names[n]))/as.numeric(tot__var_class_neigh[n]))
                  }
                  else{
                    percent_diff = append(percent_diff, NA)
                  }                }
                print(percent_diff)
                percent_diff_diff = as.data.frame(matrix(data = NA, nrow = length(list_var_classes_neigh_df), ncol = length(list_var_classes_neigh_df)))
                for(n in 1:(lvar)){
                  for(k in 1:(lvar)){
                    percent_diff_diff[n, k] = percent_diff[n] - percent_diff[k]
                  }
                }
                if(all(abs(na.omit(percent_diff_diff)) < 0.05)){
                  fitness = 1
                }
                # else{
                #   agent_df[x, c("random_scores")] = sample(x= seq(from= 0, to = 1, by= 0.01), size = length(x), replace = T)
                # } 
              }
            }
          }
        }
        else if(lvar == 2){
          print("use binary attribute function: distr_bin_attr_strat_n_neigh_stats() ")
        }
      }
    } 
    print(paste("neighborhood:", i))
  }
  random_seq = sample(nrow(agent_df))
  agent_df = agent_df[random_seq,]
  print(Sys.time())
  return(agent_df)
}




#### assigning attributes purely based on conditional probabilities

distr_attr_cond_prop = function(agent_df, variable, list_agent_propens, list_class_names, agent_exclude){
  print(Sys.time())
  agent_df[, c(variable, "random_scores")] = 0
  if(!missing(agent_exclude)){
    agent_df[, c("excluded")] = 0
    for(i in 1:length(agent_exclude)){
      agent_df[which(agent_df[, c(agent_exclude[i])] == 1) , c("excluded")] =  1
    }
    x = which(agent_df[, c("excluded")] != 1)
  }
  else{
    x = which(agent_df[, c(variable)] == 0)
  }
  lvar = length(list_class_names)
  agent_df[x, c("random_scores")] = sample(x= seq(from= 0, to = 1, by= 0.01), size = length(x), replace = T)
  if(lvar == 2){
    agent_df[x[which(agent_df[x, c(list_agent_propens[1])] >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[1]
    agent_df[x[which(agent_df[x, c(list_agent_propens[1])] < agent_df[x,c("random_scores")])], c(variable)] = list_class_names[2]
  }
  else if(lvar > 2){
    agent_df[x[which(agent_df[x, c(list_agent_propens[1])] >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[1]
    agent_df[x[which(agent_df[x, c(list_agent_propens[1])] < agent_df[x,c("random_scores")] & rowSums(agent_df[x, c(list_agent_propens[1:2])]) >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[2]
    if(lvar >3){
      for(n in 3:(lvar -1)){
        agent_df[x[which(rowSums(agent_df[x, c(list_agent_propens[1:(n-1)])]) < agent_df[x,c("random_scores")] & rowSums(agent_df[x, c(list_agent_propens[1:n])]) >= agent_df[x,c("random_scores")])], c(variable)] = list_class_names[n]
      }
    }
    agent_df[x[which(rowSums(agent_df[x, c(list_agent_propens[1:(lvar -1)])]) < agent_df[x,c("random_scores")])], c(variable)] = list_class_names[lvar]
  }
  random_seq = sample(nrow(agent_df))
  agent_df = agent_df[random_seq,]
  print(Sys.time())
  return(agent_df)
}




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

############################################################################################
######################## Data Preparation and Application for Amsterdam ####################
############################################################################################

################## loading the census datasets and if necessary subselecting relevant parts #################################
setwd("C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Population/CBS statistics")

## Neighborhood dataset
popstats = read.csv("Neighborhood statistics 2020.csv") ## count of people per age group per neighborhood
neigh_stats = popstats[which(popstats$SoortRegio_2 == "Buurt     "),]
popstats2 = read.csv("Neighborhood statistics 2019.csv") ## count of people per age group per neighborhood
neigh_stats2 = popstats2[which(popstats2$SoortRegio_2 == "Buurt     "),]
popstats3 = read.csv("Neighborhood statistics 2018.csv") ## count of people per age group per neighborhood
neigh_stats3 = popstats3[which(popstats3$SoortRegio_2 == "Buurt     "),]

#Stratified datasets
# SEX - AGE
sexstats = read.csv("Amsterdam_tot_sex_gender2020.csv") # count of people per lifeyear and gender in all of Amsterdam
sexstats$totpop = sexstats$male + sexstats$female

# AGE - SEX - MIGRATIONBACKGROUND - HOUSEHOLD COMPOSITION
migrat_stats = read.csv("age gender migrationbackground familie position.csv")
migrat_stats = migrat_stats[which(migrat_stats$Generatie == "T001040"),]
migrat_age = read.csv("agegroup coding_migration data.csv")
colnames(migrat_age) = c("Leeftijd", "age")
migrat_stats = merge(migrat_stats, migrat_age, all.x = T, all.y = F, by = "Leeftijd")

# EDUCATION - AGE - SEX - MIGRATIONBACKGROUND
setwd("C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Population/CBS statistics/socioeconomics")
absolved_edu = read.csv("diplomaabsolvation conditioned by age sex and migrationbackground.csv")
current_edu = read.csv("students conditioned by age sex and migrationbackground.csv")
age_coding = read.csv("age_coding.csv")
edu_coding = read.csv("education_coding.csv")
colnames(age_coding)[1] = "Leeftijd"
colnames(edu_coding)[1:2] = c("Onderwijssoort", "education_level")
absolved_edu = merge(absolved_edu, age_coding, by= "Leeftijd", all.x = T, all.y = F)
current_edu = merge(current_edu, age_coding, by= "Leeftijd", all.x = T, all.y = F)
absolved_edu = merge(absolved_edu, edu_coding, by= "Onderwijssoort", all.x = T, all.y = F)
current_edu = merge(current_edu, edu_coding, by= "Onderwijssoort", all.x = T, all.y = F)




#### Interesting variables

###################
## Demographics ###
###################
## Neighborhood dataset
neigh_stats[,c( "k_0Tot15Jaar", "k_15Tot25Jaar" , "k_25Tot45Jaar", "k_45Tot65Jaar", "k_65JaarOfOuder", 
                "Mannen_6", "Vrouwen_7", "WestersTotaal_17", "NietWestersTotaal_18",
                "GeboorteTotaal_24", "GeboorteRelatief_25" , "SterfteTotaal_26" , "SterfteRelatief_27")] 

## Stratified datasets
sexstats[, c("age",  "male" , "female" , "totpop")]

migrat_stats[, c("age", "Geslacht" , "Migratieachtergrond")]

############################
## Household Composition ###
############################
## Neighborhood dataset
neigh_stats[,c( "HuishoudensTotaal_28", "Eenpersoonshuishoudens_29" , 
"HuishoudensZonderKinderen_30", "HuishoudensMetKinderen_31" , "GemiddeldeHuishoudensgrootte_32")]

## Stratified datasets
migrat_stats[, c("age", "Geslacht" , "Migratieachtergrond" , "TotaalAantalPersonenInHuishoudens_1" , "ThuiswonendKind_2" , "Alleenstaand_3" , 
                 "TotaalSamenwonendePersonen_4" ,  "PartnerInNietGehuwdPaarZonderKi_5" ,     "PartnerInGehuwdPaarZonderKinderen_6" , 
                 "PartnerInNietGehuwdPaarMetKinderen_7",  "PartnerInGehuwdPaarMetKinderen_8",    "OuderInEenouderhuishouden_9"  )]


####################
## Socioeconomics ##
####################
## Neighborhood dataset

# education level
neigh_stats2[,c("OpleidingsniveauLaag_64" , "OpleidingsniveauMiddelbaar_65" ,"OpleidingsniveauHoog_66")]

# employment
neigh_stats[,c("NettoArbeidsparticipatie_67" , "PercentageWerknemers_68", "PercentageZelfstandigen_69" )]

#income
neigh_stats3[,c("AantalInkomensontvangers_67"  , "k_40PersonenMetLaagsteInkomen_70" , "k_20PersonenMetHoogsteInkomen_71",  
                "k_40HuishoudensMetLaagsteInkomen_73",  "k_20HuishoudensMetHoogsteInkomen_74",  "HuishoudensMetEenLaagInkomen_75",
                "HuishOnderOfRondSociaalMinimum_76")]

#social support
neigh_stats[, c("HuishOnderOfRondSociaalMinimum_79" , "HuishoudensTot110VanSociaalMinimum_80", "HuishoudensTot120VanSociaalMinimum_81" ,"MediaanVermogenVanParticuliereHuish_82", 
  "PersonenPerSoortUitkeringBijstand_83" , "PersonenPerSoortUitkeringAO_84", "PersonenPerSoortUitkeringWW_85" , "PersonenPerSoortUitkeringAOW_86", "JongerenMetJeugdzorgInNatura_87",
  "PercentageJongerenMetJeugdzorg_88")]

## Stratified datasets

# education level
current_edu[, c("education_level" , "age" ,  "sex"  , "Migratieachtergrond"  , "LeerlingenDeelnemersStudenten_1")]           
absolved_edu[, c("education_level" , "age" ,  "sex"  , "Migratieachtergrond"  , "Gediplomeerden_1")]  


###########################################################################################################
################################## determining size of agent population ###################################
###########################################################################################################

## Amsterdam official total population
#2021 872497
#2020 872757
#2018 854047

# CBS neighborhood summary statistics dataset 2020
## CBS must have made a mistake, probably with the age grouping, because the total is larger than the general population. 
sum(neigh_stats[,10:14]) # 875920 tot when summarizing age groups per neighborhood
sum(neigh_stats[,8:9]) #870535 tot when summarizing sex per neighborhood
sum(neigh_stats[,7]) # 871395 tot when summarizing tot pop per neighborhood

# testing if excess population when summarizing age groups could be due to double counting of edge ages of age classes (eg. 15 counted as part of 0-15 and 5-25)
sum(sexstats$totpop[sexstats$ï..age == 15], sexstats$totpop[sexstats$ï..age == 25], sexstats$totpop[sexstats$ï..age == 45], sexstats$totpop[sexstats$ï..age == 65])
#However, the sum of these edge ages is 44941, which is way larger than the excess population

# I chose the total sum of all agegroups as a starting population size as this is also my initial variable.
# When translating into integer age at hand of a lifeyear dataset, the redundant agent population can be deleted.
agents = gen_agent_df(875920)

#####################################################################################################
######################## Start with a spatial reference and initial variable:  ######################
################################ agegroup within neighborhood #######################################
agents$age_group = ""
agents$neighb_code = ""

colnames(neigh_stats)
colnam = c("k_0Tot15Jaar", "k_15Tot25Jaar" , "k_25Tot45Jaar", "k_45Tot65Jaar", "k_65JaarOfOuder" )

n = 0 # indice of agent population that is populated with attributes
for(i in 1:nrow(neigh_stats)){   # neighborhood indice
  for(g in 10:14) {            # agegroup indice
    nr_people = neigh_stats[i,g]
    agents$age_group[(n+1):(n+nr_people)] = colnam[g-9]
    agents$neighb_code[(n+1):(n+nr_people)] = neigh_stats$Codering_3[i]
    n = n + nr_people
  }
}

random_seq = sample(nrow(agents))
agents = agents[random_seq,]

############################################################################################################################
################################ Translating age groups into interger age based on age dataset #############################
################################ age (year) based on lifeyear data for city ################################################
agents$age = ""

sexstats$age_group = "" #classifying ages into age groups to link to agent dataset
# age groups are "k_0Tot15Jaar", "k_15Tot25Jaar" , "k_25Tot45Jaar", "k_45Tot65Jaar", "k_65JaarOfOuder"
sexstats$age_group[sexstats$ï..age %in% 0:14] = "k_0Tot15Jaar"
sexstats$age_group[sexstats$ï..age %in% 15:24] = "k_15Tot25Jaar"
sexstats$age_group[sexstats$ï..age %in% 25:44] = "k_25Tot45Jaar"
sexstats$age_group[sexstats$ï..age %in% 45:64] = "k_45Tot65Jaar"
sexstats$age_group[sexstats$ï..age %in% 65:105] = "k_65JaarOfOuder"


n = 0 # indice of agent population that is populated with attributes
for(g in 1:5){   # agegroup indice
  x = which(agents$age_group == colnam[g])
  f = 0
  for(m in min(which(sexstats$age_group == colnam[g])):max(which(sexstats$age_group == colnam[g]))){
    nr_people = sexstats[(m), 6]
    agents$age[(x[(f+1):(f+nr_people)])] = sexstats$ï..age[m]
    f = f + nr_people
  }
}

## As discussed when determining the population size, there the sum of all neighborhood agegroup totals was chosen, 
## which exceeds the official total population of Amsterdam. The lifeyear dataset adds up to the official total population. 
## Herewith the excess population that was not covered with the lifeyear dataset is cut out.
agents = agents[which(agents$age != ""),]


## To avoid biases in the data generation due to non-arbitrary order, this piece of code shuffles the dataset randomly.
random_seq = sample(nrow(agents))
agents = agents[random_seq,]


plot(density(as.numeric(agents$age)))


############################################ #############################################################################
########## First Application of the conditional propensity & neighborhood constraint functions: ############################
######################################## Variable: Sex ###################################################################
##########################################################################################################################

############################### sex (based on sex per neighborhood and sex per age statistics) ######################################################################

## Data Preparation
colnames(sexstats)[1] = "age"
colnames(neigh_stats)[5] = "neighb_code"

## Conditional Propensities
agents = calc_propens_agents(sexstats, "female", "totpop", agents, c("age"))

## assigning attributes to agents
agents = distr_bin_attr_strat_n_neigh_stats(agent_df = agents, neigh_df = neigh_stats, neigh_ID = "neighb_code", 
                                    variable=  "sex",  list_var_classes_neigh_df = c("Vrouwen_7", "Mannen_6"), list_agent_propens =  c("prop_female"), 
                                    list_class_names = c("female", "male"))
# 2min run for agent pop of 872754

## cross validating with neighborhood and stratified totals
neigh_valid = crossvalid(valid_df = neigh_stats, agent_df = agents, join_var = "neighb_code", list_valid_var = c("Mannen_6", "Vrouwen_7"), 
                         agent_var = "sex", list_agent_attr = c("male", "female") )

strat_valid = crossvalid(valid_df = sexstats, agent_df = agents, join_var = "age", list_valid_var = c("male", "female"), 
                         agent_var = "sex", list_agent_attr = c("male", "female") )

write.csv(agents, "Agent_pop.csv")
agents = read.csv("Agent_pop.csv") ## count of people per age group per neighborhood
agents = agents[,c("agent_ID","neighb_code",  "age_group"  , "age" , "sex")]

##################################################################
################## migration background ##########################
##################################################################

## Data Preparation
migrat_stats = migrat_stats[, c("age", "Geslacht" , "Migratieachtergrond" ,  "TotaalAantalPersonenInHuishoudens_1" , "ThuiswonendKind_2" , 
                                "Alleenstaand_3" , "TotaalSamenwonendePersonen_4" ,  "PartnerInNietGehuwdPaarZonderKi_5" ,
                                "PartnerInGehuwdPaarZonderKinderen_6" , "PartnerInNietGehuwdPaarMetKinderen_7",  "PartnerInGehuwdPaarMetKinderen_8",   
                                "OuderInEenouderhuishouden_9" )]

migrat_age = rbind(migrat_age, migrat_age)
migrat_age$sex =""
migrat_age$sex[0:21] = "female"
migrat_age$sex[22:42] = "male"
migrat_age$tot = 0
migrat_age$Western = 0
migrat_age$Dutch = 0
migrat_age$Non_Western = 0

for(i in 1:nrow(migrat_age)){
  migrat_age$tot[i] = sum(migrat_stats$TotaalAantalPersonenInHuishoudens_1[which(migrat_stats$age == migrat_age$age[i] & migrat_stats$Geslacht == migrat_age$sex[i])])
  migrat_age$Western[i] = migrat_stats$TotaalAantalPersonenInHuishoudens_1[which(migrat_stats$age == migrat_age$age[i] & migrat_stats$Geslacht == migrat_age$sex[i] & migrat_stats$Migratieachtergrond == "\"Westerse migratieachtergrond\"" )]
  migrat_age$Dutch[i] = migrat_stats$TotaalAantalPersonenInHuishoudens_1[which(migrat_stats$age == migrat_age$age[i] & migrat_stats$Geslacht == migrat_age$sex[i] & migrat_stats$Migratieachtergrond == "\"Nederlandse achtergrond\"" )]
  migrat_age$Non_Western[i] = migrat_stats$TotaalAantalPersonenInHuishoudens_1[which(migrat_stats$age == migrat_age$age[i] & migrat_stats$Geslacht == migrat_age$sex[i] & migrat_stats$Migratieachtergrond == "\"Niet-westerse migratieachtergrond\"")]
}


agents$age_group_20 = "" #classifying ages into age groups to link to migrant dataset
# "95 jaar of ouder" "0 tot 5 jaar"     "5 tot 10 jaar"    "10 tot 15 jaar"   "15 tot 20 jaar"   "20 tot 25 jaar"   "25 tot 30 jaar"  
# "30 tot 35 jaar"   "35 tot 40 jaar"   "40 tot 45 jaar"   "45 tot 50 jaar"   "50 tot 55 jaar"   "55 tot 60 jaar"   "60 tot 65 jaar"   "65 tot 70 jaar"  
# "70 tot 75 jaar"   "75 tot 80 jaar"   "80 tot 85 jaar"   "85 tot 90 jaar"   "90 tot 95 jaar"
agents$age_group_20[agents$age %in% 0:4] = "0 tot 5 jaar"
agents$age_group_20[agents$age %in% 5:9] = "5 tot 10 jaar"
agents$age_group_20[agents$age %in% 10:14] =  "10 tot 15 jaar"
agents$age_group_20[agents$age %in% 15:19] = "15 tot 20 jaar"
agents$age_group_20[agents$age %in% 20:24] =  "20 tot 25 jaar" 
agents$age_group_20[agents$age %in% 25:29] = "25 tot 30 jaar"
agents$age_group_20[agents$age %in% 30:34] =  "30 tot 35 jaar"
agents$age_group_20[agents$age %in% 35:39] =  "35 tot 40 jaar" 
agents$age_group_20[agents$age %in% 40:44] = "40 tot 45 jaar"
agents$age_group_20[agents$age %in% 45:49] = "45 tot 50 jaar"
agents$age_group_20[agents$age %in% 50:54] =  "50 tot 55 jaar"
agents$age_group_20[agents$age %in% 55:59] = "55 tot 60 jaar"
agents$age_group_20[agents$age %in% 60:64] =  "60 tot 65 jaar" 
agents$age_group_20[agents$age %in% 65:69] = "65 tot 70 jaar"
agents$age_group_20[agents$age %in% 70:74] =  "70 tot 75 jaar"
agents$age_group_20[agents$age %in% 75:79] =  "75 tot 80 jaar" 
agents$age_group_20[agents$age %in% 80:84] =  "80 tot 85 jaar" 
agents$age_group_20[agents$age %in% 85:89] = "85 tot 90 jaar"
agents$age_group_20[agents$age %in% 90:94] =  "90 tot 95 jaar"
agents$age_group_20[agents$age %in% 95:104] =  "95 jaar of ouder" 

colnames(migrat_age)[2] = "age_group_20"
neigh_stats$nr_Dutch = neigh_stats$AantalInwoners_5 - (neigh_stats$WestersTotaal_17 + neigh_stats$NietWestersTotaal_18)


## Conditional Propensities
agents = calc_propens_agents(migrat_age, "Dutch", "tot", agents, c("age_group_20", "sex") )
agents = calc_propens_agents(migrat_age, "Western", "tot", agents, c("age_group_20", "sex") )
agents = calc_propens_agents(migrat_age, "Non_Western", "tot", agents, c("age_group_20", "sex") )

## assigning attributes to agents
agents = distr_attr_strat_n_neigh_stats_3plus(agent_df =  agents, neigh_df =  neigh_stats, neigh_ID =  "neighb_code", variable =  "migrationbackground", 
                                   list_var_classes_neigh_df =  c("nr_Dutch", "WestersTotaal_17", "NietWestersTotaal_18"), 
                                   list_agent_propens =  c("prop_Dutch", "prop_Western", "prop_Non_Western"), list_class_names =  c("Dutch", "Western", "Non-Western"))

## cross validating with neighborhood and stratified totals
neigh_valid = crossvalid(valid_df = neigh_stats, agent_df = agents, join_var = "neighb_code", list_valid_var = c("nr_Dutch", "WestersTotaal_17", "NietWestersTotaal_18"), 
                         agent_var = "migrationbackground", list_agent_attr = c("Dutch", "Western", "Non-Western") )

strat_valid = crossvalid(valid_df = migrat_age, agent_df = agents, join_var = c("age_group_20", "sex"), list_valid_var =  c("Dutch", "Western", "Non_Western"), 
                         agent_var = "migrationbackground", list_agent_attr =  c("Dutch", "Western", "Non-Western") )


agents= agents[,c("agent_ID","neighb_code",  "age" , "sex", "age_group" , "age_group_20", "migrationbackground")]
write.csv(agents, "Agent_pop.csv")

######################################################################
################### household composition ############################
######################################################################
householdstats = read.csv("household position age gender.csv") ## count of people per age group per neighborhood
# and migrat_stats 

#### is a child

agents$ischild = 0
agents$ischild[which(agents$age %in%0:17)] = 1


### Single Household or not

## Data Preparation
migrat_stats$migrationbackground = ""
migrat_stats$migrationbackground[migrat_stats$Migratieachtergrond == "\"Westerse migratieachtergrond\""] = "Western"
migrat_stats$migrationbackground[migrat_stats$Migratieachtergrond == "\"Niet-westerse migratieachtergrond\""] = "Non-Western"
migrat_stats$migrationbackground[migrat_stats$Migratieachtergrond == "\"Nederlandse achtergrond\""] = "Dutch"
colnames(migrat_stats)[1:2] = c("age_group_20", "sex")
colnames(migrat_stats)[7] = c( "singlehh")

neigh_stats$nr_multiplehh = NA
for (i in 1:nrow(neigh_stats)) {
  neigh_stats$nr_multiplehh[i] = (nrow(agents[which(agents$neighb_code == neigh_stats$neighb_code[i] & agents$ischild != 1),])- as.numeric(neigh_stats$Eenpersoonshuishoudens_29[i]))
  if(neigh_stats$nr_multiplehh[i] < 0){
    neigh_stats$nr_multiplehh[i] = 0
  }
}


## Conditional Propensities
agents = calc_propens_agents(dataframe =  migrat_stats, variable =  "singlehh", total_population =  "TotaalAantalPersonenInHuishoudens_1", agent_df =  agents, list_conditional_var = c("age_group_20", "sex", "migrationbackground") )

## assigning attributes to agents
agents = distr_bin_attr_strat_n_neigh_stats(agent_df = agents, neigh_df = neigh_stats, neigh_ID = "neighb_code", agent_exclude = c("ischild"),
                                       variable=  "hh_single",  list_var_classes_neigh_df = c("Eenpersoonshuishoudens_29", "nr_multiplehh"), list_agent_propens =  c("prop_singlehh"), 
                                       list_class_names = c(1, 0))

## cross validating with neighborhood and stratified totals
neigh_valid = crossvalid(valid_df = neigh_stats, agent_df = agents, join_var = "neighb_code", list_valid_var = c("Eenpersoonshuishoudens_29", "nr_multiplehh"), 
                         agent_var = "hh_single", list_agent_attr = c(1, 0) )

strat_valid = crossvalid(valid_df = migrat_stats, agent_df = agents, join_var = c("age_group_20", "sex", "migrationbackground"), list_valid_var =  c("singlehh"), 
                         agent_var = "hh_single", list_agent_attr =  c(1, 0) )


### has a child

## Data Preparation
migrat_stats$have_kids = migrat_stats$PartnerInNietGehuwdPaarMetKinderen_7 + migrat_stats$PartnerInGehuwdPaarMetKinderen_8

neigh_stats$nr_kids = 0
neigh_stats$nr_ppl_with_kids = 0
neigh_stats$nr_ppl_without_kids = 0

for (i in 1:nrow(neigh_stats)){
  neigh_stats$nr_kids[i] = length(which(agents$neighb_code == neigh_stats$neighb_code[i] & agents$ischild == 1))
  neigh_stats$nr_ppl_with_kids[i] = neigh_stats$nr_kids[i] * 1.8 #20% live in single parent households
  neigh_stats$nr_ppl_without_kids[i] = (length(which(agents$neighb_code == neigh_stats$neighb_code[i] & agents$ischild != 1 & agents$hh_single != 1)))- neigh_stats$nr_ppl_with_kids[i]
}

## Conditional Propensities
agents = calc_propens_agents(dataframe =  migrat_stats, variable =  "have_kids", total_population =  "TotaalAantalPersonenInHuishoudens_1", agent_df =  agents, list_conditional_var = c("age_group_20", "sex", "migrationbackground") )

## assigning attributes to agents
agents = distr_bin_attr_strat_n_neigh_stats(agent_df = agents, neigh_df = neigh_stats, neigh_ID = "neighb_code", variable=  "havechild", list_var_classes_neigh_df = c("nr_ppl_with_kids", "nr_ppl_without_kids"), list_agent_propens =  c("prop_have_kids"), list_class_names = c(1, 0),  agent_exclude = c("ischild", "hh_single"))

## cross validating with neighborhood and stratified totals
neigh_valid = crossvalid(valid_df = neigh_stats, agent_df = agents, join_var = "neighb_code", list_valid_var = c("nr_ppl_with_kids", "nr_ppl_without_kids"), 
                         agent_var = "havechild", list_agent_attr = c(1, 0) )

strat_valid = crossvalid(valid_df = migrat_stats, agent_df = agents, join_var = c("age_group_20", "sex", "migrationbackground"), list_valid_var =  c("have_kids"), 
                         agent_var = "havechild", list_agent_attr =  c(1, 0) )


agents = agents[,c("agent_ID","neighb_code",  "age" , "sex", "age_group" , "age_group_20", "migrationbackground", "hh_single", "ischild", "havechild", "prop_female" ,"prop_Dutch", "prop_Western","prop_Non_Western", "prop_singlehh", "prop_have_kids")]
write.csv(agents, "Agent_pop.csv")

setwd("C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Population/CBS statistics")
agents = read.csv("Agent_pop.csv")

############################# socioeconomics ################################################
# education level
x = neigh_stats2[,c("OpleidingsniveauLaag_64" , "OpleidingsniveauMiddelbaar_65" ,"OpleidingsniveauHoog_66")]
colnames(neigh_stats2)[5] = "neighb_code"
colnames(neigh_stats2)

## Data Preparation
setwd("C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Population/CBS statistics/socioeconomics")
absolved_edu = read.csv("diplomaabsolvation conditioned by age sex and migrationbackground.csv")
current_edu = read.csv("students conditioned by age sex and migrationbackground.csv")
age_coding = read.csv("age_coding.csv")
edu_coding = read.csv("education_coding.csv")
colnames(age_coding)[1] = "Leeftijd"
colnames(edu_coding)[1:2] = c("Onderwijssoort", "education_level")
absolved_edu = merge(absolved_edu, age_coding, by= "Leeftijd", all.x = T, all.y = F)
current_edu = merge(current_edu, age_coding, by= "Leeftijd", all.x = T, all.y = F)
absolved_edu = merge(absolved_edu, edu_coding, by= "Onderwijssoort", all.x = T, all.y = F)
current_edu = merge(current_edu, edu_coding, by= "Onderwijssoort", all.x = T, all.y = F)

current_edu[, c("education_level" , "age" ,  "sex"  , "Migratieachtergrond"  , "LeerlingenDeelnemersStudenten_1")]           
absolved_edu[, c("education_level" , "age" ,  "sex"  , "Migratieachtergrond"  , "Gediplomeerden_1")]  

edu_stats = unique(absolved_edu[, c("age" ,  "sex"  , "Migratieachtergrond")])
for(n in 1:nrow(edu_stats)){
  edu_stats$absolved_high[n] = sum(absolved_edu$Gediplomeerden_1[which(absolved_edu$age == edu_stats$age[n] & absolved_edu$sex == edu_stats$sex[n] & absolved_edu$Migratieachtergrond == edu_stats$Migratieachtergrond[n] & absolved_edu$ranking == "high")])
  edu_stats$absolved_middle[n] = sum(absolved_edu$Gediplomeerden_1[which(absolved_edu$age == edu_stats$age[n] & absolved_edu$sex == edu_stats$sex[n] & absolved_edu$Migratieachtergrond == edu_stats$Migratieachtergrond[n] & absolved_edu$ranking == "middle")])
  edu_stats$absolved_low[n] = sum(absolved_edu$Gediplomeerden_1[which(absolved_edu$age == edu_stats$age[n] & absolved_edu$sex == edu_stats$sex[n] & absolved_edu$Migratieachtergrond == edu_stats$Migratieachtergrond[n] & absolved_edu$ranking == "low")])
  edu_stats$absolved_tot[n] = sum(absolved_edu$Gediplomeerden_1[which(absolved_edu$age == edu_stats$age[n] & absolved_edu$sex == edu_stats$sex[n] & absolved_edu$Migratieachtergrond == edu_stats$Migratieachtergrond[n] & absolved_edu$ranking != "")])
  edu_stats$current_high[n] = sum(current_edu$LeerlingenDeelnemersStudenten_1[which(current_edu$age == edu_stats$age[n] & current_edu$sex == edu_stats$sex[n] & current_edu$Migratieachtergrond == edu_stats$Migratieachtergrond[n] & current_edu$ranking == "high")])
  edu_stats$current_middle[n] = sum(current_edu$LeerlingenDeelnemersStudenten_1[which(current_edu$age == edu_stats$age[n] & current_edu$sex == edu_stats$sex[n] & current_edu$Migratieachtergrond == edu_stats$Migratieachtergrond[n] & current_edu$ranking == "middle")])
  edu_stats$current_low[n] = sum(current_edu$LeerlingenDeelnemersStudenten_1[which(current_edu$age == edu_stats$age[n] & current_edu$sex == edu_stats$sex[n] & current_edu$Migratieachtergrond == edu_stats$Migratieachtergrond[n] & current_edu$ranking == "low")])
  edu_stats$current_totalindf[n] = sum(current_edu$LeerlingenDeelnemersStudenten_1[which(current_edu$age == edu_stats$age[n] & current_edu$sex == edu_stats$sex[n] & current_edu$Migratieachtergrond == edu_stats$Migratieachtergrond[n] & current_edu$ranking != "")])
  edu_stats$current_total[n] = nrow(agents[ which(agents$age_group_new  == edu_stats$age[n] & agents$sex == edu_stats$sex[n] & agents$migrationbackground == edu_stats$Migratieachtergrond[n]), ])
  edu_stats$current_no_edu[n] = (edu_stats$current_total[n] - sum(edu_stats$current_low[n], edu_stats$current_middle[n], edu_stats$current_high[n]))
}

edu_stats = edu_stats[edu_stats$age_group_new != "Totaal" & edu_stats$sex != "Total" & edu_stats$migrationbackground != "Total",]
colnames(edu_stats)[1:3] = c("age_group_new", "sex", "migrationbackground")

agents$age_group_new = agents$age
agents$age_group_new[agents$age %in% 30:34] = "30 tot 35 jaar"
agents$age_group_new[agents$age %in% 35:39] = "35 tot 40 jaar"
agents$age_group_new[agents$age %in% 40:44] = "40 tot 45 jaar" 
agents$age_group_new[agents$age %in% 45:49] = "45 tot 50 jaar" 
agents$age_group_new[agents$age >= 50] = "50 jaar of ouder"  


neigh_stats2[,c("OpleidingsniveauLaag_64")] = as.numeric(neigh_stats2[,c("OpleidingsniveauLaag_64")])
neigh_stats2[,c("OpleidingsniveauMiddelbaar_65" )] = as.numeric(neigh_stats2[,c("OpleidingsniveauMiddelbaar_65" )])
neigh_stats2[,c("OpleidingsniveauHoog_66")] = as.numeric(neigh_stats2[,c("OpleidingsniveauHoog_66")])


## Conditional Propensities
agents = calc_propens_agents(dataframe =  edu_stats, variable = "absolved_high", total_population =  "absolved_tot", agent_df =  agents, list_conditional_var = c("age_group_new", "sex", "migrationbackground") )
agents = calc_propens_agents(dataframe =  edu_stats, variable = "absolved_middle", total_population =  "absolved_tot", agent_df =  agents, list_conditional_var = c("age_group_new", "sex", "migrationbackground") )
agents = calc_propens_agents(dataframe =  edu_stats, variable = "absolved_low", total_population =  "absolved_tot", agent_df =  agents, list_conditional_var = c("age_group_new", "sex", "migrationbackground") )
agents = calc_propens_agents(dataframe =  edu_stats, variable = "current_high", total_population =  "current_total", agent_df =  agents, list_conditional_var = c("age_group_new", "sex", "migrationbackground") )
agents = calc_propens_agents(dataframe =  edu_stats, variable = "current_middle", total_population =  "current_total", agent_df =  agents, list_conditional_var = c("age_group_new", "sex", "migrationbackground") )
agents = calc_propens_agents(dataframe =  edu_stats, variable = "current_low", total_population =  "current_total", agent_df =  agents, list_conditional_var = c("age_group_new", "sex", "migrationbackground") )
agents = calc_propens_agents(dataframe =  edu_stats, variable = "current_no_edu", total_population =  "current_total", agent_df =  agents, list_conditional_var = c("age_group_new", "sex", "migrationbackground") )


## assigning attributes to agents
agents$current_edu_exclude = 0
agents$current_edu_exclude[which(is.na(agents$prop_current_high))] = 1

agents = distr_attr_cond_prop(agent_df = agents, variable=  "current_education",   list_agent_propens =  c("prop_current_low",  "prop_current_middle", "prop_current_high", "prop_current_no_edu"), 
                              list_class_names = c("low", "middle", "high", "no_current_edu"), agent_exclude = "current_edu_exclude")

agents$current_education[which(agents$age < 15 & agents$age > 5) ] = "low"
agents$current_education[which( agents$age <= 5) ] = "no_current_edu"

agents$absolved = ""
agents$absolved[agents$current_education == "middle"] = "low"
agents$absolved[agents$current_education == "high" & agents$age <= 22] = "middle"
agents$absolved[agents$current_education == "high" & agents$age > 22] = "high"

neigh_stats2$LowerEdu = 0
neigh_stats2$MiddleEdu = 0
neigh_stats2$HigherEdu = 0

for(i in 1:nrow(neigh_stats2)){
  neigh_stats2[i,c("LowerEdu")] = neigh_stats2[i,c("OpleidingsniveauLaag_64")] - nrow(agents[agents$absolved == "low" & agents$neighb_code == neigh_stats2$neighb_code[i] & agents$age >= 15,])
  neigh_stats2[i,c("MiddleEdu" )] = neigh_stats2[i,c("OpleidingsniveauMiddelbaar_65" )]- nrow(agents[agents$absolved == "middle" & agents$neighb_code == neigh_stats2$neighb_code[i] & agents$age >= 15,])
  neigh_stats2[i,c("HigherEdu")] = neigh_stats2[i,c("OpleidingsniveauHoog_66")] - nrow(agents[agents$absolved == "high" & agents$neighb_code == neigh_stats2$neighb_code[i] & agents$age >= 15,])
}


neigh_stats2$LowerEdu[neigh_stats2$LowerEdu < 0] = 0
neigh_stats2$MiddleEdu[neigh_stats2$MiddleEdu < 0] = 0
neigh_stats2$HigherEdu[neigh_stats2$HigherEdu < 0] = 0

neigh_stats2[, c("OpleidingsniveauLaag_64" , "OpleidingsniveauMiddelbaar_65" ,"OpleidingsniveauHoog_66")]
neigh_stats2[, c("LowerEdu" , "MiddleEdu" ,"HigherEdu")]

agents$diplm_exclude = 0
agents$diplm_exclude[which(is.na(agents$prop_absolved_high)| agents$age < 15 | agents$absolved != "") ] = 1

agents = distr_attr_strat_n_neigh_stats_3plus(agent_df = agents, neigh_df = neigh_stats2, neigh_ID = "neighb_code", variable=  "absolved_education", 
                                            list_var_classes_neigh_df = c("LowerEdu" , "MiddleEdu" ,"HigherEdu"), 
                                            list_agent_propens =  c("prop_absolved_low",  "prop_absolved_middle", "prop_absolved_high" ), 
                                            list_class_names = c("low", "middle", "high"),  agent_exclude = c("diplm_exclude"))


agents$absolved_education[agents$absolved != ""] = agents$absolved[agents$absolved != ""]

## cross validating with neighborhood and stratified totals
neigh_valid = crossvalid(valid_df = neigh_stats2, agent_df = agents, join_var = "neighb_code", list_valid_var = c("OpleidingsniveauLaag_64" , "OpleidingsniveauMiddelbaar_65" ,"OpleidingsniveauHoog_66"), 
                         agent_var = "absolved_education", list_agent_attr = c("low", "middle", "high") )

strat_valid = crossvalid(valid_df = edu_stats, agent_df = agents, join_var = c("age_group_new", "sex", "migrationbackground"), list_valid_var =  c("absolved_low", "absolved_middle", "absolved_high"), 
                         agent_var = "absolved_education", list_agent_attr = c("low", "middle", "high") )



colnames(agents)
agents = agents[,c("agent_ID","neighb_code",  "age" , "sex", "age_group" , "age_group_20", "migrationbackground", "hh_single", "ischild", 
                   "havechild", "current_education", "absolved_education", "prop_female" ,"prop_Dutch", "prop_Western","prop_Non_Western",
                   "prop_singlehh", "prop_have_kids",  "prop_absolved_high", "prop_absolved_middle","prop_absolved_low" ,"prop_current_high",   
                   "prop_current_middle", "prop_current_low" ,"prop_current_no_edu" )]

setwd("C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Population/CBS statistics")
write.csv(agents, "Agent_pop_with_prop.csv")

setwd("C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Population")
agents_clean = agents[,c("agent_ID","neighb_code",  "age" , "sex", "age_group" , "age_group_20", "migrationbackground", "hh_single", "ischild", 
                   "havechild", "current_education", "absolved_education" )]
write.csv(agents_clean, "Agent_pop.csv")


# employment
c("NettoArbeidsparticipatie_67" , "PercentageWerknemers_68", "PercentageZelfstandigen_69" )

#income
x = neigh_stats3[,c("AantalInkomensontvangers_67"  , "k_40PersonenMetLaagsteInkomen_70" , "k_20PersonenMetHoogsteInkomen_71",  
                    "k_40HuishoudensMetLaagsteInkomen_73",  "k_20HuishoudensMetHoogsteInkomen_74",  "HuishoudensMetEenLaagInkomen_75",
                    "HuishOnderOfRondSociaalMinimum_76")]

# k_40PersonenMetLaagsteInkomen_70 Share of persons in private households that belong to national 40% people with the lowest personal income.       
# k_20PersonenMetHoogsteInkomen_71 Share of persons in private households that belong to national 20% people with the highest personal income


colnames(neigh_stats2)

setwd("C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Population/CBS statistics/socioeconomics")
income_stats = read.csv("income by gender and age.csv")
personal_attributes = read.csv("personal_attributes.csv")
colnames(personal_attributes)[1] = "Persoonskenmerken"
income_stats = merge(income_stats, personal_attributes, by= "Persoonskenmerken", all.x = T, all.y = F)

personal_attributes
c("Migratieachtergrond: Nederland" , "Migratieachtergrond: westers", "Migratieachtergrond: niet-westers",  "Totaal personen"  , "Leeftijd: 0 tot 15 jaar" ,
  "Leeftijd: 15 tot 25 jaar", "Leeftijd: 25 tot 45 jaar" , "Leeftijd: 45 tot 65 jaar" , "Leeftijd: 65 jaar of ouder", "Positie hh: hoofdkostw. zonder partner",
  "Positie hh: hoofdkostw. met partner" , "Positie hh: hoofdkostwinner", "Positie hh: partner van hoofdkostwinner", "Positie hh: kind < 18 jaar" ,
  "Positie hh: kind >=18 jaar" ,"Positie hh: overig lid"  , "SEC: zelfstandige"  ,"SEC: uitkerings- en pensioenontvanger" , 
  "SEC: ontvanger werkloosheidsuitkering", "SEC: ontvanger van sociale voorziening", "SEC: arbeidsongeschikte", "SEC: overige (zonder inkomen)",
  "SEC: werknemer" , "SEC: uitkeringsontvanger",  "SEC: pensioenontvanger" , "SEC:(school)kind of student"  )  

# in English
c("Migration background: the Netherlands", "migration background: western", "migration background: non-western", "Total persons", "age: 0 to 15 years old",
"Age: 15 to 25 years old", "age: 25 to 45 years old", "age: 45 to 65 years old", "age: 65 years or older", "position HH: main kostw. Without partner",
"HH position: main kostw. With partner", "HH position: main kostwinner", "position HH: partner of main kostwinner", "position HH: child <18 years old",
"Position HH: child> = 18 years", "position HH: other member", "sec: self-employed", "sec: benefit and pension receiver",
"Sec: recipient unemployment benefit", "SEC: Social Provision Recipient", "SEC: Incapacitated", "SEC: Other (without income)",
"SEC: employee", "SEC: Benefit receiver", "SEC: Pension Recipient", "SEC: (School) Child or Student")




calc_propens_agents = function(dataframe, variable, total_population, agent_df, list_conditional_var){
  dataframe[,c(paste("prop_",variable, sep = ""))] = dataframe[,c(variable)]/dataframe[, c(total_population)]
  order_agent_df = colnames(agent_df)
  agent_df = merge(agent_df, dataframe[,c(list_conditional_var, paste("prop_",variable, sep = ""))], all.x = T, all.y= F, by = list_conditional_var)
  agent_df = agent_df[,c(order_agent_df, paste("prop_",variable, sep = ""))]
  random_seq = sample(nrow(agent_df))
  agent_df = agent_df[random_seq,]
  return(agent_df)
}



#social support
c("HuishOnderOfRondSociaalMinimum_79" , "HuishoudensTot110VanSociaalMinimum_80", "HuishoudensTot120VanSociaalMinimum_81" ,"MediaanVermogenVanParticuliereHuish_82", 
  "PersonenPerSoortUitkeringBijstand_83" , "PersonenPerSoortUitkeringAO_84", "PersonenPerSoortUitkeringWW_85" , "PersonenPerSoortUitkeringAOW_86", "JongerenMetJeugdzorgInNatura_87",
  "PercentageJongerenMetJeugdzorg_88")


################### Health ###################################
setwd("C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Population/CBS statistics/Health")
neigh_health = read.csv("Gezondheid_per_wijk_en_buurt_2016_09062021_151732.csv")
colnames(neigh_health)
neigh_health = neigh_health[which(neigh_health$Soort.Regio == "Buurt"),]


c("ï..Wijken.en.buurten", "Gemeentenaam" ,"Soort.Regio",   "neighb_code", "Drankgebruik.Voldoet.aan.alcoholrichtlijn" , "Overgewicht.Obesitas",
  "Roker" , "Lichamelijke.gezondheid.Langdurige.ziekte.of.aandoening", "Psychische.gezondheid.Hoog.risico.op.angst.of.depressie",
  "Eenzaamheid.Ernstig.zeer.ernstig.eenzaam",   "Goed.zeer.goed.ervaren.gezondheid",  "Sporten.en.bewegen.Voldoet.aan.beweegrichtlijn",
  "Mantelzorg.Mantelzorger"  , "Mantelzorg.Mantelzorg.ontvangen.nu..65.." )

# percentage of people 19 years or older  
# (1)Drankgebruik.Voldoet.aan.alcoholrichtlijn = people adhering to alcohol guideline (0-1 glas of alcohol per day)
# (2) Overgewicht.Obesitas = people met een BMI van 30,0 kg/m2 en hoger
# (3) Roker = Smoker

neigh_health[,c( "neighb_code", "Drankgebruik.Voldoet.aan.alcoholrichtlijn" , "Overgewicht.Obesitas", "Roker")]


obesity_stats = read.csv("table__83021NED.csv")
obesity_stats= obesity_stats[which(obesity_stats$Marges == "Waarde"),]
colnames(obesity_stats)[4:8] = c("Underweight" , "Normal_weight", "Overweight" , "Moderate_Overweight", "Obese")

x = c("Underweight" , "Normal_weight", "Overweight" , "Moderate_Overweight", "Obese")
for (i in x){
  obesity_stats[,x] = gsub(",", ".", obesity_stats[,x])
  
}

# 1. Ondergewicht: BMI < 18,5
# 2. Normaal gewicht: BMI >= 18,5 en < 25,0
# 3. Overgewicht: BMI >= 25,0
# a. Matig overgewicht: BMI >= 25,0 en < 30,0
# b. Ernstig overgewicht: BMI >= 30,0

unique(obesity_stats$Kenmerken.personen)
c("Geslacht: Mannen", "Geslacht: Vrouwen", "Leeftijd: 0 tot 4 jaar", "Leeftijd: 4 tot 12 jaar"  , "Leeftijd: 12 tot 16 jaar"  ,
  "Leeftijd: 16 tot 20 jaar" , "Leeftijd: 20 tot 30 jaar" , "Leeftijd: 30 tot 40 jaar" , "Leeftijd: 40 tot 50 jaar" , "Leeftijd: 50 tot 55 jaar",
  "Leeftijd: 55 tot 65 jaar"    , "Leeftijd: 65 tot 75 jaar"  ,  "Leeftijd: 75 jaar of ouder",  "Leeftijd: 0 tot 12 jaar" ,  "Leeftijd: 12 tot 18 jaar",
  "Leeftijd: 18 jaar of ouder"  , "Positie: alleenstaande <40 jaar" ,  "Positie: alleenstaande 40 tot 65 jaar" , "Positie: alleenstaande >=65 jaar" ,
  "Positie: kind <18 jaar, eenoudergezin",  "Positie: kind >= 18 jaar eenoudergezin", "Positie: kind <18 jaar bij paar"  , "Positie: kind >=18 jaar bij paar" ,
 "Positie: ouder in eenoudergezin" , "Positie: partner in paar met kind" , "Positie: partner paar <40, geen kind", "Positie: partner paar 40-65, geen kind",
 "Positie: partner paar >=65, geen kind", "Positie: overig lid" , "Migratieachtergrond: Nederland" , "Migratieachtergrond: westers" ,
 "Migratieachtergrond: 1e gen westers", "Migratieachtergrond: 2e gen westers")


x = list(c("Geslacht: Mannen", "Geslacht: Vrouwen"),c("Leeftijd: 0 tot 4 jaar", "Leeftijd: 4 tot 12 jaar"  , "Leeftijd: 12 tot 16 jaar"  ,
  "Leeftijd: 16 tot 20 jaar" , "Leeftijd: 20 tot 30 jaar" , "Leeftijd: 30 tot 40 jaar" , "Leeftijd: 40 tot 50 jaar" , "Leeftijd: 50 tot 55 jaar",
  "Leeftijd: 55 tot 65 jaar"    , "Leeftijd: 65 tot 75 jaar"  ,  "Leeftijd: 75 jaar of ouder",  "Leeftijd: 0 tot 12 jaar" ,  "Leeftijd: 12 tot 18 jaar",
  "Leeftijd: 18 jaar of ouder"))

length(x[[2]])

x = list(c("Geslacht: Mannen", "Geslacht: Vrouwen"),c("Leeftijd: 0 tot 4 jaar", "Leeftijd: 4 tot 12 jaar"  , "Leeftijd: 12 tot 16 jaar"  ,
                                                      "Leeftijd: 16 tot 20 jaar" , "Leeftijd: 20 tot 30 jaar" , "Leeftijd: 30 tot 40 jaar" , "Leeftijd: 40 tot 50 jaar" , "Leeftijd: 50 tot 55 jaar",
                                                      "Leeftijd: 55 tot 65 jaar"    , "Leeftijd: 65 tot 75 jaar"  ,  "Leeftijd: 75 jaar of ouder",  "Leeftijd: 0 tot 12 jaar" ,  "Leeftijd: 12 tot 18 jaar",
                                                      "Leeftijd: 18 jaar of ouder"))





create_stratified_prob_table = function(nested_cond_attr_list, column_names, orig_df, strat_var, var_for_pred){
  ncondVar = length(nested_cond_attr_list)
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
  colnames(new_strat_df) = c(column_names, var_for_pred)
  for(i in 1:nrow(new_strat_df)){
    for(n in 1:length(var_for_pred)){
      new_strat_df[i,n+ncondVar] = sum(orig_df[which(orig_df[,c(strat_var)] %in% c(new_strat_df[i,1:ncondVar])),c(var_for_pred[n])])/ncondVar
    }
  }
  
  return(new_strat_df)
}

sum(obesity_stats[which(obesity_stats[,c("Kenmerken.personen")] %in% c(BMI_stats[2,1:2])),c("Underweight")])

as.numeric(obesity_stats[which(obesity_stats[,c("Kenmerken.personen")] %in% c(BMI_stats[2,1:2])),c("Underweight")])


obesity_stats[,c("Kenmerken.personen")]

BMI_stats = create_stratified_prob_table(nested_cond_attr_list = list(c("Geslacht: Mannen", "Geslacht: Vrouwen"),c("Leeftijd: 0 tot 4 jaar", "Leeftijd: 4 tot 12 jaar"  , "Leeftijd: 12 tot 16 jaar"  ,
                                                                                                                  "Leeftijd: 16 tot 20 jaar" , "Leeftijd: 20 tot 30 jaar" , "Leeftijd: 30 tot 40 jaar" , "Leeftijd: 40 tot 50 jaar" , "Leeftijd: 50 tot 55 jaar",
                                                                                                                  "Leeftijd: 55 tot 65 jaar"    , "Leeftijd: 65 tot 75 jaar"  ,  "Leeftijd: 75 jaar of ouder",  "Leeftijd: 0 tot 12 jaar" ,  "Leeftijd: 12 tot 18 jaar",
                                                                                                                  "Leeftijd: 18 jaar of ouder")),
                                         column_names = c("sex", "age_group"), var_for_pred = c("Underweight" , "Normal_weight", "Overweight" , "Moderate_Overweight", "Obese"),
                                         orig_df = obesity_stats, strat_var = "Kenmerken.personen")




######################## car ownership ##############################
c("PersonenautoSTotaal_99", "PersonenautoSBrandstofBenzine_100" , "PersonenautoSOverigeBrandstof_101", "PersonenautoSPerHuishouden_102" , "PersonenautoSNaarOppervlakte_103" , "Motorfietsen_104" )





agents$agent_ID = paste("Agent_",1:tot_pop, sep="")

write.csv(agents, "Agent_pop.csv")
