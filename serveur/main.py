from graph import Graph
import numpy as np
import networkx as nx
import copy

csvNodesFilename = "tableaux.csv"
csvEdgesFilename = "relations.csv"
nb_clusters = 5

g = Graph(csvNodesFilename, csvEdgesFilename)

paints = copy.deepcopy(g.paintings_list)

g.graph.remove_nodes_from(["tableau","peintre"])
g.embedding()
g.clustering(num_clusters = nb_clusters ,display=False)


furthest_nodes = g.find_longest_path()
starting_node = furthest_nodes[0]
ending_node = furthest_nodes[1]

# loop to associate paintings to specified cluster
paints_clusterized = []
labels = copy.deepcopy(g.cluster_labels).tolist()

for i in range(nb_clusters):
    paints_clusterized.append([])
    nb_i_iter = labels.count(i) # number of paintings in current cluster
    for j in range(nb_i_iter):
        index = labels.index(i)
        paints_clusterized[i].append(paints[index])
        labels.pop(index)
        paints.pop(index)

# sort nodes by distances 
paints = copy.deepcopy(g.paintings_list)
paints_sorted = []

while(paints != []):
    closest_interest = min(paints, key=lambda node: nx.shortest_path_length(g.graph, source=starting_node, target=node))
    paints_sorted.append(closest_interest)
    starting_node = closest_interest
    paints.pop(paints.index(starting_node))

print(paints_sorted)

# Add cluster labels as node attributes
for node, label in zip(g.paintings_list, g.cluster_labels):
    g.graph.nodes[node]['cluster'] = label

# calculate centroids of clusters
# commented because not used
# centroids = {label: nx.kamada_kawai_layout(g.graph, scale=2)[node] for label, node in zip(set(g.cluster_labels), g.graph.nodes)}

# func to know in wich cluster a specified painting is locateds
def get_cluster_from_painting(painting, cluster_list):
    for i in range(len(cluster_list)):
        if painting in cluster_list[i]:
            return i 

    return -1 # return -1 if not in any cluster

# sort clusters
musee_clusters = []
while(paints_sorted != []):
    next_painting = paints_sorted[0]
    cluster_id = get_cluster_from_painting(next_painting, paints_clusterized)
    musee_clusters.append(paints_clusterized[cluster_id])
    for e in paints_clusterized[cluster_id]:
        paints_sorted.pop(paints_sorted.index(e))
    print(musee_clusters[-1])

print("Sorted Clusters : ",musee_clusters)

# un-comment to check order visually
#g.clustering(num_clusters = nb_clusters ,display=True)
