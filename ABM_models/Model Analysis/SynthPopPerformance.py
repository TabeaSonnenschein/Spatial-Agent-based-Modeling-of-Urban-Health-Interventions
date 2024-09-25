import pandas as pd
import os
import numpy as np



# # Set working directory and read CSV files
# os.chdir("D:/PhD EXPANSE/Data/Data/Amsterdam/Population/CBS statistics")

# neigh_stats = pd.read_csv("Neighborhood statistics 2019.csv")  # count of people per age group per neighborhood
# # neigh_stats = pd.read_csv("Neighborhood statistics 2020.csv")  # count of people per age group per neighborhood
# neigh_stats = neigh_stats[neigh_stats['SoortRegio_2'] == "Buurt     "]

# # SEX - AGE
# sexstats = pd.read_csv("Amsterdam_tot_sex_gender2020.csv")  # count of people per lifeyear and gender in all of Amsterdam
# sexstats['totpop'] = sexstats['male'] + sexstats['female']

# # AGE - SEX - MIGRATIONBACKGROUND - HOUSEHOLD COMPOSITION
# migrat_stats = pd.read_csv("age gender migrationbackground familie position.csv")
# migrat_age = pd.read_csv("agegroup coding_migration data.csv")
# migrat_age.columns = ['Leeftijd', 'age']
# migrat_stats = pd.merge(migrat_stats, migrat_age, how='left', on='Leeftijd')

# # EDUCATION - AGE - SEX - MIGRATIONBACKGROUND
# os.chdir(os.path.join(allDataMetafolder, "CBS statistics/socioeconomics"))
# absolved_edu = pd.read_csv("diplomaabsolvation conditioned by age sex and migrationbackground.csv")
# current_edu = pd.read_csv("students conditioned by age sex and migrationbackground.csv")
# age_coding = pd.read_csv("age_coding.csv")
# edu_coding = pd.read_csv("education_coding.csv")
# age_coding.columns = ['Leeftijd'] + age_coding.columns[1:].tolist()
# edu_coding.columns = ['Onderwijssoort', 'education_level'] + edu_coding.columns[2:].tolist()
# absolved_edu = pd.merge(absolved_edu, age_coding, how='left', on='Leeftijd')
# current_edu = pd.merge(current_edu, age_coding, how='left', on='Leeftijd')
# absolved_edu = pd.merge(absolved_edu, edu_coding, how='left', on='Onderwijssoort')
# current_edu = pd.merge(current_edu, edu_coding, how='left', on='Onderwijssoort')

# # ###################
# # ## Demographics ###
# # ###################
# # ## Neighborhood dataset
# # neigh_stats_subset = neigh_stats[[
# #     "k_0Tot15Jaar", "k_15Tot25Jaar", "k_25Tot45Jaar", "k_45Tot65Jaar", "k_65JaarOfOuder",
# #     "Mannen_6", "Vrouwen_7", "WestersTotaal_17", "NietWestersTotaal_18",
# #     "GeboorteTotaal_24", "GeboorteRelatief_25", "SterfteTotaal_26", "SterfteRelatief_27"
# # ]]

# # ## Stratified datasets
# # sexstats_subset = sexstats[["age", "male", "female", "totpop"]]

# # migrat_stats_subset = migrat_stats[["age", "Geslacht", "Migratieachtergrond"]]

# # ############################
# # ## Household Composition ###
# # ############################
# # ## Neighborhood dataset
# # neigh_stats_household = neigh_stats[[
# #     "HuishoudensTotaal_28", "Eenpersoonshuishoudens_29",
# #     "HuishoudensZonderKinderen_30", "HuishoudensMetKinderen_31", "GemiddeldeHuishoudensgrootte_32"
# # ]]

# # ## Stratified datasets
# # migrat_stats_household = migrat_stats[[
# #     "age", "Geslacht", "Migratieachtergrond", "TotaalAantalPersonenInHuishoudens_1", "ThuiswonendKind_2", "Alleenstaand_3",
# #     "TotaalSamenwonendePersonen_4", "PartnerInNietGehuwdPaarZonderKi_5", "PartnerInGehuwdPaarZonderKinderen_6",
# #     "PartnerInNietGehuwdPaarMetKinderen_7", "PartnerInGehuwdPaarMetKinderen_8", "OuderInEenouderhuishouden_9"
# # ]]

# # ####################
# ## Socioeconomics ##
# ####################
# ## Neighborhood dataset

# # # education level
# # neigh_stats2 = pd.read_csv("neigh_stats2.csv")  # Assuming file for education level data
# # education_level_subset = neigh_stats2[[
# #     "OpleidingsniveauLaag_64", "OpleidingsniveauMiddelbaar_65", "OpleidingsniveauHoog_66"
# # ]]

# # # employment
# # employment_subset = neigh_stats[[
# #     "NettoArbeidsparticipatie_67", "PercentageWerknemers_68", "PercentageZelfstandigen_69"
# # ]]

# # # income
# # neigh_stats3 = pd.read_csv("neigh_stats3.csv")  # Assuming file for income data
# # income_subset = neigh_stats3[[
# #     "AantalInkomensontvangers_67", "k_40PersonenMetLaagsteInkomen_70", "k_20PersonenMetHoogsteInkomen_71",
# #     "k_40HuishoudensMetLaagsteInkomen_73", "k_20HuishoudensMetHoogsteInkomen_74", "HuishoudensMetEenLaagInkomen_75",
# #     "HuishOnderOfRondSociaalMinimum_76"
# # ]]

# # # social support
# # social_support_subset = neigh_stats[[
# #     "HuishOnderOfRondSociaalMinimum_79", "HuishoudensTot110VanSociaalMinimum_80", "HuishoudensTot120VanSociaalMinimum_81",
# #     "MediaanVermogenVanParticuliereHuish_82", "PersonenPerSoortUitkeringBijstand_83", "PersonenPerSoortUitkeringAO_84",
# #     "PersonenPerSoortUitkeringWW_85", "PersonenPerSoortUitkeringAOW_86", "JongerenMetJeugdzorgInNatura_87",
# #     "PercentageJongerenMetJeugdzorg_88"
# # ]]

# # ## Stratified datasets

# # # education level
# # current_edu_subset = current_edu[["education_level", "age", "sex", "Migratieachtergrond", "LeerlingenDeelnemersStudenten_1"]]
# # absolved_edu_subset = absolved_edu[["education_level", "age", "sex", "Migratieachtergrond", "Gediplomeerden_1"]]


# print(neigh_stats.columns.values)
# neigh_stats["Dutch"] = neigh_stats["AantalInwoners_5"] - (neigh_stats["WestersTotaal_17"] + neigh_stats["NietWestersTotaal_18"])
# neigh_stats["Dutch"] = neigh_stats["Dutch"].clip(lower=0)

# # calculate fraction of social group per neighborhood
# totpop = ["AantalInwoners_5"]
# agevars_neigh = ['k_0Tot15Jaar_8', 'k_15Tot25Jaar_9', 'k_25Tot45Jaar_10', 'k_45Tot65Jaar_11', 'k_65JaarOfOuder_12' ]
# sexvars_neigh = [ "Mannen_6", "Vrouwen_7" ]
# migrationbackgroundvars_neigh = [ "WestersTotaal_17", "NietWestersTotaal_18", "Dutch"]
# educationvars_neigh = [ "OpleidingsniveauLaag_64", "OpleidingsniveauMiddelbaar_65", "OpleidingsniveauHoog_66"]

# neighsubset = neigh_stats[["Codering_3"]+totpop+agevars_neigh+sexvars_neigh+migrationbackgroundvars_neigh+educationvars_neigh]

# #clear all cells with "."
# emptycells =neighsubset.loc[8, "OpleidingsniveauHoog_66"]
# neighsubset = neighsubset.replace(emptycells, None)
# neighsubset = neighsubset.dropna()

# # set all columns to int apart from codering_3
# neighsubset = neighsubset.astype({col: int for col in neighsubset.columns if col != "Codering_3"})

# print(neighsubset.head(20))

# for varslist in [agevars_neigh, sexvars_neigh, migrationbackgroundvars_neigh, educationvars_neigh]:
#     try:
#         neighsubset["total"] = neighsubset[varslist].sum(axis=1)
#     except TypeError as e:
#         print(neighsubset[varslist])
#     for var in varslist:
#         #calculate the fraction for rows where there are no None values
#         neighsubset.loc[neighsubset[var].notnull() ,f"{var}_fraction"] = neighsubset.loc[neighsubset[var].notnull(),var]/neighsubset.loc[neighsubset[var].notnull(),"total"]
        
# fractionvars = [f"{var}_fraction" for var in agevars_neigh+sexvars_neigh+migrationbackgroundvars_neigh+educationvars_neigh]
# neighsubset = neighsubset[["Codering_3"]+fractionvars]
# print(neighsubset.head(20))
# print(neighsubset.columns.values)

# #rename columns

# neighsubset.columns = ["neighb_code", "0-15", "15-25", "25-45", "45-65", "65plus", 
#                        "male","female", "Western", "Non-Western", "Dutch", "low", "middle", "high"]

# neighsubset.to_csv("D:/PhD EXPANSE/Data/Data/Amsterdam/Population/NeighborhoodFractions.csv", index=False)

# ###########################################################################
# # read neighsubset data
# neighsubset = pd.read_csv("D:/PhD EXPANSE/Data/Data/Amsterdam/Population/NeighborhoodFractions.csv")
# # rename all columns apart from the neighborhood code with "_neigh" suffix
# neighsubset.columns = ["neighb_code"] + [f"{col}_neigh" for col in neighsubset.columns if col != "neighb_code"]

# ### reading agent data
# pop_df = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/Population/Agent_pop_clean.csv")

# print(pop_df.columns.values)
# # now let us reaggregate the agent data to the neighborhood level

# # regroup age into the age groups
# pop_df["age_groups"] = pd.cut(pop_df["age"], bins=[0,15,25,45,65,110], labels=["0-15", "15-25", "25-45", "45-65", "65plus"])


# relevantvars = ["age_groups","sex","migrationbackground","absolved_education"]

# uniquevals = {}
# # for each of the relevant variables, we want to calculate the fraction of each group in each neighborhood
# # we first find the unique values for each variable
# for var in relevantvars:
#     uniquevals[var] = pop_df[var].unique()  
#     print(uniquevals[var])
#     for val in uniquevals[var]:
#         subpop = pop_df.loc[pop_df[var] == val]
#         # group by neighborhood and calculate the fraction of the group in the neighborhood
#         subpop = subpop.groupby("neighb_code").size().reset_index(name=f"{val}")
#         neighsubset = neighsubset.merge(subpop, on="neighb_code", how="left")

# print(uniquevals)
# uniquevals["age_groups"] = ["0-15", "15-25", "25-45", "45-65", "65plus"]
# uniquevals["absolved_education"] = ["low", "middle", "high"]


# for vars in uniquevals:
#     try:
#         neighsubset["total"] = neighsubset[uniquevals[vars]].sum(axis=1)
#     except TypeError as e:
#         print(neighsubset[uniquevals[vars]])
#     for var in uniquevals[vars]:
#         #calculate the fraction for rows where there are no None values
#         neighsubset.loc[neighsubset[var].notnull() ,var] = neighsubset.loc[neighsubset[var].notnull(),var]/neighsubset.loc[neighsubset[var].notnull(),"total"]

# fractionvars = [var for vars in uniquevals for var in uniquevals[vars]]
# neighsubset = neighsubset[["neighb_code"]+fractionvars]
# print(neighsubset.head(20))  

# neighsubset.to_csv("D:/PhD EXPANSE/Data/Data/Amsterdam/Population/NeighborhoodFractions_Agents.csv", index=False)


# ########################################################################################
# # calculate correlation between neighborhood fractions and agent fractions
# neighsubset = pd.read_csv("D:/PhD EXPANSE/Data/Data/Amsterdam/Population/NeighborhoodFractions.csv")
# neigh_order = neighsubset["neighb_code"].values

# # read the agent data
# neighagentsubset = pd.read_csv("D:/PhD EXPANSE/Data/Data/Amsterdam/Population/NeighborhoodFractions_Agents.csv")
# # reorder the rows based on neighborhood order
# neighagentsubset = neighagentsubset.set_index("neighb_code").reindex(neigh_order).reset_index()

# print(neighsubset["neighb_code"].values)
# print(neighagentsubset["neighb_code"].values)


# columns = [ "0-15", "15-25", "25-45", "45-65", "65plus", "male","female", "Western", "Non-Western", "Dutch", "low", "middle", "high"]

# corr = []
# R2 = []
# for col in columns:
#     singlecorr = neighsubset[col].corr(neighagentsubset[col])
#     corr.append(singlecorr)
#     R2.append(singlecorr * singlecorr)
#     print(f"R2 between {col} in neighborhood and agents: ", R2)
    
# print(np.mean(corr))
# print(np.mean(R2))

# columns.append("mean")
# corr.append(np.mean(corr))
# R2.append(np.mean(R2))


# pd.DataFrame({"variable": columns, "correlation": corr , "R2": R2}).to_csv("D:/PhD EXPANSE/Data/Data/Amsterdam/Population/NeighborhoodAgentCorrelation.csv", index=False)



######################################################
### stratified fractions age, sex, migrationbackground, education
os.chdir("D:/PhD EXPANSE/Data/Data/Amsterdam/Population/CBS statistics")
# retrieve current directory

os.chdir("D:/PhD EXPANSE/Data/Data/Amsterdam/Population/CBS statistics/socioeconomics")
absolved_edu = pd.read_csv("diplomaabsolvation conditioned by age sex and migrationbackground.csv")
age_coding = pd.read_csv("age_coding.csv")
edu_coding = pd.read_csv("education_coding.csv")
age_coding.columns = ['Leeftijd'] + age_coding.columns[1:].tolist()
edu_coding.columns = ['Onderwijssoort', 'education_level'] + edu_coding.columns[2:].tolist()
absolved_edu = pd.merge(absolved_edu, age_coding, how='left', on='Leeftijd')
absolved_edu = pd.merge(absolved_edu, edu_coding, how='left', on='Onderwijssoort')

absolved_edu = absolved_edu.loc[absolved_edu["age"] != "Totaal"]
absolved_edu = absolved_edu.loc[absolved_edu["Migratieachtergrond"] != "Total"]
absolved_edu = absolved_edu.loc[absolved_edu["sex"] != "Total"]
absolved_edu = absolved_edu.loc[absolved_edu["age"] != "Leeftijd onbekend"]
absolved_edu = absolved_edu[["sex", "age", "Migratieachtergrond","ranking","Gediplomeerden_1"]]
absolved_edu.fillna(0, inplace=True)
#  remove the absolved edu rows where age is in "12", "13", "14"
absolved_edu = absolved_edu.loc[~absolved_edu["age"].isin(["12", "13", "14"])]

# sum the Gediplomeerden_1 column for each sex, age, migrationbackground, ranking combination
absolved_edu = absolved_edu.groupby(by= ["sex", "age", "Migratieachtergrond","ranking"], as_index=False).sum()
absolved_edu_total =  absolved_edu[["sex", "age", "Migratieachtergrond","Gediplomeerden_1"]].groupby(by= ["sex", "age", "Migratieachtergrond"], as_index=False).sum()
absolved_edu = absolved_edu.merge(absolved_edu_total, on = ["sex", "age", "Migratieachtergrond"], how="left", suffixes=("", "_totalgroup"))
absolved_edu["fraction"] = absolved_edu["Gediplomeerden_1"]/absolved_edu["Gediplomeerden_1_totalgroup"]


print(absolved_edu.columns.values)
print(absolved_edu.head(50))

# rename columns ["sex", "age_group", migrationbackground, "absolved_education", "Gediplomeerden_1",  "Gediplomeerden_1_totalgroup" , "fraction"]
absolved_edu.columns = ["sex", "age_group", "migrationbackground", "absolved_education", "Gediplomeerden_1",  "Gediplomeerden_1_totalgroup" , "fraction"]
absolved_edu.to_csv("D:/PhD EXPANSE/Data/Data/Amsterdam/Population/StratifiedFractions_Education.csv", index=False)

print(absolved_edu["age_group"].unique())

pop_df = pd.read_csv("D:/PhD EXPANSE/Data/Amsterdam/ABMRessources/ABMData/Population/Agent_pop_clean.csv")
print(pop_df.columns.values)

bins=[0,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29, 30, 35,40,45,50,110]
labels=["0-11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29",
            "30 tot 35 jaar", "35 tot 40 jaar", "40 tot 45 jaar", "45 tot 50 jaar", "50 jaar of ouder"]

print(len(bins), len(labels))
print(pop_df["absolved_education"].unique())
pop_df["age_group"] = pd.cut(pop_df["age"], bins=bins, labels=labels)
pop_df = pop_df.loc[~pop_df["age_group"].isin(["0-11","12", "13", "14"])]

# group by sex, age_group, migrationbackground, absolved_education and count the number of agents in each group
pop_df_groups = pop_df.groupby(by=["sex", "age_group", "migrationbackground", "absolved_education"], as_index=False).size().reset_index()

pop_df_groups_tot = pop_df_groups[["sex", "age_group", "migrationbackground", "size"]].groupby(by = ["sex", "age_group", "migrationbackground"], as_index=False).sum()
pop_df_groups = pop_df_groups.merge(pop_df_groups_tot, on=  ["sex", "age_group", "migrationbackground"], how = "left", suffixes=("", "_totalgroup"))
pop_df_groups["fraction"] = pop_df_groups["size"]/pop_df_groups["size_totalgroup"]

print(pop_df_groups.head(50))

pop_df_groups.to_csv("D:/PhD EXPANSE/Data/Data/Amsterdam/Population/StratifiedFractions_Agents.csv", index=False)
