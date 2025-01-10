pkgs = c("lubridate", "tidyverse")
# sapply(pkgs, install.packages, character.only = T) #install packages if necessary
sapply(pkgs, require, character.only = T) #load 


setwd("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Harmonised European Time Use Survey - Eurostat")

ageTU = read.csv("NL TU_age.csv") # time use per age
act_codes = read.csv("activity_coding_abbr.csv")


agegroups <- unique(ageTU$age)
activities <- unique(ageTU$acl00)

activ_df <- as.data.frame(unique(ageTU$acl00))
colnames(activ_df) =  "act_code"
colnames(act_codes) = c("act_code", "name")

act_code_join = merge(activ_df, act_codes, by = "act_code", all.x = T, all.y = F)

unique(ageTU$unit) #"PTP_RT"   "PTP_TIME" "TIME_SP" 
# 
# Time spent: mean time spent on the activities by all individuals;
# Participation time: mean time spent in the activities by those individuals who took part in the activity; and
# Participation rate: the proportion of the individuals that spent some time doing the activities.



age_sex_act_TIME_SP = data.frame(matrix(nrow = (length(agegroups)*2), ncol = (length(activities)+2)))
age_sex_act_PTP_RT = data.frame(matrix(nrow = (length(agegroups)*2), ncol = (length(activities)+2)))
age_sex_act_PTP_TIME = data.frame(matrix(nrow = (length(agegroups)*2), ncol = (length(activities)+2)))

age_sex_act_TIME_SP[, 1] = c(agegroups, agegroups)
age_sex_act_TIME_SP[1:7, 2] = "F"
age_sex_act_TIME_SP[8:14, 2] = "M"
colnames(age_sex_act_TIME_SP) = c("agegroups", "sex", activities)
for (i in 0:1){ #sex
  for (x in 1:length(agegroups)){ #agegroup
    for (a in 1:length(activities)){ #activities
      age_sex_act_TIME_SP[(i*7)+x, a+2] = ageTU$time_X2010[which(ageTU$unit == "TIME_SP" & ageTU$s == age_sex_act_TIME_SP$sex[i*7 +1] & ageTU$age == agegroups[x] & ageTU$acl00 == activities[a] )]
    }
  }
}


age_sex_act_PTP_RT[, 1] = c(agegroups, agegroups)
age_sex_act_PTP_RT[1:7, 2] = "F"
age_sex_act_PTP_RT[8:14, 2] = "M"
colnames(age_sex_act_PTP_RT) = c("agegroups", "sex", activities)
for (i in 0:1){ #sex
  for (x in 1:length(agegroups)){ #agegroup
    for (a in 1:length(activities)){ #activities
      age_sex_act_PTP_RT[(i*7)+x, a+2] = ageTU$time_X2010[which(ageTU$unit == "PTP_RT" & ageTU$s == age_sex_act_PTP_RT$sex[i*7 +1] & ageTU$age == agegroups[x] & ageTU$acl00 == activities[a] )]
    }
  }
}


age_sex_act_PTP_TIME[, 1] = c(agegroups, agegroups)
age_sex_act_PTP_TIME[1:7, 2] = "F"
age_sex_act_PTP_TIME[8:14, 2] = "M"
colnames(age_sex_act_PTP_TIME) = c("agegroups", "sex", activities)
for (i in 0:1){ #sex
  for (x in 1:length(agegroups)){ #agegroup
    for (a in 1:length(activities)){ #activities
      age_sex_act_PTP_TIME[(i*7)+x, a+2] = ageTU$time_X2010[which(ageTU$unit == "PTP_TIME" & ageTU$s == age_sex_act_PTP_TIME$sex[i*7 +1] & ageTU$age == agegroups[x] & ageTU$acl00 == activities[a] )]
    }
  }
}

eduTU = read.csv("tus_00educ.csv")
educationlevels = unique(eduTU$isced97)
activities <- unique(eduTU$acl00)
colnames(eduTU)[3] = "edu"
eduTU = eduTU[eduTU$geo == "DE",]

edu_sex_act_TIME_SP = data.frame(matrix(nrow = (length(educationlevels)*2), ncol = (length(activities)+2)))
edu_sex_act_PTP_RT = data.frame(matrix(nrow = (length(educationlevels)*2), ncol = (length(activities)+2)))
edu_sex_act_PTP_TIME = data.frame(matrix(nrow = (length(educationlevels)*2), ncol = (length(activities)+2)))

edu_sex_act_TIME_SP[, 1] = c(educationlevels, educationlevels)
edu_sex_act_TIME_SP[1:6, 2] = "F"
edu_sex_act_TIME_SP[7:12, 2] = "M"
colnames(edu_sex_act_TIME_SP) = c("education", "sex", activities)
for (i in 0:1){ #sex
  for (x in 1:length(educationlevels)){ #edugroup
    for (a in 1:length(activities)){ #activities
      edu_sex_act_TIME_SP[(i*6)+x, a+2] = eduTU$time_X2010[which(eduTU$unit == "TIME_SP" & eduTU$sex == edu_sex_act_TIME_SP$sex[(i*6)+1] & eduTU$edu == educationlevels[x] & eduTU$acl00 == activities[a] )]
    }
  }
}

edu_sex_act_PTP_RT[, 1] = c(educationlevels, educationlevels)
edu_sex_act_PTP_RT[1:6, 2] = "F"
edu_sex_act_PTP_RT[7:12, 2] = "M"
colnames(edu_sex_act_PTP_RT) = c("educationlevels", "sex", activities)
for (i in 0:1){ #sex
  for (x in 1:length(educationlevels)){ #edugroup
    for (a in 1:length(activities)){ #activities
      edu_sex_act_PTP_RT[(i*6)+x, a+2] = eduTU$time_X2010[which(eduTU$unit == "PTP_RT" & eduTU$sex == edu_sex_act_PTP_RT$sex[i*6 +1] & eduTU$edu == educationlevels[x] & eduTU$acl00 == activities[a] )]
    }
  }
}


edu_sex_act_PTP_TIME[, 1] = c(educationlevels, educationlevels)
edu_sex_act_PTP_TIME[1:6, 2] = "F"
edu_sex_act_PTP_TIME[7:12, 2] = "M"
colnames(edu_sex_act_PTP_TIME) = c("educationlevels", "sex", activities)
for (i in 0:1){ #sex
  for (x in 1:length(educationlevels)){ #edugroup
    for (a in 1:length(activities)){ #activities
      edu_sex_act_PTP_TIME[(i*6)+x, a+2] = eduTU$time_X2010[which(eduTU$unit == "PTP_TIME" & eduTU$sex == edu_sex_act_PTP_TIME$sex[i*6 +1] & eduTU$edu == educationlevels[x] & eduTU$acl00 == activities[a] )]
    }
  }
}


hhstatusTU = read.csv("tus_00hhstatus.csv")
hhstatustypes = unique(hhstatusTU$hhstatus)
activities <- unique(hhstatusTU$acl00)
hhstatusTU = hhstatusTU[hhstatusTU$geo == "DE",]

hhstatus_sex_act_TIME_SP = data.frame(matrix(nrow = (length(hhstatustypes)*2), ncol = (length(activities)+2)))
hhstatus_sex_act_PTP_RT = data.frame(matrix(nrow = (length(hhstatustypes)*2), ncol = (length(activities)+2)))
hhstatus_sex_act_PTP_TIME = data.frame(matrix(nrow = (length(hhstatustypes)*2), ncol = (length(activities)+2)))

hhstatus_sex_act_TIME_SP[, 1] = c(hhstatustypes, hhstatustypes)
hhstatus_sex_act_TIME_SP[1:12, 2] = "F"
hhstatus_sex_act_TIME_SP[13:24, 2] = "M"
colnames(hhstatus_sex_act_TIME_SP) = c("hhstatus", "sex", activities)
for (i in 0:1){ #sex
  for (x in 1:length(hhstatustypes)){ #hhstatusgroup
    for (a in 1:length(activities)){ #activities
      hhstatus_sex_act_TIME_SP[(i*12)+x, a+2] = hhstatusTU$time_X2010[which(hhstatusTU$unit == "TIME_SP" & hhstatusTU$sex == hhstatus_sex_act_TIME_SP$sex[(i*12)+1] & hhstatusTU$hhstatus == hhstatustypes[x] & hhstatusTU$acl00 == activities[a] )]
    }
  }
}

hhstatus_sex_act_PTP_RT[, 1] = c(hhstatustypes, hhstatustypes)
hhstatus_sex_act_PTP_RT[1:12, 2] = "F"
hhstatus_sex_act_PTP_RT[12:24, 2] = "M"
colnames(hhstatus_sex_act_PTP_RT) = c("hhstatustypes", "sex", activities)
for (i in 0:1){ #sex
  for (x in 1:length(hhstatustypes)){ #hhstatusgroup
    for (a in 1:length(activities)){ #activities
      hhstatus_sex_act_PTP_RT[(i*12)+x, a+2] = hhstatusTU$time_X2010[which(hhstatusTU$unit == "PTP_RT" & hhstatusTU$s == hhstatus_sex_act_PTP_RT$sex[i*12 +1] & hhstatusTU$hhstatus == hhstatustypes[x] & hhstatusTU$acl00 == activities[a] )]
    }
  }
}


hhstatus_sex_act_PTP_TIME[, 1] = c(hhstatustypes, hhstatustypes)
hhstatus_sex_act_PTP_TIME[1:12, 2] = "F"
hhstatus_sex_act_PTP_TIME[12:24, 2] = "M"
colnames(hhstatus_sex_act_PTP_TIME) = c("hhstatustypes", "sex", activities)
for (i in 0:1){ #sex
  for (x in 1:length(hhstatustypes)){ #hhstatusgroup
    for (a in 1:length(activities)){ #activities
      hhstatus_sex_act_PTP_TIME[(i*12)+x, a+2] = hhstatusTU$time_X2010[which(hhstatusTU$unit == "PTP_TIME" & hhstatusTU$s == hhstatus_sex_act_PTP_TIME$sex[i*12 +1] & hhstatusTU$hhstatus == hhstatustypes[x] & hhstatusTU$acl00 == activities[a] )]
    }
  }
}

profstatusTU = read.csv("tus_00profstat.csv", sep = ";")
activities <- unique(profstatusTU$acl00)
profstatusTU = profstatusTU[profstatusTU$geo == "NL",]
profstatustypes = unique(profstatusTU$wstatus)

profstatus_sex_act_TIME_SP = data.frame(matrix(nrow = (length(profstatustypes)*2), ncol = (length(activities)+2)))
profstatus_sex_act_PTP_RT = data.frame(matrix(nrow = (length(profstatustypes)*2), ncol = (length(activities)+2)))
profstatus_sex_act_PTP_TIME = data.frame(matrix(nrow = (length(profstatustypes)*2), ncol = (length(activities)+2)))

profstatus_sex_act_TIME_SP[, 1] = c(profstatustypes, profstatustypes)
profstatus_sex_act_TIME_SP[1:5, 2] = "F"
profstatus_sex_act_TIME_SP[6:10, 2] = "M"
colnames(profstatus_sex_act_TIME_SP) = c("profstatus", "sex", activities)
for (i in 0:1){ #sex
  for (x in 1:length(profstatustypes)){ #profstatusgroup
    for (a in 1:length(activities)){ #activities
      profstatus_sex_act_TIME_SP[(i*5)+x, a+2] = profstatusTU$time_X2010[which(profstatusTU$unit == "TIME_SP" & profstatusTU$sex == profstatus_sex_act_TIME_SP$sex[(i*5)+1] & profstatusTU$wstatus == profstatustypes[x] & profstatusTU$acl00 == activities[a] )]
    }
  }
}

profstatus_sex_act_PTP_RT[, 1] = c(profstatustypes, profstatustypes)
profstatus_sex_act_PTP_RT[1:5, 2] = "F"
profstatus_sex_act_PTP_RT[6:10, 2] = "M"
colnames(profstatus_sex_act_PTP_RT) = c("profstatus", "sex", activities)
for (i in 0:1){ #sex
  for (x in 1:length(profstatustypes)){ #profstatusgroup
    for (a in 1:length(activities)){ #activities
      profstatus_sex_act_PTP_RT[(i*5)+x, a+2] = profstatusTU$time_X2010[which(profstatusTU$unit == "PTP_RT" & profstatusTU$sex == profstatus_sex_act_PTP_RT$sex[i*5 +1] & profstatusTU$wstatus == profstatustypes[x] & profstatusTU$acl00 == activities[a] )]
    }
  }
}


profstatus_sex_act_PTP_TIME[, 1] = c(profstatustypes, profstatustypes)
profstatus_sex_act_PTP_TIME[1:5, 2] = "F"
profstatus_sex_act_PTP_TIME[6:10, 2] = "M"
colnames(profstatus_sex_act_PTP_TIME) = c("profstatus", "sex", activities)
for (i in 0:1){ #sex
  for (x in 1:length(profstatustypes)){ #profstatusgroup
    for (a in 1:length(activities)){ #activities
      profstatus_sex_act_PTP_TIME[(i*5)+x, a+2] = profstatusTU$time_X2010[which(profstatusTU$unit == "PTP_TIME" & profstatusTU$sex == profstatus_sex_act_PTP_TIME$sex[i*5 +1] & profstatusTU$wstatus == profstatustypes[x] & profstatusTU$acl00 == activities[a] )]
    }
  }
}


activities = c("sleep", "work", "at_study_facility", "eat", "childcare", "social_life", "entertainment", "physical_exercise", "walking_the_dog", "at_home")
corr_activity_codes = c("AC01", "AC1A", "AC21A", "AC02", "AC38A", "AC38B", "AC51A", "AC51B", "AC52", "AC6A", "AC344")
activities_intermediate = c( "sleep", "work", "at_study_facility", "eat", "childcare1", "childcare2", "social_life1", "social_life2","entertainment", "physical_exercise", "walking_the_dog")

## preparing age sex dataset
strat_activ_TU_age = age_sex_act_PTP_TIME[, c("agegroups", "sex", corr_activity_codes)]
colnames(strat_activ_TU_age) = c("agegroups", "sex", activities_intermediate)
write.csv(strat_activ_TU_age, "strat_activ_TU_age.csv")

strat_activ_PTP_RT_age = age_sex_act_PTP_RT[, c("agegroups", "sex", corr_activity_codes)]
colnames(strat_activ_PTP_RT_age) = c("agegroups", "sex", activities_intermediate)
write.csv(strat_activ_PTP_RT_age, "strat_activ_PTP_RT_age.csv")

## preparing edu sex dataset
edu_coding = as.data.frame(unique(edu_sex_act_PTP_TIME$educationlevels))
edu_coding$edu_level = NA
colnames(edu_coding)[1] = "educationlevels"
edu_coding[edu_coding$educationlevels == "ED1", 2] = "low"
edu_coding[edu_coding$educationlevels == "ED2" | edu_coding$educationlevels == "ED3_4", 2] = "middle"
# edu_coding[edu_coding$educationlevels == "ED5A_6" | edu_coding$educationlevels == "ED5B", 2] = "high" # if ED5B not NA
edu_coding[edu_coding$educationlevels == "ED5A_6", 2] = "high"

strat_activ_TU_edu = edu_sex_act_PTP_TIME[, c("educationlevels", "sex", corr_activity_codes)]
colnames(strat_activ_TU_edu) = c("educationlevels", "sex", activities_intermediate)
strat_activ_TU_edu = merge(strat_activ_TU_edu, edu_coding, by = "educationlevels", all.x = T)
strat_activ_TU_edu = strat_activ_TU_edu[, c("educationlevels", "edu_level", "sex", activities_intermediate)]
write.csv(strat_activ_TU_edu, "strat_activ_TU_edu.csv")

strat_activ_PTP_RT_edu = edu_sex_act_PTP_RT[, c("educationlevels", "sex", corr_activity_codes)]
colnames(strat_activ_PTP_RT_edu) = c("educationlevels", "sex", activities_intermediate)
strat_activ_PTP_RT_edu = merge(strat_activ_PTP_RT_edu, edu_coding, by = "educationlevels", all.x = T)
strat_activ_PTP_RT_edu = strat_activ_PTP_RT_edu[, c("educationlevels", "edu_level", "sex", activities_intermediate)]
write.csv(strat_activ_PTP_RT_edu, "strat_activ_PTP_RT_edu.csv")


## preparing profstatus sex dataset
profstatus_coding = as.data.frame(unique(profstatus_sex_act_PTP_TIME$profstatus))
profstatus_coding$prof_status = NA

strat_activ_TU_profstatus = profstatus_sex_act_PTP_TIME[, c("profstatus", "sex", corr_activity_codes)]
colnames(strat_activ_TU_profstatus) = c("profstatus", "sex", activities_intermediate)
strat_activ_TU_profstatus = merge(strat_activ_TU_profstatus, profstatus_coding, by = "profstatus", all.x = T)
strat_activ_TU_profstatus = strat_activ_TU_profstatus[, c("profstatus", "edu_level", "sex", activities_intermediate)]
write.csv(strat_activ_TU_profstatus, "strat_activ_TU_profstatus.csv")


## preparing hhstatus sex dataset
hhstatus_coding = read.csv("hhstatus_coding.csv", sep= ";")
colnames(hhstatus_coding)[1] = "hhstatustypes"

strat_activ_TU_hhstatus = hhstatus_sex_act_PTP_TIME[, c("hhstatustypes", "sex", corr_activity_codes)]
colnames(strat_activ_TU_hhstatus) = c("hhstatustypes", "sex", activities_intermediate)
strat_activ_TU_hhstatus = merge(strat_activ_TU_hhstatus, hhstatus_coding, by = "hhstatustypes", all.x = T)
write.csv(strat_activ_TU_hhstatus, "strat_activ_TU_hhstatus.csv")


strat_activ_PTP_RT_hhstatus = hhstatus_sex_act_PTP_RT[, c("hhstatustypes", "sex", corr_activity_codes)]
colnames(strat_activ_PTP_RT_hhstatus) = c("hhstatustypes", "sex", activities_intermediate)
strat_activ_PTP_RT_hhstatus = merge(strat_activ_PTP_RT_hhstatus, hhstatus_coding, by = "hhstatustypes", all.x = T)
write.csv(strat_activ_PTP_RT_hhstatus, "strat_activ_PTP_RT_hhstatus.csv")


create_stratified_table = function(nested_cond_attr_list, column_names){
  ncondVar = length(column_names)
  attr_length = c()
  for(i in 1:ncondVar){
    attr_length = append(attr_length, length(nested_cond_attr_list[[i]]))
  }
  new_strat_df = as.data.frame(matrix(nrow = prod(attr_length), ncol = (ncondVar)))
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
  colnames(new_strat_df) = c(column_names)
  return(new_strat_df)
}


social_profiles_schedules = create_stratified_table(nested_cond_attr_list = list(c("M", "F"),
                                                                       c("Y15-20", "Y20-24", "Y25-44", "Y45-64", "Y_GE65"),
                                                                       c("low", "middle", "high"), 
                                                                       c("1", "0"), 
                                                                       c("1", "0")),
                                          column_names = c("sex", "age_TU_groups", "absolved_education", "havechild", "hh_single" ))

social_profiles_schedules$age_groups = NA
social_profiles_schedules$age_groups[social_profiles_schedules$age_TU_groups == "Y15-20"| social_profiles_schedules$age_TU_groups == "Y20-24"] = "18-25"
social_profiles_schedules$age_groups[social_profiles_schedules$age_TU_groups == "Y15-20"| social_profiles_schedules$age_TU_groups == "Y20-24"|social_profiles_schedules$age_TU_groups == "Y25-44"] = "18-45"
social_profiles_schedules$age_groups[social_profiles_schedules$age_TU_groups == "Y25-44"] = "25-44"
social_profiles_schedules$age_groups[social_profiles_schedules$age_TU_groups == "Y45-64"] = "45-64"
social_profiles_schedules$age_groups[social_profiles_schedules$age_TU_groups == "Y_GE65"] = "65plus"

social_profiles_schedules[,activities_intermediate]= NA

social_profiles_schedules_TU = social_profiles_schedules

for(i in 1:nrow(social_profiles_schedules_TU)){
  for(x in activities_intermediate){
    age_sexTU = as.POSIXct(strat_activ_TU_age[which(strat_activ_TU_age$agegroups == social_profiles_schedules_TU$age[i] & strat_activ_TU_age$sex == social_profiles_schedules_TU$sex[i] ), c(x)], format = "%H:%M")
    edu_sexTY = mean(as.POSIXct(strat_activ_TU_edu[which(strat_activ_TU_edu$edu_level == social_profiles_schedules_TU$absolved_education[i] & strat_activ_TU_edu$sex == social_profiles_schedules_TU$sex[i] ), c(x)], format = "%H:%M"))
    if(social_profiles_schedules_TU$havechild[i] == 1){
      has_childTU = mean(as.POSIXct(strat_activ_TU_hhstatus[which(strat_activ_TU_hhstatus$has_child == social_profiles_schedules_TU$havechild[i] & strat_activ_TU_hhstatus$single_hh == social_profiles_schedules_TU$hh_single[i] &  strat_activ_TU_hhstatus$sex == social_profiles_schedules_TU$sex[i]), c(x)], format = "%H:%M"))
      hh_sex_ageTU = mean(as.POSIXct(strat_activ_TU_hhstatus[which(strat_activ_TU_hhstatus$single_hh == social_profiles_schedules_TU$hh_single[i] &  strat_activ_TU_hhstatus$sex == social_profiles_schedules_TU$sex[i] & strat_activ_TU_hhstatus$age == social_profiles_schedules$age_groups[i]), c(x)], format = "%H:%M"))
      social_profiles_schedules_TU[i, c(x)] = format(mean(c(age_sexTU, edu_sexTY, hh_sex_ageTU, has_childTU)), format='%H:%M')
    }
    else{
      hh_sex_ageTU = mean(as.POSIXct(strat_activ_TU_hhstatus[which(strat_activ_TU_hhstatus$has_child == social_profiles_schedules_TU$havechild[i] & strat_activ_TU_hhstatus$single_hh == social_profiles_schedules_TU$hh_single[i] &  strat_activ_TU_hhstatus$sex == social_profiles_schedules_TU$sex[i] & strat_activ_TU_hhstatus$age == social_profiles_schedules_TU$age_groups[i]), c(x)], format = "%H:%M"))
      social_profiles_schedules_TU[i, c(x)] = format(mean(c(age_sexTU, edu_sexTY, hh_sex_ageTU)), format='%H:%M')
    }
  }
}

social_profiles_schedules_TU = social_profiles_schedules_TU[!is.na(social_profiles_schedules_TU$sleep),]



social_profiles_schedules_PTP_RT = social_profiles_schedules

for(i in 1:nrow(social_profiles_schedules_PTP_RT)){
  for(x in activities_intermediate){
    age_sexTU = as.numeric(strat_activ_PTP_RT_age[which(strat_activ_PTP_RT_age$agegroups == social_profiles_schedules_PTP_RT$age[i] & strat_activ_PTP_RT_age$sex == social_profiles_schedules_PTP_RT$sex[i] ), c(x)])
    edu_sexTY = mean(as.numeric(strat_activ_PTP_RT_edu[which(strat_activ_PTP_RT_edu$edu_level == social_profiles_schedules_PTP_RT$absolved_education[i] & strat_activ_PTP_RT_edu$sex == social_profiles_schedules_PTP_RT$sex[i] ), c(x)]))
    if(social_profiles_schedules_PTP_RT$havechild[i] == 1){
      has_childTU = mean(as.numeric(strat_activ_PTP_RT_hhstatus[which(strat_activ_PTP_RT_hhstatus$has_child == social_profiles_schedules_PTP_RT$havechild[i] & strat_activ_PTP_RT_hhstatus$single_hh == social_profiles_schedules_PTP_RT$hh_single[i] &  strat_activ_PTP_RT_hhstatus$sex == social_profiles_schedules_PTP_RT$sex[i]), c(x)]))
      hh_sex_ageTU = mean(as.numeric(strat_activ_PTP_RT_hhstatus[which(strat_activ_PTP_RT_hhstatus$single_hh == social_profiles_schedules_PTP_RT$hh_single[i] &  strat_activ_PTP_RT_hhstatus$sex == social_profiles_schedules_PTP_RT$sex[i] & strat_activ_PTP_RT_hhstatus$age == social_profiles_schedules$age_groups[i]), c(x)]))
      social_profiles_schedules_PTP_RT[i, c(x)] = (mean(c(age_sexTU, edu_sexTY, hh_sex_ageTU, has_childTU))/100)
    }
    else{
      hh_sex_ageTU = mean(as.numeric(strat_activ_PTP_RT_hhstatus[which(strat_activ_PTP_RT_hhstatus$has_child == social_profiles_schedules_PTP_RT$havechild[i] & strat_activ_PTP_RT_hhstatus$single_hh == social_profiles_schedules_PTP_RT$hh_single[i] &  strat_activ_PTP_RT_hhstatus$sex == social_profiles_schedules_PTP_RT$sex[i] & strat_activ_PTP_RT_hhstatus$age == social_profiles_schedules_PTP_RT$age_groups[i]), c(x)]))
      social_profiles_schedules_PTP_RT[i, c(x)] = (mean(c(age_sexTU, edu_sexTY, hh_sex_ageTU))/100)
    }
  }
}

social_profiles_schedules_PTP_RT = social_profiles_schedules_PTP_RT[!is.na(social_profiles_schedules_PTP_RT$sleep),]


setwd("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population")
agents_clean = read.csv("Agent_pop.csv")

agents_clean$age_TU_groups = NA
agents_clean$age_TU_groups[agents_clean$age < 20 & agents_clean$age >=15] = "Y15-20"
agents_clean$age_TU_groups[agents_clean$age < 25 & agents_clean$age >=20] = "Y20-24"
agents_clean$age_TU_groups[agents_clean$age < 45 & agents_clean$age >=25] = "Y25-44"
agents_clean$age_TU_groups[agents_clean$age < 65 & agents_clean$age >=45] = "Y45-64"
agents_clean$age_TU_groups[ agents_clean$age >=65] = "Y_GE65"

social_profiles_schedules_PTP_RT$sex[social_profiles_schedules_PTP_RT$sex == "M"] = "male"
social_profiles_schedules_PTP_RT$sex[social_profiles_schedules_PTP_RT$sex == "F"] = "female"

social_profiles_schedules_TU$sex[social_profiles_schedules_TU$sex == "M"] = "male"
social_profiles_schedules_TU$sex[social_profiles_schedules_TU$sex == "F"] = "female"

agents_withschedules = merge(agents_clean, social_profiles_schedules_PTP_RT[, c("sex", "age_TU_groups", "absolved_education", "havechild", "hh_single", activities_intermediate )], by = c("sex", "age_TU_groups", "absolved_education", "havechild", "hh_single"), all.x = T, all.y = F)
agents_withschedules = merge(agents_withschedules, social_profiles_schedules_TU[, c("sex", "age_TU_groups", "absolved_education", "havechild", "hh_single", activities_intermediate )], by = c("sex", "age_TU_groups", "absolved_education", "havechild", "hh_single"), all.x = T, all.y = F)


for(i in activities_intermediate){
  agents_withschedules[, c("random_scores")] = sample(x= seq(from= 0, to = 1, by= 0.01), size = nrow(agents_withschedules), replace = T)
  agents_withschedules[, c(paste(i, "_time", sep = ""))] = NA
  agents_withschedules[which(agents_withschedules[, c("random_scores")] <= agents_withschedules[, c(paste(i,".x", sep="") )]), c(paste(i, "_time", sep = ""))] = agents_withschedules[which(agents_withschedules[, c("random_scores")] <= agents_withschedules[, c(paste(i,".x", sep="") )]), c(paste(i,".y", sep="") )]
  agents_withschedules[which(agents_withschedules[, c("random_scores")] > agents_withschedules[, c(paste(i,".x", sep="") )]), c(paste(i, "_time", sep = ""))] = NA
}

agents_withschedules = agents_withschedules[, c("agent_ID","neighb_code",  "age" , "sex", "age_group" , "age_group_20", "migrationbackground", "hh_single", "ischild", 
                                                "havechild", "current_education", "absolved_education", "BMI", paste(activities_intermediate, "_time", sep = ""))]

random_seq = sample(nrow(agents_withschedules))
agents_withschedules = agents_withschedules[random_seq,]


activities_intermediate

schedules <- as.data.frame(matrix(nrow = (24*6), ncol = 1))

schedules[((8*6)+3):(15*6), 1] = "school"
schedules[c((0):(7*6), (22*6):(24*6)), 1] = "sleeping"
schedules[c(((7*6)+1):((8*6) +2), (19*6):((22*6)-1)), 1] = "at_Home"
schedules[c(((15*6)+1):((19*6) -1)), 1] = "social_life"
colnames(schedules) = "kids"

schedules$youngadult = NA

schedules[1:(8*6),2] = "sleeping"
schedules[((8*6)+1):90,2] = "work"
schedules[91:103, 2] = "at_Home"
schedules[104:122, 2] = "entertainment"
schedules[123:135, 2] = "at_Home"
schedules[136:144, 2] = "sleeping"

schedules$elderly = NA

schedules[c(1:(6*6), (22*6):(24*6)),3] = "sleeping"
schedules[((6*6)+1):(11*6),3] = "at_Home"
schedules[((11*6)+1):(15*6), 3] = "work"
schedules[((15*6)+1):(18*6), 3] = "social_life"
schedules[((18*6)+1):((22*6)-1), 3] = "at_Home"

schedules$adult = NA

schedules[c(1:((6*6)+3), ((23*6)+3):(24*6)),4] = "sleeping"
schedules[((6*6)+4):((7*6)+2), 4] = "at_Home"
schedules[((7*6)+3):(17*6),4] = "work"
schedules[((12*6)+3):(13*6),4] = "eat"
schedules[((17*6)+1):((17*6)+4), 4] = "at_Home"
schedules[((17*6)+5):((19*6)), 4] = "social_life"
schedules[((19*6)+1):((21*6)), 4] = "eat"
schedules[((21*6)+1):((23*6)+2), 4] = "at_Home"


write.csv(schedules, "schedules.csv")


agents_clean$scheduletype = NA
agents_clean$scheduletype[agents_clean$age < 18] = "kids"
agents_clean$scheduletype[agents_clean$age >= 18 & agents_clean$age < 35] = "youngadult"
agents_clean$scheduletype[agents_clean$age >= 35 & agents_clean$age < 65] = "adult"
agents_clean$scheduletype[agents_clean$age >= 65 ] = "elderly"

setwd("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population")

write.csv(agents_clean, "Agent_pop.csv", row.names = FALSE)
write.csv(agents_clean[1:100,], "Agent_pop_100.csv", row.names = FALSE)
