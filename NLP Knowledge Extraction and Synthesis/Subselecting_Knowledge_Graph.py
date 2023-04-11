import numpy as np
import pandas as pd
import os
from itertools import chain

os.chdir(r"D:\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
evidence_instances_full = pd.read_csv("unique_evidence_instances_clean2_harmonised_BO_BD_unique_SG_unique.csv")

evidence_instances = evidence_instances_full[['DOI', 'Sentence', 'Fullsentence', 'BehaviorOption', 'BehaviorOptionHarmon', 'BehaviorDeterminant', 'Studygroup',
                                              'Moderator', 'stat_significance', 'stat_consistency', 'stat_direction', 'stat_correl']]

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
    candit_vars = pot_sign_var[['BehaviorOptionHarmon', 'BehaviorDeterminant', 'Studygroup', 'Moderator']].drop_duplicates()
    candit_vars["Nr_Studies_Significant"] = list(pot_sign_var[['BehaviorOptionHarmon', 'BehaviorDeterminant', 'Studygroup', 'Moderator']].value_counts(sort = False))
    all_resp_evid = pd.merge(evidence_instances,candit_vars, on=['BehaviorOptionHarmon', 'BehaviorDeterminant', 'Studygroup', 'Moderator'])
    inconsistent_ones = all_resp_evid.loc[(all_resp_evid["stat_significance"] == "insignificant")| (evidence_instances["stat_consistency"] == "inconsistent"), ['BehaviorOptionHarmon', 'BehaviorDeterminant', 'Studygroup', 'Moderator', 'DOI']]
    inconsistent_ones.sort_values(by=['BehaviorDeterminant', 'Studygroup', 'Moderator'], inplace=True)
    inconsistent_types = inconsistent_ones[['BehaviorOptionHarmon', 'BehaviorDeterminant', 'Studygroup', 'Moderator']].drop_duplicates()
    inconsistent_types["Nr_Studies_Insignificant"] = list(inconsistent_ones[['BehaviorOptionHarmon', 'BehaviorDeterminant', 'Studygroup', 'Moderator']].value_counts(sort = False))
    candit_vars = pd.merge(candit_vars,inconsistent_types, how = "outer", on=['BehaviorOptionHarmon', 'BehaviorDeterminant', 'Studygroup', 'Moderator'])
    AllRelevantEvidence = pd.concat([AllRelevantEvidence, candit_vars])

AllRelevantEvidence.to_csv("AllRelevantEvidence.csv")
AllRelevantEvidence['Nr_Studies_Insignificant'] = AllRelevantEvidence['Nr_Studies_Insignificant'].fillna(0)
AllRelevantEvidence = AllRelevantEvidence.query('Nr_Studies_Significant > Nr_Studies_Insignificant')

relevant_variables = [list(AllRelevantEvidence['BehaviorDeterminant'])]
relevant_variables.extend([list(AllRelevantEvidence['Studygroup']), list(AllRelevantEvidence['Moderator'])])
relevant_variables = list(chain.from_iterable([i.replace("['", ""). replace("']", "").split("', '") for i in list(chain.from_iterable(relevant_variables))]))
relevant_variables_clean = sorted(list(dict.fromkeys(relevant_variables)))
relevant_variables_clean.remove("-100")
print(relevant_variables_clean)
relevant_variables_df = pd.DataFrame(relevant_variables_clean)
relevant_variables_df["Nr_mentions"] = [relevant_variables.count(el) for el in relevant_variables_clean]
relevant_variables_df["Nr_Studies_Significant"] = [sum(AllRelevantEvidence["Nr_Studies_Significant"].loc[(AllRelevantEvidence['BehaviorDeterminant'] == el)|(AllRelevantEvidence['Studygroup'] == el)|(AllRelevantEvidence['Moderator'] == el) ]) for el in relevant_variables_clean ]
print(relevant_variables_df)

relevant_variables_df.to_csv("RelevantVariables.csv")

