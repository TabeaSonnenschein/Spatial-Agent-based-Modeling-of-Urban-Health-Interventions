import numpy as np
import pandas as pd
import os
from itertools import chain

os.chdir(r"D:\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
evidence_instances_full = pd.read_csv("unique_evidence_instances_clean2_harmonised_BO_manualclean_BD_unique_SG_unique.csv")

evidence_instances = evidence_instances_full[['DOI', 'Sentence', 'Fullsentence', 'BehaviorOption', 'BehaviorOptionHarmon', 'BehaviorDeterminant', 'Studygroup',
                                              'Moderator', 'stat_significance', 'stat_consistency', 'stat_direction', 'stat_correl']]

for column in ['BehaviorDeterminant', 'Studygroup', 'Moderator']:
    evidence_instances[column] = evidence_instances[column].str.lower()

relevant_BOs = ["walking", "biking", "driving", "public transport use"]
evidence_instances[evidence_instances["BehaviorOptionHarmon"].isin(relevant_BOs)]


AllRelevantEvidence = pd.DataFrame()
for BOclass in relevant_BOs:
    pot_sign_var = evidence_instances.loc[((evidence_instances["BehaviorOptionHarmon"] == BOclass)
                            & ((evidence_instances["stat_significance"] == "significant")
                             | (evidence_instances["stat_consistency"] == "consistent"))),
                            ['BehaviorOptionHarmon', 'BehaviorDeterminant', 'Studygroup', 'Moderator', 'DOI']]
    pot_sign_var.drop_duplicates(inplace = True)
    pot_sign_var.sort_values(by=['BehaviorDeterminant', 'Studygroup', 'Moderator'], inplace=True)
    candit_vars = pot_sign_var[['BehaviorOptionHarmon', 'BehaviorDeterminant', 'Studygroup', 'Moderator']].drop_duplicates().reset_index(drop=True)
    candit_vars["Nr_Studies_Significant"] = list(pot_sign_var[['BehaviorOptionHarmon', 'BehaviorDeterminant', 'Studygroup', 'Moderator']].value_counts(sort = False))
    candit_vars["listDOIsSignificant"] = [", ".join(pot_sign_var.loc[(pot_sign_var['BehaviorOptionHarmon'] == candit_vars['BehaviorOptionHarmon'].iloc[idx])
                                                          &(pot_sign_var['BehaviorDeterminant'] == candit_vars['BehaviorDeterminant'].iloc[idx])
                                                          &(pot_sign_var['Studygroup'] == candit_vars['Studygroup'].iloc[idx])
                                                          &(pot_sign_var['Moderator'] == candit_vars['Moderator'].iloc[idx]), "DOI"]) for idx in candit_vars.index.values]
    all_resp_evid = pd.merge(evidence_instances,candit_vars, on=['BehaviorOptionHarmon', 'BehaviorDeterminant', 'Studygroup', 'Moderator'])
    inconsistent_ones = all_resp_evid.loc[(all_resp_evid["stat_significance"] == "insignificant")| (evidence_instances["stat_consistency"] == "inconsistent"), ['BehaviorOptionHarmon', 'BehaviorDeterminant', 'Studygroup', 'Moderator', 'DOI']]
    inconsistent_ones.sort_values(by=['BehaviorDeterminant', 'Studygroup', 'Moderator'], inplace=True)
    inconsistent_types = inconsistent_ones[['BehaviorOptionHarmon', 'BehaviorDeterminant', 'Studygroup', 'Moderator']].drop_duplicates().reset_index(drop=True)
    inconsistent_types["Nr_Studies_Insignificant"] = list(inconsistent_ones[['BehaviorOptionHarmon', 'BehaviorDeterminant', 'Studygroup', 'Moderator']].value_counts(sort = False))
    inconsistent_types["listDOIsInsignificant"] = [", ".join(inconsistent_ones.loc[(inconsistent_ones['BehaviorOptionHarmon'] == inconsistent_types['BehaviorOptionHarmon'].iloc[idx])
                    & (inconsistent_ones['BehaviorDeterminant'] == inconsistent_types['BehaviorDeterminant'].iloc[idx])
                    & (inconsistent_ones['Studygroup'] == inconsistent_types['Studygroup'].iloc[idx])
                    & (inconsistent_ones['Moderator'] == inconsistent_types['Moderator'].iloc[idx]), "DOI"]) for idx in inconsistent_types.index.values]

    candit_vars = pd.merge(candit_vars,inconsistent_types, how = "outer", on=['BehaviorOptionHarmon', 'BehaviorDeterminant', 'Studygroup', 'Moderator'])
    AllRelevantEvidence = pd.concat([AllRelevantEvidence, candit_vars])

AllRelevantEvidence.to_csv("RelevantEvidence.csv")
AllRelevantEvidence['Nr_Studies_Insignificant'] = AllRelevantEvidence['Nr_Studies_Insignificant'].fillna(0)
AllRelevantEvidence = AllRelevantEvidence.query('Nr_Studies_Significant > Nr_Studies_Insignificant')

relevant_variables = pd.DataFrame(AllRelevantEvidence['BehaviorDeterminant'])
relevant_variables["Type"] = "BD"
relevant_variables.rename(columns={"BehaviorDeterminant": "Variable"}, inplace = True)
studygroupvariables = list(chain.from_iterable([i.replace("['", ""). replace("']", "").split("', '") for i in AllRelevantEvidence['Studygroup']]))
relevant_variables = relevant_variables.append(pd.DataFrame({"Variable":studygroupvariables, "Type": ["SG"]* len(studygroupvariables)}), ignore_index=True)
relevant_variables = relevant_variables.append(pd.DataFrame({"Variable": AllRelevantEvidence['Moderator'], "Type":  ["MO"] * len(AllRelevantEvidence['Moderator'])}), ignore_index=True)
relevant_variables_df = relevant_variables.sort_values(by = "Variable").drop_duplicates()
relevant_variables_df = relevant_variables_df.loc[relevant_variables_df["Variable"] != "-100"]
relevant_variables_df["NrSignStudiedCombinations"] = [list(relevant_variables.loc[relevant_variables["Type"] == relevant_variables_df.iloc[idx, 1], "Variable"]).count(value) for idx, value in enumerate(relevant_variables_df["Variable"])]
relevant_variables_df["NrDOIsSignificant"] = 0
for type in ["BD", "SG", "MO"]:
    indices = np.where(relevant_variables_df["Type"] == type)[0]
    if type == "BD":
        relevant_variables_df["NrDOIsSignificant"].iloc[indices] = [len(set((AllRelevantEvidence.loc[AllRelevantEvidence['BehaviorDeterminant'] == el, "listDOIsSignificant"]))) for el in relevant_variables_df["Variable"].iloc[indices] ]
    elif type == "SG":
        relevant_variables_df["NrDOIsSignificant"].iloc[indices] = [len(set((AllRelevantEvidence.loc[(AllRelevantEvidence['Studygroup'] == el) | ( AllRelevantEvidence['Studygroup'].str.contains("'" + el + "'" )), "listDOIsSignificant"]))) for el in relevant_variables_df["Variable"].iloc[indices] ]
    elif type == "MO":
        relevant_variables_df["NrDOIsSignificant"].iloc[indices] = [len(set((AllRelevantEvidence.loc[AllRelevantEvidence['Moderator'] == el  , "listDOIsSignificant"]))) for el in relevant_variables_df["Variable"].iloc[indices] ]


print(relevant_variables_df)

relevant_variables_df.to_csv("RelevantVariables.csv", index=False)

