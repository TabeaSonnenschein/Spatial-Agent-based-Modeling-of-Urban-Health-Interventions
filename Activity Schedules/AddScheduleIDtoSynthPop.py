import pandas as pd
import itertools
import numpy as np


# Reading datasets
ScheduleGroups = pd.read_csv("D:\PhD EXPANSE\Data\EU microdata access\HETUS2010_Synthpop_schedules.csv")
SynthPop = pd.read_csv("C:/Users/Tabea/Documents/PhD EXPANSE/Data/Amsterdam/Population/Agent_pop.csv")

# Checking the columns
print(ScheduleGroups.columns)
print(SynthPop.columns)


# restructuring variables that are not in the same format
SynthPop["agegroup"] = SynthPop["age"].mask(SynthPop["age"].between(0, 17), 1).mask(
    SynthPop["age"].between(18, 24), 2).mask(SynthPop["age"].between(25, 34), 3).mask(SynthPop["age"].between(35, 44), 4).mask(
        SynthPop["age"].between(45, 64), 5).mask(SynthPop["age"].between(65, 120), 6)
SynthPop["agegroup"].loc[SynthPop["age"]<10] = None 
ScheduleGroups["sex"] = ScheduleGroups["sex"].replace({1: "male", 2: "female"})
SynthPop["personal_income"] = SynthPop["personal_income"].replace({"has_personal_income": 1, "no_personal_income": 0})
SynthPop["current_education_binary"] = 1
SynthPop["current_education_binary"].loc[SynthPop["current_education"]== "no_current_edu"] = 0
ScheduleGroups = ScheduleGroups.rename(columns={"current_education": "current_education_binary"})


# identifying the variables that are needed for the join
vars = ["agegroup", "sex", "havechild", "personal_income", "current_education_binary",  "car_access",  "hh_single" ]


# look ath the values of the variables
for var in vars:
    print("SynthPop")
    print(SynthPop[var].value_counts())
    print("ScheduleGroups") 
    print(ScheduleGroups[var].value_counts())


# merge the two dataframes based on the variables
SynthPop = pd.merge(SynthPop, ScheduleGroups, on=vars, how="left")
print(SynthPop["ScheduleID"].value_counts())


SynthPop["ScheduleID"].fillna("SchedBaby", inplace=True)
SynthPop["ScheduleID"].loc[SynthPop["age"].between(6,10)] = "SchedChild"

# Now SynthPop has a column with the schedule group ID
print(SynthPop.head(20))
print(SynthPop.columns)

# save the file
SynthPop.to_csv(r"C:\Users\Tabea\Documents\PhD EXPANSE\Data\Amsterdam\Population\Agent_popwithScheduleID.csv", index=False)