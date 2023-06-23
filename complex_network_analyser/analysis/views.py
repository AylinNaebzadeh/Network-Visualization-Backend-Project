from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import pandas as pd

def read_data():
    data = pd.read_excel('./data/edges.xlsx')
    G = nx.from_pandas_edgelist(data, 'sourceNodeId', 'targetNodeId', create_using=nx.DiGraph())
    
    labels_df = pd.read_excel('nodes.xlsx')

    labels_dict = labels_df.set_index('NodeId')['Labels'].to_dict()

    nx.set_node_attributes(G, labels_dict, 'label')
    return G

@api_view(['GET'])
def general_statistical_info(request):
    if request.method == 'GET':
        G = read_data()
        print(f"THE G IS {G}")

        avg_in_degree_value = sum(d for n, d in G.in_degree()) / float(number_of_nodes)
        print(f"The average in degree in the graph network is: {avg_in_degree_value}")

        avg_out_degree_value = sum(d for n, d in G.out_degree()) / float(number_of_nodes)
        print(f"The average out degree in the graph network is: {avg_out_degree_value}")

        network_diameter = max([max(j.values()) for (i,j) in nx.shortest_path_length(G)])

        path_lengths = (y.values() for (x, y) in nx.shortest_path_length(G))
        average_shortest_path_length = statistics.mean(chain.from_iterable(path_lengths))

        N = G.order()
        sum_in_degrees = sum(d for n, d in G.in_degree())
        max_in = max(d for n, d in G.in_degree())
        centralization = float(N * max_in - sum_in_degrees) / (N - 1) ** 2

        result = {
            "nodes_count": G.number_of_nodes(),
            "edges_count": G.number_of_edges(),
            "avg_in_degree": avg_in_degree_value,
            "avg_out_degree": avg_out_degree_value,
            "density": nx.density(G),
            "diameter": network_diameter,
            "avg_shortest_path_length": average_shortest_path_length,
            "avg_cc": nx.average_clustering(G),
            "transitivity": nx.transitivity(G),
            "assotativity": nx.degree_pearson_correlation_coefficient(G),
            "degree_centralization": centralization
        }
        return Response(result, status=status.HTTP_200_OK)