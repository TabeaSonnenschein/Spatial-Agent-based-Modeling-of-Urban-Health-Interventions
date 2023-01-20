import os
import pandas as pd
import numpy as np

#####################################################################
## This script uses the evidence instance dataframe to generate edgelists and nodelists for visualization of the knowledge graph.
## This visualization can happen for example with the open source software Gephi
################################################################################

### Functions
def assign_keys_to_uniq_var(df, column, key_prefix):
    ''' Takes a dataframe, column and key_prefix name
    and generates keys for the unique values in the column and adds it to the dataframe'''
    uniq_val = set(uniq_edgelist[column])
    uniq_keys = [key_prefix + str(i) for i in range(1,(len(uniq_val)+1))]
    print("Nr of unique keys", len(uniq_keys))
    df[key_prefix+"keys"] = [uniq_keys[i] for x in df[column] for i,f in enumerate(uniq_val) if x == f]
    return df
    nodes.to_csv((graph_name+"_nodeslist.csv"), index=False)


# Output dataframes can be read by gephi and when installing EventGraphLayout plugin transformed to tripartite graph visualization
# This graph visualization function uses the harmonised Behavior Choice options only as an optional way to subselect the evidence instances
# The verbatim original variable names are the labels in the nodes and edgelist outputs
def prepare_output_tables_Gephi_subgraph_BOBDSG(df, subset_keys, graph_name, harmon_BOs = False):
    ''' Generates a nodes- and an edgelist for the Behavior Choice Option (BO), Behavior Determinants (BD) and Studygroups (SG) for instances
        where one of the strings in the subset keys is in the Behavior Choice option
        or where it equals the value of a column (BehaviorOptionHarmon) with manually harmonised Behavior Choice options.'''
    if harmon_BOs:
        sub_graph_edgelist = df.iloc[np.where(df['BehaviorOptionHarmon'] == subset_keys[0])[0]]
    else:
        sub_graph_edgelist = df.iloc[[count for count, value in enumerate(df["BehaviorOption"]) if any(True for x in subset_keys if x in value)]]
    sub_graph_edgelist1 = sub_graph_edgelist[['BO_keys', 'BD_keys', 'sign_consist', 'counts_mention', 'counts_articles']].rename(columns={'BO_keys': 'Source', 'BD_keys': 'Target'})
    sub_graph_edgelist2 = sub_graph_edgelist[['BD_keys', 'SG_keys', 'sign_consist', 'counts_mention', 'counts_articles']].rename(columns={'BD_keys': 'Source', 'SG_keys': 'Target'})
    nodes = pd.concat([sub_graph_edgelist[['BO_keys', 'BehaviorOption']].rename(columns={'BO_keys':'Id', 'BehaviorOption': 'Label' }),
                       sub_graph_edgelist[['BD_keys', 'BehaviorDeterminant']].rename(columns={'BD_keys':'Id', 'BehaviorDeterminant': 'Label' }),
                       sub_graph_edgelist[['SG_keys', 'Studygroup']].rename(columns={'SG_keys':'Id', 'Studygroup': 'Label'})],
                      ignore_index=True, axis=0)
    l = len(sub_graph_edgelist.index)
    nodes["Mode"] = 4
    nodes["Mode"].iloc[:l] = 2
    nodes["Mode"].iloc[l:(l*2)] = 3
    nodes.loc[len(nodes.index)] = ['BO_class', graph_name , 1]
    nodes = nodes.drop_duplicates()
    superclass_df = pd.DataFrame({"Source": ['BO_class'] * len(set(sub_graph_edgelist['BO_keys'])),
                                  "Target": list(dict.fromkeys(sub_graph_edgelist['BO_keys'])),
                                  "sign_consist": [3]* len(set(sub_graph_edgelist['BO_keys'])),
                                  "counts_mention": [100]* len(set(sub_graph_edgelist['BO_keys'])),
                                  "counts_articles": [100]* len(set(sub_graph_edgelist['BO_keys']))})
    sub_graph_edgelist = pd.concat([sub_graph_edgelist1, sub_graph_edgelist2, superclass_df], ignore_index=True, axis=0)
    sub_graph_edgelist.to_csv(
        (graph_name + "_edgelist_BOBDSG.csv"), index=False)
    nodes.to_csv((graph_name+"_nodeslist_BOBDSG.csv"), index=False)


# Output dataframes can be read by gephi and when installing EventGraphLayout plugin transformed to bipartite graph visualization
# This graph visualization aggregates the evidence at the harmonised Behavior Choice Option level to simplify the output
def prepare_output_tables_Gephi_harmonBOBD(df, graph_name, Source_col, Target_col, Source_label, Target_label):
    ''' Generates a nodes- and an edgelist for the harmonised Behavior Choice Option (BO) and Behavior Determinants (BD)
        for all evidence instances (no subgraph) but aggregated at the harmonised Behavior Choice Option level.'''
    subgraph = df[[Source_col, Target_col, Source_label,Target_label, 'sign_consist']]
    subgraph.drop_duplicates()
    subgraph[['counts_mention', 'counts_articles']] = 0
    for count, value in enumerate(subgraph[Source_label]):
        mentions = list(np.where((evidence_instances_full[Source_label] == value) & (evidence_instances_full[Target_label] == subgraph[Target_label].iloc[count]))[0])
        subgraph["counts_mention"].iloc[count] = len(mentions)
        subgraph["counts_articles"].iloc[count] = len(set(evidence_instances_full["DOI"].iloc[mentions]))
    subgraph.rename(columns={Source_col: 'Source', Target_col: 'Target'}, inplace=True)
    nodes = pd.concat([subgraph[['Source', Source_label]].rename(columns={'Source':'Id', Source_label: 'Label' }),
                       subgraph[['Target', Target_label]].rename(columns={'Target':'Id', Target_label: 'Label' })],
                      ignore_index=True, axis=0)
    nodes["Mode"] = 2
    nodes["Mode"].iloc[:len(subgraph['Source'])] = 1
    nodes = nodes.drop_duplicates()
    subgraph.to_csv(
        (graph_name + "_edgelist.csv"), index=False)
    nodes.to_csv((graph_name+"_nodeslist.csv"), index=False)


## Execution

# Reading the evidence data
os.chdir(r"D:\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
evidence_instances_full = pd.read_csv("unique_evidence_instances_clean2_harmonised_BO_manualclean.csv")

# Preparing the data
evidence_instances_full.replace({"-100": 'NaN'}, regex=False, inplace=True)
evidence_instances_full.fillna("NaN")
print(evidence_instances_full.head())
evidence_instances_full['sign_consist'] = [1 if (evidence_instances_full['stat_significance'].iloc[i] == "significant")
                                                or (evidence_instances_full['stat_consistency'].iloc[i] == "consistent")
                                                or (evidence_instances_full['stat_correl'].iloc[i] == "correlated")
                                           else 0 for i in range(0,len(evidence_instances_full['stat_consistency']))]
evidence_instances_full["BehaviorDeterminant"] = [i.lower() for i in evidence_instances_full["BehaviorDeterminant"]]
evidence_instances_full["Studygroup"].iloc[evidence_instances_full["Studygroup"] == "NaN"] = "general population"
evidence_instances_full["Studygroup"] = [i.lower() for i in evidence_instances_full["Studygroup"]]
print(set(list(evidence_instances_full["Studygroup"])))
evidence_instances_full["BehaviorOption"] = [i.lower() for i in evidence_instances_full["BehaviorOption"]]
uniq_edgelist = evidence_instances_full[["BehaviorOption", "BehaviorOptionHarmon", "BehaviorDeterminant", "Studygroup", "Moderator", "sign_consist"]].drop_duplicates()
uniq_edgelist = uniq_edgelist.drop_duplicates()

print("edgelist length", len(evidence_instances_full))
print("unique edgelist length",len(uniq_edgelist))


# Add data on frequency of evidence across articles
uniq_edgelist[["counts_mention", "counts_articles"]] = 1
for x in range(0,len(uniq_edgelist['BehaviorOption'])):
    mentions = list(np.where((evidence_instances_full["BehaviorOption"] == uniq_edgelist["BehaviorOption"].iloc[x]) &
                                                  (evidence_instances_full["BehaviorDeterminant"] == uniq_edgelist["BehaviorDeterminant"].iloc[x]) &
                                                  (evidence_instances_full["Studygroup"] == uniq_edgelist["Studygroup"].iloc[x]) &
                                                  (evidence_instances_full["Moderator"] == uniq_edgelist["Moderator"].iloc[x]) &
                                                  (evidence_instances_full["sign_consist"] == uniq_edgelist["sign_consist"].iloc[x]))[0])
    uniq_edgelist["counts_mention"].iloc[x] = len(mentions)
    uniq_edgelist["counts_articles"].iloc[x] = len(set(evidence_instances_full["DOI"].iloc[mentions]))

print("counts mention distribution:")
print(uniq_edgelist["counts_mention"].value_counts())
print("counts articles distribution:")
print(uniq_edgelist["counts_articles"].value_counts())

# Assigning keys to unique variables
uniq_edgelist = assign_keys_to_uniq_var(uniq_edgelist, "BehaviorOption", "BO_")
uniq_edgelist = assign_keys_to_uniq_var(uniq_edgelist, "BehaviorDeterminant", "BD_")
uniq_edgelist = assign_keys_to_uniq_var(uniq_edgelist, "Studygroup", "SG_")
uniq_edgelist = assign_keys_to_uniq_var(uniq_edgelist, "Moderator", "MO_")
uniq_edgelist = assign_keys_to_uniq_var(uniq_edgelist, "BehaviorOptionHarmon", "BOharm_")
uniq_edgelist.to_csv("full_edgelist.csv", index=False)

# generating Output tables for different modes and graph visualizations
prepare_output_tables_Gephi_subgraph_BOBDSG(df = uniq_edgelist, subset_keys = ["biking"],
                            graph_name = "bike", harmon_BOs=True)

prepare_output_tables_Gephi_subgraph_BOBDSG(df = uniq_edgelist, subset_keys = ["walking"],
                            graph_name = "walking", harmon_BOs=True)

prepare_output_tables_Gephi_subgraph_BOBDSG(df = uniq_edgelist, subset_keys = ["active school travel"],
                            graph_name = "activeschooltravel", harmon_BOs=True)

prepare_output_tables_Gephi_subgraph_BOBDSG(df = uniq_edgelist, subset_keys = ["driving"],
                            graph_name = "driving", harmon_BOs=True)

prepare_output_tables_Gephi_subgraph_BOBDSG(df = uniq_edgelist, subset_keys = ["physical activity"],
                            graph_name = "pysicalactivity", harmon_BOs=True)

prepare_output_tables_Gephi_subgraph_BOBDSG(df = uniq_edgelist, subset_keys = ["active travel"],
                            graph_name = "activetravel", harmon_BOs=True)

prepare_output_tables_Gephi_subgraph_BOBDSG(df = uniq_edgelist, subset_keys = ["public transport use"],
                            graph_name = "transit", harmon_BOs=True)

prepare_output_tables_Gephi_harmonBOBD(df = uniq_edgelist, graph_name = "harmonise_BO_final", Source_col = "BOharm_keys",
                            Target_col = "BD_keys", Source_label = "BehaviorOptionHarmon",
                            Target_label = "BehaviorDeterminant")



## use of script without manually harmonised Behavior Choice Options

# prepare_output_tables_Gephi_subgraph_BOBDSG(df = uniq_edgelist, subset_keys = ["bike", "biking", "cycl"],
#                           graph_name = "bike", harmon_BOs = False)

# prepare_output_tables_Gephi_subgraph_BOBDSG(df = uniq_edgelist, subset_keys = ["public", "transit", "bus", "subway", "tram"],
#                          graph_name = "publicTransport", , harmon_BOs = False)
