
## this script generates a set of agents based on statistical data that is 
# representative for a population of a city and can be used for simulation purposes, such as an agent-based model.


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
          if(length(which(agent_df[x, c(variable)] == list_class_names[1])) >= tot__var_class_neigh[1] & length(which(agent_df[x, c(variable)] == list_class_names[2])) >= tot__var_class_neigh[2] & length(which(agent_df[x, c(variable)] == list_class_names[3])) >= tot__var_class_neigh[3]){
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
              percent_diff = append(percent_diff, length(which(agent_df[x, c(variable)] == list_class_names[n]))/as.numeric(tot__var_class_neigh[n]))
            }
            percent_diff_diff = as.data.frame(matrix(data = NA, nrow = length(list_var_classes_neigh_df), ncol = length(list_var_classes_neigh_df)))
            for(n in 1:(lvar)){
              for(k in 1:(lvar)){
                percent_diff_diff[n, k] = percent_diff[n] - percent_diff[k]
              }
            }
            if(all(abs(percent_diff_diff) < 0.03)){
              fitness = 1
            }
            else{
              for(n in 1:(lvar)){
                m = which(percent_diff_diff[n,] < (-0.03))
                abs_diff = as.numeric(((sum(as.numeric(abs(percent_diff_diff[n, m])))/length(m)) * as.numeric(tot__var_class_neigh[n])))/3
                if(length(m)> 0){
                  for(l in m){
                    class = which(agent_df[x, c(variable)] %in% list_class_names[l])[1:as.integer(abs_diff*(as.numeric(tot__var_class_neigh[l])/sum(as.numeric(tot__var_class_neigh[m]))))]
                    class = class[!is.na(class)]
                    agent_df[x[class], c(list_agent_propens[n])] = agent_df[x[class], c(list_agent_propens[n])] + 0.3
                    agent_df[x[class], c(list_agent_propens[m])] = agent_df[x[class], c(list_agent_propens[m])] - (0.3/length(m))
                  }
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
popstats = read.csv("Neighborhood statistics 2020.csv") ## count of people per age group per neighborhood
popstats[is.na(popstats)] = 0
neigh_stats = popstats[which(popstats$SoortRegio_2 == "Buurt     "),]
popstats2 = read.csv("Neighborhood statistics 2018.csv") ## count of people per age group per neighborhood
wijk_stats = popstats[which(popstats$SoortRegio_2 == "Wijk      "),]

sexstats = read.csv("Amsterdam_tot_sex_gender2020.csv") # count of people per lifeyear and gender in all of Amsterdam
sexstats$totpop = sexstats$male + sexstats$female
agents = read.csv("Agent_pop.csv") ## count of people per age group per neighborhood


#### Interesting variables in neighborhood dataset

###################
## Demographics ###
###################
neigh_stats[,c( "k_0Tot15Jaar", "k_15Tot25Jaar" , "k_25Tot45Jaar", "k_45Tot65Jaar", "k_65JaarOfOuder", 
                "Mannen_6", "Vrouwen_7", "WestersTotaal_17", "NietWestersTotaal_18" )]

#also interesting to account for demographic change and birth rate in future
neigh_stats[,c("GeboorteTotaal_24", "GeboorteRelatief_25" , "SterfteTotaal_26" , "SterfteRelatief_27")]

############################
## Household Composition ###
############################

neigh_stats[,c( "HuishoudensTotaal_28", "Eenpersoonshuishoudens_29" , 
"HuishoudensZonderKinderen_30", "HuishoudensMetKinderen_31" , "GemiddeldeHuishoudensgrootte_32")]

####################
## Socioeconomics ##
####################

# education level
neigh_stats[,c("OpleidingsniveauLaag_64" , "OpleidingsniveauMiddelbaar_65" ,"OpleidingsniveauHoog_66")]

# employment
neigh_stats[,c("NettoArbeidsparticipatie_67" , "PercentageWerknemers_68", "PercentageZelfstandigen_69" )]
#income
neigh_stats[,c("AantalInkomensontvangers_70" , "GemiddeldInkomenPerInkomensontvanger_71" , "GemiddeldInkomenPerInwoner_72", "k_40PersonenMetLaagsteInkomen_73" , "k_20PersonenMetHoogsteInkomen_74", 
               "GemGestandaardiseerdInkomenVanHuish_75" , "k_40HuishoudensMetLaagsteInkomen_76",  "k_20HuishoudensMetHoogsteInkomen_77",  "HuishoudensMetEenLaagInkomen_78")]

#social support
neigh_stats[, c("HuishOnderOfRondSociaalMinimum_79" , "HuishoudensTot110VanSociaalMinimum_80", "HuishoudensTot120VanSociaalMinimum_81" ,"MediaanVermogenVanParticuliereHuish_82", 
  "PersonenPerSoortUitkeringBijstand_83" , "PersonenPerSoortUitkeringAO_84", "PersonenPerSoortUitkeringWW_85" , "PersonenPerSoortUitkeringAOW_86", "JongerenMetJeugdzorgInNatura_87",
  "PercentageJongerenMetJeugdzorg_88")]





################################## determining size of agent population ###################################
## Amsterdam official total population
#2021 872497
#2020 872757
#2018 854047

# CBS neighborhood summary statistics dataset 2020
## CBS must have made a mistake, probably with the age grouping, because the total is larger than the general population. 
sum(neigh_stats[,10:14]) # 875920 tot when summarizing age groups per neighborhood
sum(neigh_stats[,8:9]) #870535 tot when summarizing sex per neighborhood
sum(neigh_stats[,7]) # 871395 tot when summarizing tot pop per neighborhood
sum(wijk_stats[,10:14]) # 873165 tot  when summarizing age groups per district
sum(wijk_stats[,8:9]) # 871955 tot when summarizing sex ¨per district
sum(wijk_stats[,7]) # 872165 when summarizing tot pop per district

# testing if excess population when summarizing age groups could be due to double counting of edge ages of age classes (eg. 15 counted as part of 0-15 and 5-25)
sum(sexstats$totpop[sexstats$ï..age == 15], sexstats$totpop[sexstats$ï..age == 25], sexstats$totpop[sexstats$ï..age == 45], sexstats$totpop[sexstats$ï..age == 65])
#However, the sum of these edge ages is 44941, which is way larger than the excess population

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


#only age
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

agents = agents[which(agents$age != ""),]

random_seq = sample(nrow(agents))
agents = agents[random_seq,]


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
migrat_stats = read.csv("age gender migrationbackground familie position.csv")
migrat_stats = migrat_stats[which(migrat_stats$Generatie == "T001040"),]
migrat_age = read.csv("agegroup coding_migration data.csv")
colnames(migrat_age) = c("Leeftijd", "age")
migrat_stats = merge(migrat_stats, migrat_age, all.x = T, all.y = F, by = "Leeftijd")
migrat_stats = migrat_stats[, c("age", "Geslacht" , "Migratieachtergrond" , "Perioden",  "TotaalAantalPersonenInHuishoudens_1" , "ThuiswonendKind_2" , "Alleenstaand_3" , "TotaalSamenwonendePersonen_4" ,  "PartnerInNietGehuwdPaarZonderKi_5" ,
                                "PartnerInGehuwdPaarZonderKinderen_6" , "PartnerInNietGehuwdPaarMetKinderen_7",  "PartnerInGehuwdPaarMetKinderen_8",    "OuderInEenouderhuishouden_9" , "OverigLidHuishouden_10" , "PersonenInInstitutioneleHuishoudens_11" )]

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

############################# socioeconomics ################################################
# education level
neigh_stats[,c("OpleidingsniveauLaag_64" , "OpleidingsniveauMiddelbaar_65" ,"OpleidingsniveauHoog_66")]

## Data Preparation
setwd("C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Population/CBS statistics/socioeconomics")
absolved_edu = read.csv("diplomaabsolvation conditioned by age sex and migrationbackground.csv")
current_edu = read.csv("students conditioned by age sex and migrationbackground.csv")
age_coding = read.csv("age_coding.csv")
edu_coding = read.csv("education_coding.csv")
colnames(age_coding)[1] = "Leeftijd"
colnames(edu_coding)[1] = "Onderwijssoort"
absolved_edu = merge(absolved_edu, age_coding, by= "Leeftijd", all.x = T, all.y = F)
current_edu = merge(current_edu, age_coding, by= "Leeftijd", all.x = T, all.y = F)
absolved_edu = merge(absolved_edu, edu_coding, by= "Onderwijssoort", all.x = T, all.y = F)
current_edu = merge(current_edu, edu_coding, by= "Onderwijssoort", all.x = T, all.y = F)





# employment
c("NettoArbeidsparticipatie_67" , "PercentageWerknemers_68", "PercentageZelfstandigen_69" )
#income
neigh_stats[,c("AantalInkomensontvangers_70" , "GemiddeldInkomenPerInkomensontvanger_71" , "GemiddeldInkomenPerInwoner_72", "k_40PersonenMetLaagsteInkomen_73" , "k_20PersonenMetHoogsteInkomen_74", 
 "GemGestandaardiseerdInkomenVanHuish_75" , "k_40HuishoudensMetLaagsteInkomen_76",  "k_20HuishoudensMetHoogsteInkomen_77",  "HuishoudensMetEenLaagInkomen_78")]

setwd("C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Population/CBS statistics/socioeconomics")
income_stats = read.csv("income by gender and age.csv")
personal_attributes = read.csv("personal_attributes.csv")
colnames(personal_attributes)[1] = "Persoonskenmerken"
income_stats = merge(income_stats, personal_attributes, by= "Persoonskenmerken", all.x = T, all.y = F)


#social support
c("HuishOnderOfRondSociaalMinimum_79" , "HuishoudensTot110VanSociaalMinimum_80", "HuishoudensTot120VanSociaalMinimum_81" ,"MediaanVermogenVanParticuliereHuish_82", 
  "PersonenPerSoortUitkeringBijstand_83" , "PersonenPerSoortUitkeringAO_84", "PersonenPerSoortUitkeringWW_85" , "PersonenPerSoortUitkeringAOW_86", "JongerenMetJeugdzorgInNatura_87",
  "PercentageJongerenMetJeugdzorg_88")


################### Health ###################################
setwd("C:/Dokumente/PhD EXPANSE/Data/Amsterdam/Population/CBS statistics/Health")
neigh_health = read.csv("Gezondheid_per_wijk_en_buurt_2016_09062021_151732.csv")
colnames(neigh_health)

c("ï..Wijken.en.buurten", "Gemeentenaam" ,"Soort.Regio",   "neighb_code", "Drankgebruik.Voldoet.aan.alcoholrichtlijn" , "Overgewicht.Obesitas",
  "Roker" , "Lichamelijke.gezondheid.Langdurige.ziekte.of.aandoening", "Psychische.gezondheid.Hoog.risico.op.angst.of.depressie",
  "Eenzaamheid.Ernstig.zeer.ernstig.eenzaam",   "Goed.zeer.goed.ervaren.gezondheid",  "Sporten.en.bewegen.Voldoet.aan.beweegrichtlijn",
  "Mantelzorg.Mantelzorger"  , "Mantelzorg.Mantelzorg.ontvangen.nu..65.." )



######################## car ownership ##############################
c("PersonenautoSTotaal_99", "PersonenautoSBrandstofBenzine_100" , "PersonenautoSOverigeBrandstof_101", "PersonenautoSPerHuishouden_102" , "PersonenautoSNaarOppervlakte_103" , "Motorfietsen_104" )

  

##########################checking descriptive stats for representativeness################################
agents = agents[which(agents$age != ""),]
summary(as.numeric(agents$age))
plot(density(as.numeric(agents$age)))
summary(as.factor(agents$sex))


random_seq = sample(nrow(agents))
agents = agents[random_seq,]

agents$agent_ID = paste("Agent_",1:tot_pop, sep="")


write.csv(agents, "Agent_pop.csv")
