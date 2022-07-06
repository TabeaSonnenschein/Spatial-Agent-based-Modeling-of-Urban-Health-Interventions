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
evidence_instances_full['sign_consist'] = [1 if (evidence_instances_full['stat_significance'].iloc[i] == "significant")or (evidence_instances_full['stat_consistency'].iloc[i] == "consistent" ) else 0 for i in range(0,len(evidence_instances_full['stat_consistency']))]
# x = list(np.where((evidence_instances_full['stat_significance'] == "significant")|(evidence_instances_full['stat_consistency'] == "consistent" ))[0])
# evidence_instances_full.iloc[x, 'sign_consist'] = 1
clean_edgelist = evidence_instances_full[["BehaviorOption","BehaviorDeterminant", "Studygroup", "Moderator", "sign_consist"]]
print(clean_edgelist)

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

subset_sizes = [5, 5, 4, 3, 2, 4, 4, 3]
subset_color = [
   "gold",
   "violet",
   "violet",
   "violet",
   "violet",
   "limegreen",
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




app = Dash(__name__)

app.layout = html.Div([
    html.P("Dash Cytoscape:"),
    cyto.Cytoscape(
        id='cytoscape',
        elements=[
            {'data': {'id': 'ca', 'label': 'Canada'}},
            {'data': {'id': 'on', 'label': 'Ontario'}},
            {'data': {'id': 'qc', 'label': 'Quebec'}},
            {'data': {'source': 'ca', 'target': 'on'}},
            {'data': {'source': 'ca', 'target': 'qc'}}
        ],
        layout={'name': 'breadthfirst'},
        style={'width': '400px', 'height': '500px'}
    )
])


app.run_server(debug=True)