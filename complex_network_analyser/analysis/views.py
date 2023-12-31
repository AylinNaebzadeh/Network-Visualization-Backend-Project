from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
import os
import networkx as nx
import statistics
from itertools import chain
from collections import Counter, defaultdict
from operator import itemgetter
import pickle
import json
import community as louvain_community
import EoN

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
            "avg_in_degree": float("{:.6f}".format(avg_in_degree_value)),
            "avg_out_degree": float("{:.6f}".format(avg_out_degree_value)) ,
            "density": float("{:.6f}".format(nx.density(G))),
            "diameter": network_diameter,
            "avg_shortest_path_length": float("{:.6f}".format(average_shortest_path_length)),
            "avg_cc": float("{:.6f}".format(nx.average_clustering(G))),
            "transitivity": float("{:.6f}".format(nx.transitivity(G))),
            "assortiativity": float("{:.6f}".format(nx.degree_pearson_correlation_coefficient(G))),
            "degree_centralization": float("{:.6f}".format(centralization))
        }
        print("+++++++++++++++++++++ END ++++++++++++++++++++++++")
        return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
def convert_graph(G):
    pos = nx.spring_layout(G)
    data = {"nodes": [], "edges": []}
    for node in G.nodes:
        data["nodes"].append({
            "id": str(node),
            "olabel": G.nodes[node]["label"],
            "size": 10,
            "x": pos[node][0] * 1000,
            "y": pos[node][1] * 1000
        })
    for edge in G.edges:
        data["edges"].append({
            "source": str(edge[0]),
            "target": str(edge[1]),
            "weight": 2.5,
            "startPoint": {
                "x": pos[edge[0]][0] * 1000,
                "y": pos[edge[0]][1] * 1000
            },
            "endPoint": {
                "x": pos[edge[1]][0] * 1000,
                "y": pos[edge[1]][1] * 1000
            }
        })

    return Response(data, status=status.HTTP_200_OK)

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


@api_view(['GET'])
def community_weight(request):
    if request.method == 'GET':
        G = read_data()  # function to read your network data
        if isinstance(G, nx.DiGraph):
            G = G.to_undirected()
        partition = louvain_community.best_partition(G)
        communities = []
        for com in set(partition.values()):
            communities.append(set(nodes for nodes in partition.keys() if partition[nodes] == com))
        community_weights = []
        for community in communities:
            weight = len(community)
            community_weights.append(weight)
        weight_count = Counter(community_weights)
        result = [{'#Communities': v, 'Weight': k} for k, v in weight_count.items()]
        result = sorted(result, key=lambda x: x['Weight'])
        return Response(result, status=status.HTTP_200_OK)

"""
    Label Analysis
"""

@api_view(['GET'])
def node_labels(request):
    if request.method == 'GET':
        G = read_data()  # function to read your network data
        labels = [data['label'] for n, data in G.nodes(data=True)]
        label_count = Counter(labels)
        total_count = sum(label_count.values())
        result = [{'type': k, 'value': v / total_count * 100} for k, v in label_count.items()]
        return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
def label_clustering(request):
    if request.method == 'GET':
        G = read_data()  # function to read your network data
        clustering = nx.clustering(G)
        label_clustering = defaultdict(list)
        for n, data in G.nodes(data=True):
            label = data['label']
            cc = clustering[n]
            label_clustering[label].append(cc)
        result = []
        labels = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7', 'Unknown']
        for i, label in enumerate(labels):
            cc_avg = sum(label_clustering[label]) / len(label_clustering[label])
            result.append({'key': str(i + 1), 'label': label, 'cc_avg': cc_avg})
        
        return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
def label_degree_values(request):
    if request.method == 'GET':
        G = read_data()
        degree_values = {}

        for node, degree in G.degree():
            label = G.nodes[node]['label']
            if label not in degree_values:
                degree_values[label] = []
            degree_values[label].append(degree)

        data = []
        for i, label in enumerate(sorted(degree_values.keys())):
            degrees = degree_values[label]
            average_degree = sum(degrees) / len(degrees)
            max_degree = max(degrees)
            min_degree = min(degrees)
            data.append({
                "key": str(i+1),
                "label": label,
                "avg": average_degree,
                "min": min_degree,
                "max": max_degree
            })
        return Response(data)


@api_view(['GET'])
def label_degree_distribution(request, label):
    if request.method == 'GET':
        G = read_data()

        nodes = [n for n in G.nodes() if G.nodes[n]['label'] == label]

        degree_sequence = sorted([d for n, d in G.degree(nodes)], reverse=True)
        degreeCount = Counter(degree_sequence)
        data = [{"Degree": deg, "Frequency": cnt} for deg, cnt in degreeCount.items()]

        data.sort(key=lambda x: x["Degree"])
        return Response(data)


@api_view(['GET'])
def sis_epidemic(request):
    if request.method == 'GET':
        G = read_data()
        # Set the initial conditions for the SI model
        gamma = 1.
        tau = 0.2
        initial_infected_nodes = [n for n in G.nodes() if G.nodes[n]['label'] == 'L1']  # initial set of infected nodes
        # Simulate the spread of the epidemic on the network
        t, S, I = EoN.fast_SIS(G, tau, gamma, initial_infected_nodes, tmin=0, tmax=2000)
        print(f"THE t in SIS MODEL IS: {t}")
        print(f"THE S in SIS MODEL IS: {S}")
        print(f"THE I in SIS MODEL IS: {I}")

        t_selected = [t[0]]
        S_selected = [S[0]]
        I_selected = [I[0]]
        for i in range(1, len(t)):
            if t[i] - t_selected[-1] >= 50:
                t_selected.append(int(t[i]))
                S_selected.append(S[i])
                I_selected.append(I[i])

        data = []
        for i in range(len(t_selected)):
            data.append({
                "name": "S",
                "t": str(t_selected[i]),
                "count": S_selected[i]
            })

        for i in range(len(t_selected)):
            data.append({
                "name": "I",
                "t": str(t_selected[i]),
                "count": I_selected[i]
            })
        return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def sir_epidemic(request):
    if request.method == 'GET':
        G = read_data()
        p = 0.5  # probability of infection
        r = 0.5  # probability of recovery
        initial_infected_nodes = [n for n in G.nodes() if G.nodes[n]['label'] == 'L1']  # initial set of infected nodes

        # Simulate the spread of the epidemic on the network
        t, S, I, R = EoN.fast_SIR(G, p, r, initial_infecteds=initial_infected_nodes, tmax=2000, tmin=0)
        print(f"THE t in SIR MODEL IS: {t}")

        t_selected = [t[0]]
        S_selected = [S[0]]
        I_selected = [I[0]]
        R_selected = [R[0]]

        for i in range(1, len(t)):
            if t[i] - t_selected[-1] >= 50:
                t_selected.append(int(t[i]))
                S_selected.append(S[i])
                I_selected.append(I[i])
                R_selected.append(R[i])
        
        data = []
        for i in range(len(t)):
            data.append({
                "name": "S",
                "t": str(t[i]),
                "count": S[i]
            })

        for i in range(len(t)):
            data.append({
                "name": "I",
                "t": str(t[i]),
                "count": I[i]
            })

        for i in range(len(t)):
            data.append({
                "name": "R",
                "t": str(t[i]),
                "count": R[i]
            })

        return Response(data, status=status.HTTP_200_OK)
