from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
import os
import networkx as nx
import statistics
from itertools import chain
from collections import Counter
from operator import itemgetter
import pickle
import json


def read_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    edges_path = os.path.join(base_dir, 'data', 'edges.xlsx')
    nodes_path = os.path.join(base_dir, 'data', 'nodes.xlsx')

    data = pd.read_excel(edges_path)
    G = nx.from_pandas_edgelist(data, 'sourceNodeId', 'targetNodeId', create_using=nx.DiGraph())

    labels_df = pd.read_excel(nodes_path)
    labels_dict = labels_df.set_index('NodeId')['Labels'].to_dict()
    nx.set_node_attributes(G, labels_dict, 'label')
    return G


@api_view(['GET'])
def general_statistical_info(request):
    if request.method == 'GET':
        G = read_data()
        print(f"THE G IS {G}")

        number_of_nodes = G.number_of_nodes()
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


@api_view(['GET'])
def top_5_nodes_based_on_several_measures(request):
    if request.method == 'GET':
        G = read_data()
        # Calculate degree centrality
        degree_centrality = nx.degree_centrality(G)

        degree_centrality_sorted = [] 
        for node in sorted(degree_centrality, key=degree_centrality.get, reverse=True)[:5]:
            degree_centrality_sorted.append({'node': node, 'value': degree_centrality[node]})

        print(f'****************** TOP 5 NODES BY DEGREE CENTRALITY: {degree_centrality_sorted}')

        # Calculate closeness centrality
        closeness_centrality = nx.closeness_centrality(G)

        closeness_centrality_sorted = [] 
        for node in sorted(closeness_centrality, key=closeness_centrality.get, reverse=True)[:5]:
            closeness_centrality_sorted.append({'node': node, 'value': closeness_centrality[node]})

        print(f'****************** TOP 5 NODES BY CLOSENESS CENTRALITY: {closeness_centrality_sorted}')
        
        # Calculate betweenness centrality
        betweenness_centrality = nx.betweenness_centrality(G)

        betweenness_centrality_sorted = []
        for node in sorted(betweenness_centrality, key=betweenness_centrality.get, reverse=True)[:5]:
            betweenness_centrality_sorted.append({'node': node, 'value': betweenness_centrality[node]})

        print(f'****************** TOP 5 NODES BY BETWEENNESS CENTRALITY: {betweenness_centrality_sorted}')

        # Calculate eigenvector centrality
        eigenvector_centrality = nx.eigenvector_centrality(G)

        eigenvector_centrality_sorted = []  
        for node in sorted(eigenvector_centrality, key=eigenvector_centrality.get, reverse=True)[:5]:
            eigenvector_centrality_sorted.append({'node': node, 'value': eigenvector_centrality[node]})

        print(f'****************** TOP 5 NODES BY EIGENVECTOR CENTRALITY: {eigenvector_centrality_sorted}')

        result = {}
        result = []
        centrality_measures = [
            ('Degree Centrality', degree_centrality_sorted),
            ('Closeness Centrality', closeness_centrality_sorted),
            ('Betweenness Centrality', betweenness_centrality_sorted),
            ('Eigenvector Centrality', eigenvector_centrality_sorted)
        ]

        for i, (measure_name, measure_data) in enumerate(centrality_measures):
            measure_dict = {
                'key': str(i + 1),
                'feature': measure_name
            }
            for j, data in enumerate(measure_data):
                measure_dict[f'id{j + 1}'] = data['node']
                measure_dict[f'value{j + 1}'] = data['value']
            result.append(measure_dict)

        return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
def degree_distribution(request):
    if request.method == 'GET':
        G = read_data()  # function to read your network data
        degree_sequence = [d for n, d in G.degree()]
        degree_count = Counter(degree_sequence)
        result = [{'Degree': k, 'Frequency': v} for k, v in sorted(degree_count.items())]
        total_frequency = sum([item['Frequency'] for item in result])
        if total_frequency == G.number_of_nodes():
            print("The sum of frequencies is equal to the number of nodes")
        else:
            print("The sum of frequencies is not equal to the number of nodes")
        return Response(result, status=status.HTTP_200_OK)