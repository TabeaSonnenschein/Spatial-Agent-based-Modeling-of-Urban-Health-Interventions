import csv
import os
import pandas as pd
import itertools
import numpy as np


# reading the time use data from the csv file
HETUS2010 = pd.read_csv("D:\PhD EXPANSE\Data\EU microdata access\HETUS\DATA\TUS_SUF_A_NL_2010.csv")


# extract the variables that are needed for the activity schedules
# Explanation of the variables:
    # DDV6 = 1 # employed or student
    # HHC1  # household size
    # HHC3 + HHC4 # number of children in household
    # HHQ6p # number of cars in household
    # HHQ9_1 #household income quintile
    # INC1 # sex of respondent 1= male 2= female
    # INC2 # agegroup of respondent
    # INC4_126 # main activity of respondent (student, employed, retired, unemployed, other)
    # IND19 # currently in education
    # IND22_1 # highest level of education
    # IND28_1 # marital status
    # IND41_1 # migration background


# Process the relevant variables
Attributes = HETUS2010[["PID", "INC1", "INC2", "INC4_1", "IND13_1", "IND19", "IND22_1", "IND28_1", "IND41_1", "DDV6", "HHC1", "HHC3", "HHC4", "HHQ6p", "HHQ9_1"]]
Attributes.drop_duplicates(inplace=True) # drop duplicates

# show the distribution of the variables
print(Attributes["INC2"].value_counts())    # agegroup
print(Attributes["INC1"].value_counts())    # sex
print(Attributes["INC4_1"].value_counts())  # main activity
print(Attributes["IND19"].value_counts())   # currently in education
print(Attributes["IND28_1"].value_counts()) # marital status
print(Attributes["DDV6"].value_counts())    # employed or student
print(Attributes["HHC1"].value_counts())    # household size
print(Attributes["HHC3"].value_counts())    # number of children in household
print(Attributes["HHC4"].value_counts())    # number of children in household
print(Attributes["HHQ6p"].value_counts())   # number of cars in household

# print(Attributes["IND13_1"].value_counts())  # personal income quintile, not asked in NL
# print(Attributes["IND41_1"].value_counts()) # migration background, not asked in NL
# print(Attributes["IND22_1"].value_counts()) # highest level of education, not asked in NL
# print(Attributes["HHQ9_1"].value_counts())  # household income quintile, not asked in NL


# restructuring the variables
HETUS2010["car_access"] = HETUS2010["HHQ6p"].replace({(0,-9): 0, (1,2,3): 1})
HETUS2010["personal_income"]  = HETUS2010["INC4_1"].replace({(1,2,3): 1, (4,5,8):0})
HETUS2010["sex"]  = HETUS2010["INC1"]
HETUS2010["agegroup"]  = HETUS2010["INC2"].replace({(2,3):2, (4,5):3, (6,7):4, (8,9,10,11):5, (12,13,14,15):6})
HETUS2010["hh_single"]  = HETUS2010["HHC1"].replace({1: 1, (2,3,4,5,6,7,8):0})
HETUS2010["nrchildren"]  = HETUS2010["HHC3"].replace({(6,7,8,9):0}) + HETUS2010["HHC4"].replace({(6,7,8,9):0})
HETUS2010["havechild"]  = HETUS2010["nrchildren"].replace({0: 0, (1,2,3,4,5,6,7,8):1})
HETUS2010["current_education"] = HETUS2010["IND19"].replace({(2,-9): 0})
# HETUS2010["student"]   = HETUS2010["INC4_1"].replace({5: 1, (1,2,3,4,8):0}) # duplicated with current_education


# create a new csv file with the subselected variables
Synthpop_attr = HETUS2010[["agegroup", "sex", "personal_income", "current_education",  "car_access",  "hh_single",  "havechild"]]
Synthpop_attr.drop_duplicates(inplace=True) # drop duplicates

# create a table of all possible combinations of the variable values
vars = ["agegroup", "sex", "havechild", "personal_income", "current_education",  "car_access",  "hh_single" ]
#vars = ["agegroup", "sex", "personal_income", "current_education",   "havechild"]

def CreateCombinations(vars):
    #varlength, totlength = varlengthNproduct(vars)
    combinations = []
    for var in vars:
        combinations.append(Synthpop_attr[var].unique())
    return(list(itertools.product(*combinations)))

Synthpop_schedules = pd.DataFrame(CreateCombinations(vars), columns=vars)
print(Synthpop_schedules.head(10))
print(Synthpop_schedules.shape)
pd.DataFrame.to_csv(Synthpop_schedules, "D:\PhD EXPANSE\Data\EU microdata access\HETUS2010_Synthpop_schedules.csv", index=False)

# create the activity schedules framework
Weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
Weekdays_int = [1,2,3,4,5,6,7]

print(HETUS2010.columns.values.tolist())

print(HETUS2010["DDV1"].value_counts()) # day of week
print(HETUS2010["Mact1"].value_counts()) # activity 1


ActivityVars = ["Mact" + str(i) for i in range(1,145)]
LocationVars = ["Wherep" + str(i) for i in range(1,145)]

# recoding the activities
for timestamp in ActivityVars:
    HETUS2010[timestamp]  = HETUS2010[timestamp].replace({
        (11, 531): 1,                   # sleep/rest
        (21, 121):2,                    # eating
        (111, 129):3,                   # work
        (211):4,                        # school/university
        (31,200,212,221,12,39,300,312,321,323, 
        324,329,331,332,333,339,342,343,349,
        351,352,353,354,359,371,381,382,383,384,
        389,391,392,399,514,711,712,713,719, 
        721,722,723,729,731,732,733,739,811,
        812,819,821,831,995,998,999):5, # at home
        (311):6,                        # cooking
        (322, 341):7,                    # gardening
        (344, 611,612,613,614,615,
         616,619,621,631):8,            # walking the dog
        (361, 362, 363, 369):9,         # shopping/services
        (411,421,422,423,424,425,429,431,432,
        439,511,512,513,519):10,       # social life
        (521,522,523,524,525,529):11,   # entertainment / culture
        (910,920,936,938,939,940,950,960,
        980,900):12,                    # travel
        })
    # print(HETUS2010[timestamp].value_counts())


Synthpop_schedules[["NrPeople", "NrVars"] + ActivityVars + LocationVars] = None

def SchedulePopulater(Synthpop_schedules, Weekdays_int):
    for day in Weekdays_int:
        #print("Day", day)
        daysubset = HETUS2010.loc[HETUS2010["DDV1"]== day,["PID", "DDV1"]+ vars + ActivityVars]
        #print(daysubset.head(10))
        Synthpop_schedules_day = Synthpop_schedules
        for i in range(len(Synthpop_schedules.index)):
            #print("populationgroup", i, vars, list(Synthpop_schedules[vars].iloc[i]))
            mask = daysubset[vars].apply(lambda x: np.all(x.values == Synthpop_schedules[vars].iloc[i]), axis=1)
            popsubset = daysubset[mask]
            subvars = vars
            while len(popsubset.index) == 0:
                subvars = subvars[:-1]
                mask = daysubset[subvars].apply(lambda x: np.all(x.values == Synthpop_schedules[subvars].iloc[i]), axis=1)
                popsubset = daysubset[mask]
            print(len(popsubset.index))
            Synthpop_schedules_day["NrPeople"].iloc[i] = len(popsubset.index)
            Synthpop_schedules_day["NrVars"].iloc[i] = len(subvars)
            if len(popsubset.index) > 0:
                for timestamp in ActivityVars:
                    Synthpop_schedules_day[timestamp].iloc[i] = popsubset[timestamp].value_counts().index[0]
        Synthpop_schedules_day.to_csv("D:\PhD EXPANSE\Data\EU microdata access\HETUS2010_Synthpop_schedules_day" + str(day) + ".csv", index=False)
    return(Synthpop_schedules)

Synthpop_schedules = SchedulePopulater(Synthpop_schedules, Weekdays_int)