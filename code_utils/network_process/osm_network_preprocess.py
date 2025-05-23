
import tqdm
import pyproj
import networkx as nx
import pandas as pd
import geopandas as gpd

from shapely.ops import transform
from shapely.geometry import Point, LineString, MultiLineString

from typing import Union, Any, Dict, Tuple, List, Optional
from shapely.geometry.base import BaseGeometry


def remove_nodes_outside_boundary(
    G: nx.MultiDiGraph,
    projected_crs: Union[str, int, Dict],
    boundary: BaseGeometry,
    node_attr_x: str = "x",
    node_attr_y: str = "y",
    source_crs: Union[str, int, Dict] = "EPSG:4326",
) -> nx.MultiDiGraph:
    """
    Remove nodes from a copy of G whose point (x, y) falls outside `boundary`.

    Parameters
    ----------
    G : nx.MultiDiGraph
        Input graph; nodes must carry lon/lat under `node_attr_x`/`node_attr_y`.
    projected_crs : str|dict|int
        CRS of the boundary polygon (e.g. "EPSG:3414").
    boundary : BaseGeometry
        Shapely polygon in `projected_crs` defining the valid area.
    node_attr_x : str
        Node‐attribute name for longitude (default "x").
    node_attr_y : str
        Node‐attribute name for latitude (default "y").
    source_crs : str|dict|int
        CRS of node lon/lat coordinates (default WGS84: "EPSG:4326").

    Returns
    -------
    nx.MultiDiGraph
        A copy of G with out‐of‐boundary nodes removed.
    """
    assert G.is_multigraph(), "Input graph must be a networkx.MultiDiGraph"

    # 1) Duplicate the graph so the original remains unchanged
    G2 = G.copy()

    # 2) Build a transformer to reproject from source_crs → projected_crs
    transformer = pyproj.Transformer.from_crs(
        crs_from = pyproj.CRS.from_user_input(source_crs),
        crs_to = pyproj.CRS.from_user_input(projected_crs),
        always_xy = True)

    # 3) Identify nodes to remove
    nodes_to_remove = []
    for node, data in tqdm.tqdm(G2.nodes(data=True), desc="Removing nodes outside boundary"):

        lon = data.get(node_attr_x)
        lat = data.get(node_attr_y)

        # 3a) If either coordinate is missing, mark for removal
        if (lon is None) or (lat is None):
            nodes_to_remove.append(node)
            continue

        # 3b) Reproject the lon/lat point into the projected CRS
        x_proj, y_proj = transformer.transform(lon, lat)
        pt = Point(x_proj, y_proj)

        # 3c) If the point lies outside the boundary polygon, mark for removal
        if not boundary.contains(pt):
            nodes_to_remove.append(node)

    # 4) Remove all marked nodes at once
    G2.remove_nodes_from(nodes_to_remove)

    # 5)
    G2.graph.update({'crs' : projected_crs})

    return G2
# =============================================================================================================
def reproject_network_geometry(
    G: nx.MultiDiGraph,
    projected_crs: Union[str, dict, int],
    source_crs: Union[str, dict, int] = "EPSG:4326",
    edge_attr_geom: str = "geometry",
    edge_attr_len: str = "length_m",
    edge_non_geom_add: bool = True,
    node_attr_x: str = "x",
    node_attr_y: str = "y",
    node_attr_proj_x: str = "proj_x",
    node_attr_proj_y: str = "proj_y",
    node_non_geom_remove: bool = True,
) -> nx.MultiDiGraph:
    """
    Reproject node coordinates and edge geometries, then compute & store edge lengths.

    Steps:
      1) Duplicate G so the original remains unchanged.
      2) Build a PyProj transformer from source_crs → projected_crs.
      3) Reproject each node’s (lon, lat) into the projected CRS.
      4) Optionally remove nodes missing valid coordinates.
      5) For each edge:
         • If it has a LineString/MultiLineString, reproject that geometry.
         • Otherwise, build a straight LineString between its two reprojected nodes.
         • Overwrite or add the geometry attribute as requested.
         • Compute its length (in metres) and store it.

    Parameters
    ----------
    G : nx.MultiDiGraph
        Input graph; nodes must have lon/lat under node_attr_x/node_attr_y.
    projected_crs : str | dict | int
        Target CRS for output geometries (e.g. "EPSG:3414").
    source_crs : str | dict | int, default "EPSG:4326"
        CRS of input node lon/lat (default WGS84).
    edge_attr_geom : str, default "geometry"
        Key in edge data for input/output Shapely geometry.
    edge_attr_len : str, default "length_m"
        Key in edge data under which to store length in metres.
    edge_non_geom_add : bool, default True
        If True, add a straight-line fallback geometry for edges missing valid geom.
    node_attr_x : str, default "x"
        Key in node data for longitude.
    node_attr_y : str, default "y"
        Key in node data for latitude.
    node_attr_proj_x : str, default "proj_x"
        Key in node data under which to store reprojected x.
    node_attr_proj_y : str, default "proj_y"
        Key in node data under which to store reprojected y.
    node_non_geom_remove : bool, default True
        If True, remove nodes missing valid coords (and their edges).

    Returns
    -------
    A copy of G with:
      - projected node coords under node_attr_proj_x/node_attr_proj_y,
      - edge geometries in projected_crs under edge_attr_geom,
      - edge lengths (m) under edge_attr_len,
      - graph‐level 'crs' set to projected_crs.
    """
    assert G.is_multigraph(), "Input graph must be a networkx.MultiDiGraph"

    # 1) Work on a shallow copy to preserve the original graph
    G2 = G.copy()


    # 2) Prepare transformer: lon/lat (source_crs) → projected_crs
    transformer = pyproj.Transformer.from_crs(
        pyproj.CRS.from_user_input(source_crs),
        pyproj.CRS.from_user_input(projected_crs),
        always_xy = True)


    # 3) Reproject node coordinates
    removed_node_list = []
    for n, node_data in tqdm.tqdm(G2.nodes(data=True), desc="Step 1: reprojecting nodes"):

        node_data_new = node_data.copy()

        x_origin = node_data_new.get(node_attr_x)
        y_origin = node_data_new.get(node_attr_y)
        if (x_origin is None) or (y_origin is None):
            removed_node_list.append(n)
            continue

        # project node coordinates
        x_proj, y_proj = transformer.transform(x_origin, y_origin)

        # update node attributes
        node_data_new.update({
            node_attr_proj_x: x_proj,
            node_attr_proj_y: y_proj})

        # update the node attributes
        nx.set_node_attributes(G2, {n: node_data_new})

    # 4) Remove nodes lacking valid coords (and their incident edges)
    if node_non_geom_remove and (len(removed_node_list) > 0):
        G2.remove_nodes_from(removed_node_list)
        print(f"Removed nodes with invalid coordinates: {len(removed_node_list)}")


    # 5) compute edge lengths
    for u, v, k, edge_data in tqdm.tqdm(G2.edges(keys=True, data=True), desc="Step 2: reprojecting edge"):

        edge_data_new = edge_data.copy()
        edge_geom = edge_data_new.get(edge_attr_geom)

        # skip non‐line geometries
        if isinstance(edge_geom, (LineString, MultiLineString)):
            # valid geometry: project it
            proj_geom = transform(transformer.transform, edge_geom)
            # Overwrite the geometry attribute with the reprojected version
            edge_data_new.update({
                edge_attr_len:  proj_geom.length,
                edge_attr_geom: proj_geom,})

        else:
            # Add geometry only if specified
            if edge_non_geom_add:

                # fallback to straight line between the two nodes
                x1, y1 = G2.nodes[u].get(node_attr_proj_x), G2.nodes[u].get(node_attr_proj_y)
                x2, y2 = G2.nodes[v].get(node_attr_proj_x), G2.nodes[v].get(node_attr_proj_y)
                proj_geom = LineString([(x1, y1), (x2, y2)])

                edge_data_new.update({
                    edge_attr_len : proj_geom.length,
                    edge_attr_geom: proj_geom})

            else:
                # skip this edge
                continue

        # update the edge attributes
        nx.set_edge_attributes(G2, {(u, v, k): edge_data_new})

    # 6) Append the projected CRS to the graph
    G2.graph.update({'crs': projected_crs})

    return G2
# =============================================================================================================
def collapse_multidigraph_to_graph(
    G_multi: nx.MultiDiGraph,
    weight: str
) -> nx.Graph:
    """
    Collapse a directed MultiDiGraph into a simple undirected Graph by:
      1. Copying over all node attributes.
      2. For each unordered pair of nodes, selecting the parallel edge with minimal `weight`.
      3. Copying *all* attributes of that minimal-weight edge.
      4. Dropping self-loops.

    Parameters
    ----------
    G_multi : nx.MultiDiGraph
        Input directed multigraph (may have parallel edges).
    weight : str
        Name of the edge-attribute whose numeric value is used to pick the minimal edge.

    Returns
    -------
    nx.Graph
        An undirected graph with:
          - the same nodes (and their attributes) as G_multi,
          - at most one edge per node pair, carrying the attributes of the minimal-weight edge.
    """
    assert G_multi.is_multigraph(), "Input graph must be a networkx.MultiDiGraph"

    # 0) Prepare the new simple Graph
    G = nx.Graph()

    # 1) Copy nodes and their attribute dicts
    #    We .copy() each attrs to avoid mutating the original
    for node, attrs in G_multi.nodes(data=True):
        G.add_node(node, **attrs.copy())

    # 2) Find the minimal-weight edge for each unordered node pair
    #    best[(a, b)] = (min_weight, attributes_of_that_edge)
    best: Dict[Tuple[Any, Any], Tuple[float, Dict[str, Any]]] = {}

    # No edge key for this multigraph
    for u, v, k, data in tqdm.tqdm(G_multi.edges(keys=True, data=True), desc="Selecting minimal edges"):
        # 2a) Skip self-loops
        if u == v:
            continue

        # 2b) Order the pair so (a,b) == (min(u,v), max(u,v))
        a, b = (u, v) if u <= v else (v, u)

        # 2c) Extract and coerce the weight to float (fallback to +inf)
        w_raw = data.get(weight, None)
        try:
            w_val = float(w_raw)
        except (TypeError, ValueError):
            w_val = float("inf")

        # 2d) Keep this edge if it's the first seen or has a smaller weight
        prev = best.get((a, b))
        if prev is None or w_val < prev[0]:
            best[(a, b)] = (w_val, data.copy())

    # 3) Add the chosen minimal-weight edges to G
    for (a, b), (_, edge_attrs) in best.items():
        G.add_edge(a, b, **edge_attrs)

    return G
# =============================================================================================================
def process_isolated_nodes(
    G: nx.Graph,
    threshold: Optional[float] = None,
    node_attr_x: str = "proj_x",
    node_attr_y: str = "proj_y",
    edge_attr_geom: str = "geometry",
    edge_attr_len: str = "length_m",
) -> nx.Graph:
    """
    Connect or remove isolated nodes based on a distance threshold.

    Parameters
    ----------
    G : nx.MultiDiGraph
        Graph whose nodes carry projected coordinates under 'proj_x' and 'proj_y'.
    threshold : float or None
        If float: maximal distance within which to connect an isolated node
        to its nearest non-isolated node. If None: simply drop all isolated nodes.

    Returns
    -------
    nx.MultiDiGraph
        A new graph where:
          - When threshold is None: all degree-0 nodes are removed.
          - Otherwise:
              • Each degree-0 node within `threshold` of its nearest neighbor
                is connected by a straight-line edge.
              • Any isolated node farther than `threshold` (or lacking coords) is dropped.
    """
    # Work on a shallow copy so the original G is untouched
    G2 = G.copy()

    # Identify all isolated nodes
    isolated_nodes = list(nx.isolates(G2))

    # 1) If no isolated nodes, nothing to do
    if not isolated_nodes:
        print('No isolated nodes to process.')
        return G2  # nothing to do

    # If no threshold specified, drop all isolated nodes
    if threshold is None:
        G2.remove_nodes_from(isolated_nodes)
        print('Dropped all isolated nodes.')
        return G2


    # Nearest joint between isolated and network nodes
    # 1) Prepare the pool of non-isolated nodes to connect to
    non_isolated = list(set(list(G2.nodes())) - set(isolated_nodes))

    # 2) Convert node list to GeoSeries
    # -----------------------------------------------
    def _convert_nodes_to_geoseries(node_list):
        df = pd.DataFrame({
            'node_id':   node_list,
            node_attr_x: [G2.nodes[node].get(node_attr_x) for node in node_list],
            node_attr_y: [G2.nodes[node].get(node_attr_y) for node in node_list]
        }).dropna(subset=[node_attr_x, node_attr_y], how='any')
        # Convert to GeoSeries
        return gpd.GeoDataFrame(
            index = df['node_id'].values,
            data = df['node_id'].values,
            columns = ['node_id'],
            geometry = gpd.points_from_xy(df[node_attr_x], df[node_attr_y]),
            crs = G2.graph.get("crs", None))
    # --------------------------------------------
    iso_node_gdf = _convert_nodes_to_geoseries(isolated_nodes)
    noniso_node_gdf = _convert_nodes_to_geoseries(non_isolated)

    # 3) Perform a nearest‐neighbor spatial join (with max_distance)
    joined_node = gpd.sjoin_nearest(
        left_df = iso_node_gdf, right_df = noniso_node_gdf,
        how = 'inner',
        max_distance = threshold, distance_col = 'distance_m',
        lsuffix = 'left', rsuffix = 'right')

    # print(joined_node.columns)

    # 4) For each isolated node, either connect or drop
    for idx, row in tqdm.tqdm(joined_node.iterrows(), desc="Connecting isolated nodes (total edges: {})".format(len(joined_node))):
        iso_node = row['node_id_left']
        nbr_node = row['node_id_right']
        dist = row['distance_m']

        # 4a) If the distance is within threshold, connect with a straight line
        G2.add_edge(iso_node, nbr_node, **{
            edge_attr_geom: LineString([
                iso_node_gdf['geometry'].loc[iso_node],
                noniso_node_gdf['geometry'].loc[nbr_node]]),
            edge_attr_len: dist,})

    # 5) Remove all remaining isolated nodes
    remaining_isolated = list(nx.isolates(G2))
    if remaining_isolated:
        G2.remove_nodes_from(remaining_isolated)
        print(f'Dropped remaining isolated nodes: {len(remaining_isolated)}')

    return G2
# ============================================================================================================
def graph_to_geodataframe(
    G: nx.Graph,
    crs: str,
    node_attr_x: str = "x",
    node_attr_y: str = "y",
    edge_attr_geom: str = "geometry",
) -> Tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """
    Extract nodes and edges from a NetworkX graph as GeoDataFrames.

    Parameters
    ----------
    G : nx.Graph | nx.DiGraph | nx.MultiGraph | nx.MultiDiGraph
        Input graph. Nodes must carry attributes `node_attr_x`, `node_attr_y`
        for their coordinates. Edges should carry a Shapely geometry under
        `edge_attr_geom` if present.
    node_attr_x : str
        Node attribute key for x-coordinate (longitude or projected x).
    node_attr_y : str
        Node attribute key for y-coordinate (latitude or projected y).
    edge_attr_geom : str
        Edge attribute key for Shapely geometry.
    crs : str
        Coordinate reference system to assign to both GeoDataFrames.

    Returns
    -------
    node_gdf : geopandas.GeoDataFrame
        GeoDataFrame of nodes with columns:
        - index: node ID
        - all node attributes
        - geometry: Point(x, y)
    edge_gdf : geopandas.GeoDataFrame
        GeoDataFrame of edges with columns:
        - source, target (and key if multigraph)
        - all edge attributes
        - geometry: the edge geometry
    """
    # Nodes
    node_df = pd.DataFrame.from_dict(
        dict(G.nodes(data=True)), orient='index')

    node_gdf = gpd.GeoDataFrame(
        node_df,
        geometry = gpd.points_from_xy(node_df[node_attr_x], node_df[node_attr_y]),
        crs = crs)

    # Edges
    edge_df = nx.to_pandas_edgelist(
        G, source='source', target='target', edge_key='edge_key')

    edge_gdf = gpd.GeoDataFrame(
        edge_df,
        geometry = edge_df[edge_attr_geom],
        crs = crs)

    return node_gdf, edge_gdf
# ============================================================================================================
def convert_network_geometry_attr_to_wkt(
    G: Union[nx.Graph, nx.DiGraph],
    node_attr: str = "geometry",
    edge_attr: str = "geometry",
) -> Union[nx.Graph, nx.DiGraph]:
    """
    Convert Shapely geometry attributes on nodes and edges to WKT strings.

    Parameters
    ----------
    G : Graph-like
        A NetworkX graph (Graph, DiGraph).
    node_attr : str, optional
        Name of the node attribute containing a Shapely geometry (default: 'geometry').
    edge_attr : str, optional
        Name of the edge attribute containing a Shapely geometry (default: 'geometry').
    inplace : bool, optional
        If True, modify the input graph in place and return it; otherwise, work on a copy (default: False).

    Returns
    -------
    Graph-like
        A graph where any node or edge attributes matching `node_attr` or `edge_attr`
        have been converted from Shapely geometries to their WKT representations.
    """
    # Determine working graph
    G2 = G.copy()

    # Convert node geometries
    if node_attr is not None:
        for node, data in tqdm.tqdm(G2.nodes(data=True), desc="Updating node geometries"):
            if node_attr in data:
                geom = data.get(node_attr)
                if isinstance(geom, BaseGeometry):
                    data.update({node_attr: geom.wkt})

    # Convert edge geometries
    if edge_attr is not None:
        for _, _, data in tqdm.tqdm(G2.edges(data=True), desc="Updating edge geometries"):
            if edge_attr in data:
                geom = data.get(edge_attr)
                if isinstance(geom, BaseGeometry):
                    data.update({edge_attr: geom.wkt})

    return G2
# ============================================================================================================