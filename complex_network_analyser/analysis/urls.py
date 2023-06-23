from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('general_statistical_info/', general_statistical_info, name="get general statistical information"),
    path('top_5_nodes_based_on_several_measures/', top_5_nodes_based_on_several_measures, name="get top five nodes table"),
    path('degree_distribution/', degree_distribution, name='plot degree distribution'),
    path('community_weight/', community_weight, name='get community with their weight'),
    path('node_labels/', node_labels, name='get the percent of nodes for each label'),
    path('label_clustering/', label_clustering, name='get average CC for nodes for each label'),
    path('label_degree_values/', label_degree_values, name='get degree values for nodes for each label'),
    path('label_degree_distribution/<str:label>/', label_degree_distribution, name='get the degree distribution for each label'),
]