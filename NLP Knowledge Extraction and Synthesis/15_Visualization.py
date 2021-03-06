import itertools
import matplotlib.pyplot as plt
import networkx as nx
from dash import Dash, html
import dash_cytoscape as cyto
import os
import pandas as pd
import numpy as np
os.chdir(r"C:\Users\Tabea\Documents\PhD EXPANSE\Written Paper\02- Behavioural Model paper")
evidence_instances_full = pd.read_csv("unique_evidence_instances_clean2.csv")
print(evidence_instances_full.head())
evidence_instances_full['sign_consist'] = [1 if (evidence_instances_full['stat_significance'].iloc[i] == "significant")
                                                or (evidence_instances_full['stat_consistency'].iloc[i] == "consistent" )
                                           else 0 for i in range(0,len(evidence_instances_full['stat_consistency']))]
print("edgelist length", len(evidence_instances_full))
uniq_edgelist = evidence_instances_full[["BehaviorOption","BehaviorDeterminant", "Studygroup", "Moderator", "sign_consist"]].drop_duplicates()
print("unique edgelist length",len(uniq_edgelist))

uniq_edgelist[["counts_mention", "counts_articles"]] = 1
for x in range(0,len(uniq_edgelist['BehaviorOption'])):
    mentions = list(np.where((evidence_instances_full["BehaviorOption"] == uniq_edgelist["BehaviorOption"].iloc[x]) &
                                                  (evidence_instances_full["BehaviorDeterminant"] == uniq_edgelist["BehaviorDeterminant"].iloc[x]) &
                                                  (evidence_instances_full["Studygroup"] == uniq_edgelist["Studygroup"].iloc[x]) &
                                                  (evidence_instances_full["Moderator"] == uniq_edgelist["Moderator"].iloc[x]) &
                                                  (evidence_instances_full["sign_consist"] == uniq_edgelist["sign_consist"].iloc[x]))[0])
    uniq_edgelist["counts_mention"].iloc[x] = len(mentions)
    print(set(evidence_instances_full["DOI"].iloc[mentions]))
    uniq_edgelist["counts_articles"].iloc[x] = len(set(evidence_instances_full["DOI"].iloc[mentions]))


print(uniq_edgelist)
print(uniq_edgelist[uniq_edgelist["counts_mention"]>1])


plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

subset_sizes = [len(set(uniq_edgelist['BehaviorOption'])),
                len(set(uniq_edgelist['BehaviorDeterminant'])),
                len(set(uniq_edgelist['Studygroup'])),
                len(set(uniq_edgelist['Moderator']))]
subset_color = [
   "gold",
   "violet",
   "limegreen",
   "darkorange",
]

def multilayered_graph(*subset_sizes):
   extents = nx.utils.pairwise(itertools.accumulate((0,) + subset_sizes))
   layers = [range(start, end) for start, end in extents]
   G = nx.Graph()
   for (i, layer) in enumerate(layers):
      G.add_nodes_from(layer, layer=i)
   for layer1, layer2 in nx.utils.pairwise(layers):
      G.add_edges_from(itertools.product(layer1, layer2))
   return G

G = multilayered_graph(*subset_sizes)
color = [subset_color[data["layer"]] for v, data in G.nodes(data=True)]
pos = nx.multipartite_layout(G, subset_key="layer")
nx.draw(G, pos, node_color=color, with_labels=False)

plt.axis("equal")

plt.show()

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