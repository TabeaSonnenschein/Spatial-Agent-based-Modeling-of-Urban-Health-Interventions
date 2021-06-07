
setwd("C:/Dokumente/PhD EXPANSE/Data/Harmonised European Time Use Survey - Eurostat")
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
