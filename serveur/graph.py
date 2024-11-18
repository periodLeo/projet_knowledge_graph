import pandas as pd
import networkx as nx 
import matplotlib.pyplot as plt
import numpy as np
from math import ceil

from node2vec import Node2Vec
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn.manifold import TSNE


class Graph:

    def __init__(self, csvNodesFilename, csvEdgesFilename):
        nodesDf = pd.read_csv(csvNodesFilename)
        edgesDf = pd.read_csv(csvEdgesFilename)

        self.graph = nx.Graph() # create empty graph
        self.paintings_list = []

        # load paintings nodes with meta-data in our graph
        for _, row in nodesDf.iterrows():
            self.graph.add_nodes_from([(row['id'], {
                "tableaux": row['nom'],
                "peintre" : row['peintre'],
                "date"    : row['date']} )])
            self.paintings_list.append(row['id']) # create a list of paintings id

        # creates edges following using RDF triple
        for _, row in edgesDf.iterrows():
            self.graph.add_edge(row['head'], row['tail'], label=row['relation'])

        # layout used to display graph
        self.pos = nx.kamada_kawai_layout(self.graph)

    #display graph following self.pos layout
    def display_graph(self):

        labels = nx.get_edge_attributes(self.graph, 'label')
        plt.figure(figsize=(12, 10))
        nx.draw(self.graph, self.pos, with_labels=True, font_size=10, node_size=700, node_color='lightblue', edge_color='gray', alpha=0.6)
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels=labels, font_size=8, label_pos=0.3, verticalalignment='baseline')
        plt.title('Knowledge Graph')
        plt.show()

    def embedding(self):

        node2vec = Node2Vec(self.graph, dimensions=64, walk_length=30, num_walks=200, workers=4) # You can adjust these parameters
        model = node2vec.fit(window=10, min_count=1, batch_words=4) # Training the model
        self.embeddings = np.array([model.wv[node] for node in self.graph.nodes()])

        # Reduce dimensionality using t-SNE
        tsne = TSNE(n_components=2, perplexity=10, n_iter=400)
        self.embeddings_2d = tsne.fit_transform(self.embeddings)

    def clustering_dbs(self):
        
        # Perform DBSCAN clustering on node embeddings
        dbscan = DBSCAN(eps=1.0, min_samples=2) # Adjust eps and min_samples
        cluster_labels = dbscan.fit_predict(self.embeddings)
        
        # Visualize clusters
        plt.figure(figsize=(12, 10))
        nx.draw(self.graph, self.pos, with_labels=True, font_size=10, node_size=700, node_color=cluster_labels, cmap=plt.cm.Set1, edge_color='gray', alpha=0.6)
        plt.title('Graph Clustering using DBSCAN')
        plt.show()

    def clustering(self, num_clusters = 4, display = False):

        # Perform K-Means clustering on node embeddings
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        self.cluster_labels = kmeans.fit_predict(self.embeddings)

        # Visualize clusters
        if(display):
            plt.figure(figsize=(12, 10))
            nx.draw(self.graph, self.pos, with_labels=True, font_size=10, node_size=700, node_color=self.cluster_labels, cmap=plt.cm.Set1, edge_color="gray", alpha=0.6)
            plt.title('Graph Clustering using K-Means')

            plt.show()

        self.cluster_labels = self.cluster_labels[0:len(self.paintings_list)]

    # used to find starting and ending paintings in our sorted painting list
    def find_longest_path(self):
        paintings = ["",""]
        longest_path_length = 0 
        nb_paintings = len(self.paintings_list)
        for first_node in self.paintings_list[0:ceil(nb_paintings)-1]: #divided by 2 to upper value to avoid redundancy
            for second_node in self.paintings_list:
                # we want the longest of every shortest path between paintings nodes
                path_length = nx.shortest_path_length(self.graph, first_node, second_node)
                if path_length > longest_path_length:
                    longest_path_length = path_length
                    paintings[0] = first_node
                    paintings[1] = second_node

        return paintings


# if __name__ == "__main__" :
#     csvNodesFilename = "tableaux.csv"
#     csvEdgesFilename = "relations.csv"
#     g = generate_graph(csvNodesFilename, csvEdgesFilename)
#     display_graph(g)