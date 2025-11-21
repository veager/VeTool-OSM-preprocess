import pandas as pd
import networkx as nx
from typing import Union


def get_giant_component(
    graph: Union[nx.Graph, nx.DiGraph]
) -> Union[nx.Graph, nx.DiGraph]:
    """
    Return the largest (weakly) connected component of the graph.

    For directed graphs, uses weakly connected components;
    for undirected graphs, uses connected components.

    Parameters
    ----------
    graph : networkx.Graph or networkx.DiGraph
        Input graph.

    Returns
    -------
    networkx.Graph or networkx.DiGraph
        Subgraph corresponding to the largest component (copied).
    """
    # Choose component function based on graph type
    if graph.is_directed():
        components = nx.weakly_connected_components(graph)
    else:
        components = nx.connected_components(graph)

    # Identify the largest component
    largest = max(components, key=len)

    # Return a copy of the subgraph for the largest component
    return graph.subgraph(largest).copy()
# ============================================================================================
# def _get_giant_component(graph):
#
#     if nx.is_directed(graph):
#         giant_com = sorted(nx.weakly_connected_components(graph), key=len, reverse=True)
#     elif not nx.is_directed(graph):
#         giant_com = sorted(nx.connected_components(graph), key=len, reverse=True)
#
#     giant_com = graph.subgraph(giant_com[0])
#
#     return graph
# # ============================================================================================
def print_graph_info(graph: Union[nx.Graph, nx.DiGraph]) -> None:
    """
    Print summary statistics of the graph and its largest component.

    Parameters
    ----------
    graph : networkx.Graph or networkx.DiGraph
        Input graph.
    """
    print('\nIs directed: ', graph.is_directed(),
        '\nNo. of nodes: ', graph.number_of_nodes(),
        '\nNo. of edges: ', graph.number_of_edges(),
        '\nNo. of isolated nodes: ', len(list(nx.isolates(graph))),
        '\nNo. of self-loops: ', nx.number_of_selfloops(graph))

    # Largest component stats
    giant = get_giant_component(graph)
    # Get the giant component
    print('\nThe giant component: ',
        '\n\tNo. of nodes: ', giant.number_of_nodes(),
        '\n\tNo. of edges: ', giant.number_of_edges())

    # Component counts
    if graph.is_directed():
        count = nx.number_weakly_connected_components(graph)
        print(f"\nNo. of weakly connected components: {count}")
    else:
        count = nx.number_connected_components(graph)
        print(f"No. of connected components: {count}")
# ============================================================================================
#%%
def compute_travel_statistics(
    graph: Union[nx.Graph, nx.DiGraph]
) -> pd.DataFrame:
    """
    Compute travel statistics (distance, duration, speed) for each edge in the graph.

    Assumes each edge has 'distance' and 'travel_duration' attributes.

    Parameters
    ----------
    graph : networkx.Graph or networkx.DiGraph
        Input graph with required edge attributes.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing 'distance', 'duration', and computed 'speed'.
    """
    # Extract edge attributes
    distances = list(nx.get_edge_attributes(graph, 'distance').values())
    durations = list(nx.get_edge_attributes(graph, 'travel_duration').values())

    # Build DataFrame and compute speed
    df = pd.DataFrame({'distance': distances, 'duration': durations})
    df['speed'] = df['distance'].div(df['duration'])
    return df
# ============================================================================================