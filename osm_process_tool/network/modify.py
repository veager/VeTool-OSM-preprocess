import networkx as nx
from typing import Any, Iterable, Union


def remove_node_edge_attrs(
    G: nx.Graph,
    node_attrs: Union[str, Iterable[str]],
    edge_attrs: Union[str, Iterable[str]]
) -> nx.Graph:
    """
    Return a shallow copy of the graph with specified node- and edge-level
    attributes removed.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph or nx.MultiGraph or nx.MultiDiGraph
        The input graph.
    node_attrs : str or iterable of str
        Node attribute name(s) to remove.
    edge_attrs : str or iterable of str
        Edge attribute name(s) to remove.

    Returns
    -------
    G2 : same type as G
        A shallow copy of G where each specified node attribute has been
        popped from every node, and each specified edge attribute has been
        popped from every edge.
    """
    # Create a shallow copy to avoid mutating the original
    G2 = G.copy()

    # Normalize inputs to lists
    if isinstance(node_attrs, str):
        node_attrs = [node_attrs]
    if isinstance(edge_attrs, str):
        edge_attrs = [edge_attrs]

    # Remove node attributes
    for _, attrs in G2.nodes(data=True):
        for attr_name in node_attrs:
            if attr_name in attrs:
                attrs.pop(attr_name, None)

    # Remove edge attributes
    for _, _, attrs in G2.edges(data=True):
        for attr_name in edge_attrs:
            if attr_name in attrs:
                attrs.pop(attr_name, None)

    return G2
# ======================================================================================
def remove_edge_by_attr_value(
    G: nx.Graph,
    attr_name: str,
    attr_values: Union[Any, Iterable[Any]],
    remove_isolated_nodes: bool = True
) -> nx.Graph:
    """
    Return a shallow copy of G with edges removed whose attribute `attr_name`
    matches any of `attr_values`. Optionally drop any nodes that become isolated.

    Parameters
    ----------
    G : nx.Graph or nx.DiGraph or nx.MultiGraph or nx.MultiDiGraph
        The input graph.
    attr_name : str
        The edge-attribute key to inspect.
    attr_values : single value or iterable of values
        If an edge’s `attr_name` is equal to any of these, that edge is removed.
    remove_isolated_nodes : bool, default True
        If True, remove any nodes that have degree==0 after edge removal.

    Returns
    -------
    G2 : same type as G
        A shallow copy of G with the specified edges (and optionally
        resultant isolated nodes) removed.
    """
    # 1) Make a shallow copy so original graph is untouched
    G2 = G.copy()

    # 2) Normalize attr_values to a set for efficient membership testing
    if not isinstance(attr_values, Iterable) or isinstance(attr_values, (str, bytes)):
        values = {attr_values}
    else:
        values = set(attr_values)

    # 3) Identify edges to remove
    to_remove = []
    # For Graph/DiGraph, edges(data=True) yields (u, v, data)
    for u, v, data in G2.edges(data=True):
        if data.get(attr_name) in values:
            to_remove.append((u, v))

    # 4) Remove those edges
    G2.remove_edges_from(to_remove)

    # 5) Optionally remove nodes that are now isolated
    if remove_isolated_nodes:
        isolated = list(nx.isolates(G2))
        if isolated:
            G2.remove_nodes_from(isolated)

    return G2
# =====================================================================================