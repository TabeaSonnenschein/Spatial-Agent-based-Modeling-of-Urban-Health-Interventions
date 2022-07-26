import itertools
import matplotlib.pyplot as plt
import networkx as nx
from dash import Dash, html
import dash_cytoscape as cyto
import os
import pandas as pd
import numpy as np
from networkx.algorithms import bipartite
#
# os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
# evidence_instances_full = pd.read_csv("unique_evidence_instances_clean2.csv")
# evidence_instances_full.replace({"-100": 'NaN'}, regex=False, inplace=True)
# evidence_instances_full.fillna("NaN")
# print(evidence_instances_full.head())
#
# evidence_instances_full['sign_consist'] = [1 if (evidence_instances_full['stat_significance'].iloc[i] == "significant")
#                                                 or (evidence_instances_full['stat_consistency'].iloc[i] == "consistent" )
#                                            else 0 for i in range(0,len(evidence_instances_full['stat_consistency']))]
# print("edgelist length", len(evidence_instances_full))
# uniq_edgelist = evidence_instances_full[["BehaviorOption","BehaviorDeterminant", "Studygroup", "Moderator", "sign_consist"]].drop_duplicates()
# uniq_edgelist["BehaviorDeterminant"] = [i.lower() for i in uniq_edgelist["BehaviorDeterminant"]]
# uniq_edgelist["Studygroup"].iloc[uniq_edgelist["Studygroup"]== "NaN"] = "general population"
# uniq_edgelist["Studygroup"] = [i.lower() for i in uniq_edgelist["Studygroup"]]
# print(uniq_edgelist["Studygroup"] )
# uniq_edgelist["BehaviorOption"] = [i.lower() for i in uniq_edgelist["BehaviorOption"]]
# uniq_edgelist = uniq_edgelist.drop_duplicates()
# print("unique edgelist length",len(uniq_edgelist))
#
# uniq_edgelist[["counts_mention", "counts_articles"]] = 1
# for x in range(0,len(uniq_edgelist['BehaviorOption'])):
#     mentions = list(np.where((evidence_instances_full["BehaviorOption"] == uniq_edgelist["BehaviorOption"].iloc[x]) &
#                                                   (evidence_instances_full["BehaviorDeterminant"] == uniq_edgelist["BehaviorDeterminant"].iloc[x]) &
#                                                   (evidence_instances_full["Studygroup"] == uniq_edgelist["Studygroup"].iloc[x]) &
#                                                   (evidence_instances_full["Moderator"] == uniq_edgelist["Moderator"].iloc[x]) &
#                                                   (evidence_instances_full["sign_consist"] == uniq_edgelist["sign_consist"].iloc[x]))[0])
#     uniq_edgelist["counts_mention"].iloc[x] = len(mentions)
#     uniq_edgelist["counts_articles"].iloc[x] = len(set(evidence_instances_full["DOI"].iloc[mentions]))
#
#
# print(uniq_edgelist)
# print(uniq_edgelist[uniq_edgelist["counts_mention"]>1])
#
# def assign_keys_to_uniq_var(df, column, key_prefix):
#     uniq_val = set(uniq_edgelist[column])
#     uniq_keys = [key_prefix + str(i) for i in range(1,(len(uniq_val)+1))]
#     print("Nr of unique keys", len(uniq_keys))
#     df[key_prefix+"keys"] = [uniq_keys[i] for x in df[column] for i,f in enumerate(uniq_val) if x == f]
#     return df
#
# uniq_edgelist = assign_keys_to_uniq_var(uniq_edgelist, "BehaviorOption", "BO_")
# uniq_edgelist = assign_keys_to_uniq_var(uniq_edgelist, "BehaviorDeterminant", "BD_")
# uniq_edgelist = assign_keys_to_uniq_var(uniq_edgelist, "Studygroup", "SG_")
# uniq_edgelist = assign_keys_to_uniq_var(uniq_edgelist, "Moderator", "MO_")
#
# uniq_edgelist.to_csv("full_edgelist.csv", index=False)
#
# # Output dataframes can be read by gephi and when installing EventGraphLayout plugin transformed to bipartite graph visualization
# def prepare_output_tables_Gephi_subgraphBOBD(df, subset_keys, graph_name, Source_col, Target_col, Source_label, Target_label):
#     sub_graph_edgelist = df.iloc[[count for count, value in enumerate(df["BehaviorOption"]) if any(True for x in subset_keys if x in value)]]
#     sub_graph_edgelist.rename(columns={Source_col: 'Source', Target_col: 'Target'}, inplace=True)
#     nodes = pd.concat([sub_graph_edgelist[['Source', Source_label]].rename(columns={'Source':'Id', Source_label: 'Label' }),
#                        sub_graph_edgelist[['Target', Target_label]].rename(columns={'Target':'Id', Target_label: 'Label' })],
#                       ignore_index=True, axis=0)
#     nodes["Mode"] = 3
#     nodes["Mode"].iloc[:len(sub_graph_edgelist['Source'])] = 2
#     nodes.loc[len(nodes.index)] = ['BO_class', graph_name , 1]
#     nodes = nodes.drop_duplicates()
#     superclass_df = pd.DataFrame({"Source": ['BO_class'] * len(set(sub_graph_edgelist['Source'])),
#                                   "Target": list(dict.fromkeys(sub_graph_edgelist['Source'])),
#                                   "sign_consist": [3]* len(set(sub_graph_edgelist['Source'])),
#                                   "counts_mention": [100]* len(set(sub_graph_edgelist['Source'])),
#                                   "counts_articles": [100]* len(set(sub_graph_edgelist['Source']))})
#     sub_graph_edgelist = pd.concat([sub_graph_edgelist[['Source', 'Target', 'sign_consist', 'counts_mention', 'counts_articles']],
#                                     superclass_df], ignore_index=True, axis=0)
#     sub_graph_edgelist.to_csv(
#         (graph_name + "_edgelist.csv"), index=False)
#     nodes.to_csv((graph_name+"_nodeslist.csv"), index=False)
#
# def prepare_output_tables_Gephi_subgraph_all(df, subset_keys, graph_name):
#     sub_graph_edgelist = df.iloc[[count for count, value in enumerate(df["BehaviorOption"]) if any(True for x in subset_keys if x in value)]]
#     sub_graph_edgelist1 = sub_graph_edgelist[['BO_keys', 'BD_keys', 'sign_consist', 'counts_mention', 'counts_articles']].rename(columns={'BO_keys': 'Source', 'BD_keys': 'Target'})
#     sub_graph_edgelist2 = sub_graph_edgelist[['BD_keys', 'SG_keys', 'sign_consist', 'counts_mention', 'counts_articles']].rename(columns={'BD_keys': 'Source', 'SG_keys': 'Target'})
#     nodes = pd.concat([sub_graph_edgelist[['BO_keys', 'BehaviorOption']].rename(columns={'BO_keys':'Id', 'BehaviorOption': 'Label' }),
#                        sub_graph_edgelist[['BD_keys', 'BehaviorDeterminant']].rename(columns={'BD_keys':'Id', 'BehaviorDeterminant': 'Label' }),
#                        sub_graph_edgelist[['SG_keys', 'Studygroup']].rename(columns={'SG_keys':'Id', 'Studygroup': 'Label'})],
#                       ignore_index=True, axis=0)
#     l = len(sub_graph_edgelist.index)
#     nodes["Mode"] = 4
#     nodes["Mode"].iloc[:l] = 2
#     nodes["Mode"].iloc[l:(l*2)] = 3
#     nodes.loc[len(nodes.index)] = ['BO_class', graph_name , 1]
#     nodes = nodes.drop_duplicates()
#     superclass_df = pd.DataFrame({"Source": ['BO_class'] * len(set(sub_graph_edgelist['BO_keys'])),
#                                   "Target": list(dict.fromkeys(sub_graph_edgelist['BO_keys'])),
#                                   "sign_consist": [3]* len(set(sub_graph_edgelist['BO_keys'])),
#                                   "counts_mention": [100]* len(set(sub_graph_edgelist['BO_keys'])),
#                                   "counts_articles": [100]* len(set(sub_graph_edgelist['BO_keys']))})
#     sub_graph_edgelist = pd.concat([sub_graph_edgelist1, sub_graph_edgelist2, superclass_df], ignore_index=True, axis=0)
#     sub_graph_edgelist.to_csv(
#         (graph_name + "_edgelist_BOBDSG.csv"), index=False)
#     nodes.to_csv((graph_name+"_nodeslist_BOBDSG.csv"), index=False)
#
# # prepare_output_tables_Gephi_subgraph_all(df = uniq_edgelist, subset_keys = ["walk"],
# #                             graph_name = "walk")
#
# prepare_output_tables_Gephi_subgraph_all(df = uniq_edgelist, subset_keys = ["bike", "cycl"],
#                             graph_name = "bike")

# prepare_output_tables_Gephi_subgraphBOBD(df = uniq_edgelist, subset_keys = ["walk"],
#                             graph_name = "walk", Source_col = "BO_keys",
#                             Target_col = "BD_keys", Source_label = "BehaviorOption",
#                             Target_label = "BehaviorDeterminant")
#
# prepare_output_tables_Gephi_subgraphBOBD(df = uniq_edgelist, subset_keys = ["bike", "cycl"],
#                             graph_name = "bike", Source_col = "BO_keys",
#                             Target_col = "BD_keys", Source_label = "BehaviorOption",
#                             Target_label = "BehaviorDeterminant")
#

os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
evidence_instances_full = pd.read_csv("unique_evidence_instances_clean2_harmonised_BO.csv")
evidence_instances_full.replace({"-100": 'NaN'}, regex=False, inplace=True)
evidence_instances_full.fillna("NaN")
print(evidence_instances_full.head())

for x in list(dict.fromkeys(evidence_instances_full["BehaviorOption"])):
    print(x, len(evidence_instances_full[evidence_instances_full["BehaviorOption"]==x]))

#
# evidence_instances_full['sign_consist'] = [1 if (evidence_instances_full['stat_significance'].iloc[i] == "significant")
#                                                 or (evidence_instances_full['stat_consistency'].iloc[i] == "consistent" )
#                                            else 0 for i in range(0,len(evidence_instances_full['stat_consistency']))]
# evidence_instances_full = evidence_instances_full.drop_duplicates()
# print("edgelist length", len(evidence_instances_full))
# uniq_edgelist = evidence_instances_full[["BehaviorOption","BehaviorDeterminant", "sign_consist"]].drop_duplicates()
# print("unique edgelist length",len(uniq_edgelist))
# uniq_edgelist["BehaviorDeterminant"] = [i.lower() for i in uniq_edgelist["BehaviorDeterminant"]]
#

# uniq_edgelist[["counts_mention", "counts_articles"]] = 1
# for x in range(0,len(uniq_edgelist['BehaviorOption'])):
#     mentions = list(np.where((evidence_instances_full["BehaviorOption"] == uniq_edgelist["BehaviorOption"].iloc[x]) &
#                                                   (evidence_instances_full["BehaviorDeterminant"] == uniq_edgelist["BehaviorDeterminant"].iloc[x]) &
#                                                   (evidence_instances_full["sign_consist"] == uniq_edgelist["sign_consist"].iloc[x]))[0])
#     uniq_edgelist["counts_mention"].iloc[x] = len(mentions)
#     uniq_edgelist["counts_articles"].iloc[x] = len(set(evidence_instances_full["DOI"].iloc[mentions]))
#
# uniq_edgelist = assign_keys_to_uniq_var(uniq_edgelist, "BehaviorOption", "BO_")
# uniq_edgelist = assign_keys_to_uniq_var(uniq_edgelist, "BehaviorDeterminant", "BD_")
#
#
# # Output dataframes can be read by gephi and when installing EventGraphLayout plugin transformed to bipartite graph visualization
# def prepare_output_tables_Gephi(df, graph_name, Source_col, Target_col, Source_label, Target_label):
#     df.rename(columns={Source_col: 'Source', Target_col: 'Target'}, inplace=True)
#     nodes = pd.concat([df[['Source', Source_label]].rename(columns={'Source':'Id', Source_label: 'Label' }),
#                        df[['Target', Target_label]].rename(columns={'Target':'Id', Target_label: 'Label' })],
#                       ignore_index=True, axis=0)
#     nodes["Mode"] = 2
#     nodes["Mode"].iloc[:len(df['Source'])] = 1
#     nodes = nodes.drop_duplicates()
#     df.to_csv(
#         (graph_name + "_edgelist.csv"), index=False)
#     nodes.to_csv((graph_name+"_nodeslist.csv"), index=False)
#
# prepare_output_tables_Gephi(df = uniq_edgelist, graph_name = "harmonise_BO", Source_col = "BO_keys",
#                             Target_col = "BD_keys", Source_label = "BehaviorOption",
#                             Target_label = "BehaviorDeterminant")

#
# graph = nx.from_pandas_edgelist(df = uniq_edgelist[["BehaviorOption","BO_keys", "BehaviorDeterminant", "BD_keys", "sign_consist", "counts_articles"]], source = "BO_keys", target="BD_keys", edge_attr= ["sign_consist","counts_articles"])
#
# graph = nx.Graph()
# # Add nodes with the node attribute "bipartite"
# graph.add_nodes_from(set(uniq_edgelist["BO_keys"]), bipartite=0)
# graph.add_nodes_from(set(uniq_edgelist["BD_keys"]), bipartite=1)
# # Add edges only between nodes of opposite node sets
# # print([(a,b) for a,b in uniq_edgelist[["BO_keys", "BD_keys"]]])
# graph.add_edges_from(list(uniq_edgelist[["BO_keys", "BD_keys"]].itertuples(index=False, name=None)))
#
# nx.draw(graph)
# plt.show()
# #
# # nx.draw_kamada_kawai(graph)
# # plt.show()
#
# subset_color = ["limegreen", "darkorange"]
# color = [subset_color[data["layer"]] for v, data in graph.nodes(data=True)]
# pos = nx.multipartite_layout(graph, subset_key="layer")
# nx.draw(graph, pos, node_color=color, with_labels=False)
#
# plt.axis("equal")
#
# plt.show()


#
#
# plt.rcParams["figure.figsize"] = [7.50, 3.50]
# plt.rcParams["figure.autolayout"] = True
#
# subset_sizes = [len(set(uniq_edgelist['BehaviorOption'])),
#                 len(set(uniq_edgelist['BehaviorDeterminant'])),
#                 len(set(uniq_edgelist['Studygroup'])),
#                 len(set(uniq_edgelist['Moderator']))]
# subset_color = [
#    "gold",
#    "violet",
#    "limegreen",
#    "darkorange",
# ]
#
# def multilayered_graph(*subset_sizes):
#    extents = nx.utils.pairwise(itertools.accumulate((0,) + subset_sizes))
#    layers = [range(start, end) for start, end in extents]
#    G = nx.Graph()
#    for (i, layer) in enumerate(layers):
#       G.add_nodes_from(layer, layer=i)
#    for layer1, layer2 in nx.utils.pairwise(layers):
#       G.add_edges_from(itertools.product(layer1, layer2))
#    return G
#
# G = multilayered_graph(*subset_sizes)
# color = [subset_color[data["layer"]] for v, data in G.nodes(data=True)]
# pos = nx.multipartite_layout(G, subset_key="layer")
# nx.draw(G, pos, node_color=color, with_labels=False)
#
# plt.axis("equal")
#
# plt.show()

#
#
#
# app = Dash(__name__)
#
# app.layout = html.Div([
#     html.P("Dash Cytoscape:"),
#     cyto.Cytoscape(
#         id='cytoscape',
#         elements=[
#             {'data': {'id': 'ca', 'label': 'Canada'}},
#             {'data': {'id': 'on', 'label': 'Ontario'}},
#             {'data': {'id': 'qc', 'label': 'Quebec'}},
#             {'data': {'source': 'ca', 'target': 'on'}},
#             {'data': {'source': 'ca', 'target': 'qc'}}
#         ],
#         layout={'name': 'breadthfirst'},
#         style={'width': '400px', 'height': '500px'}
#     )
# ])
#
#
# app.run_server(debug=True)