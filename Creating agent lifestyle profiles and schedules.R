
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





social_profiles_schedules <- as.data.frame(matrix(nrow = 6, ncol = 5))

activities = c("sleep", "work", "at_study_facility", "eat", "childcare", "social_life", "entertainment", "physical_exercise", "walking_the_dog", "at_home")
corr_activity_codes = c("AC01", "AC1A", "AC21A", "AC02", "AC38A", "AC38B", "AC51A", "AC51B", "AC52", "AC6A", "AC344")

strat_activ_TU = age_sex_act_PTP_TIME[, c("agegroups", "sex", corr_activity_codes)]
colnames(strat_activ_TU) =c("agegroups", "sex", "sleep", "work", "at_study_facility", "eat", "childcare1", "childcare2", "social_life1", "social_life2","entertainment", "physical_exercise", "walking_the_dog")
