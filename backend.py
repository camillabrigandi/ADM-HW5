import heapq
from class_graph import graph
import pickle
import networkx as nx 
import numpy as np
from tabulate import tabulate

# LOAD NEEDED DATA 
file = open("citation.pkl",'rb')
citation_data = pickle.load(file)
file.close()

file = open("collaboration.pkl",'rb')
collaboration_data = pickle.load(file)
file.close()

# SOME BACKEND FUNCTIONS

# Functionality 2.1
def graph_features(graph, graph_name):
    #n nodes
    num_nodes = len(graph.nodes())
    #n edges 
    num_edges = len(graph.edges())
    #density 
    density = nx.density(graph)
    #distribution degree
    degree_distribution = list(dict(nx.degree(graph)).values())
    #average degree
    average_degree = np.mean(degree_distribution)
    
    #hubs
    #define percentile 95 percentile
    percentile_95 = np.percentile(degree_distribution, 95)
    #take the hubs
    hubs = [node for node, degree in dict(nx.degree(graph)).items() if degree > percentile_95]

    #sparse or dense
    #formula 
    threshold = len(graph.edges()) / (len(graph.nodes()) * (len(graph.nodes()) -1)  )
    is_dense = "Dense" if density > threshold else "Sparse"

    #return the result ()
    report = f"Graph Features Report for '{graph_name}':\n"
    report += f"Number of Nodes: {num_nodes}\n"
    report += f"Number of Edges: {num_edges}\n"
    report += f"Graph Density: {density}\n"
    report += f"Degree Distribution: {degree_distribution}\n"
    report += f"Average Degree: {average_degree}\n"
    report += f"Graph Hubs: {hubs}\n"
    report += f"Graph Density Status: {is_dense}\n"

    return report

##### Functionality 2 : Node's contribution ######
def centrality(graph, node, graph_name):
    #Betweenness
    betweenness = nx.betweenness_centrality(graph)[node]
    #PageRank
    pagerank = nx.pagerank(graph)[node]
    #closeness centrality
    closeness_centrality = nx.closeness_centrality(graph)[node]
    #degree centrality
    degree_centrality = nx.degree_centrality(graph)[node]

    #results
    data = [
        ["Betweenness", betweenness],
        ["Pagerank", pagerank],
        ["Closeness Centrality", closeness_centrality],
        ["Degree Centrality", degree_centrality]
    ]
    
    table = tabulate(data, headers=["Feature", "Value"], tablefmt="fancy_grid")
    report = f"Graph Features Report for '{graph_name}':\n{table}"

    return report
# Functions needed to extract top N authors and papers ----NEEDED IN FUNCTIONALITIES 2.3, 2.4, 2.5
def extract_topN(G, N, flag):

    # Function to retrieve the top N papers wrt number of citations
    def topN_papers(G, N):
        # create list of tuples (node, indegree(node)) for heapq
        nodes_indegree = []
        for node in G.nodes: 
            nodes_indegree.append((node, G.indegree(node)))
        
        # retrieve topN papers
        nlargest = heapq.nlargest(N, nodes_indegree, key= lambda t: t[1])

        # return only the nodes with the most  number of citations
        return [t[0] for t in nlargest]

    # Function to retrieve top N authors wrt their total number of publications
    def topN_authors(G, N):

        # initialize empty list 
        n_publications = []

        # Retrieve all the edges' weigths of the graph
        all_weigths = G.edges_attributes['weigths']

        # retrieve number of publications for each node
        #  dictionary {node: {Neighbor: edge between neighbor and node} for all the neighbors of the node}
        all_nodes_neigh_withedges = dict({node: G.neighborhood_withedges_onlyundirected(node) for node in G.nodes})
        
        for node in G.nodes: 
            # Retrieve info on the current node
            current_node_info = all_nodes_neigh_withedges[node]

            # Construct dictionary {Neighbor: weigth of the edge between neighbor and node} for all the neighbors of the node:
            # Initialize dictionary with all the weigths set to 0
            neigh_weigths_dict = dict.fromkeys(current_node_info.keys(), 0)
            # Update the dictionary with the correct weights
            neigh_weigths_dict.update({neigh: all_weigths[current_node_info[neigh]] for neigh in current_node_info if current_node_info[neigh] in all_weigths})

            # Update the list of the number of publications for each node
            n_publications.append( ( node, sum( neigh_weigths_dict.values() ) ) )

        # Retrieve top N authors wrt their total number of publications
        nlargest = heapq.nlargest(N, n_publications, key= lambda t: t[1])

        # Return only the nodes (without number of publications)
        return [t[0] for t in nlargest]


    if flag == 'authors':
        topN = topN_authors(G, N)
    elif flag == 'papers': 
        topN = topN_papers(G, N)
    else:
        return 'invalid flag'
    
    return topN


##### Functionality 3 : Shortest path ########
def shortest_path(G, source, sink):    
# Initialize dictionary containing shortest paths to each node
    paths = dict.fromkeys(G.nodes, [])
    paths.update({source: [[]]})

    #initialize BFS' exploration dictionary using distances from the source
    distances = dict.fromkeys(G.nodes, float('inf'))

    # set distance to 0 for the first node and add it to a queue
    distances.update({source: 0})
    q = [source]

    while q != []:
        # Extract node to explore from the queue
        parent = q.pop(0)

        # Retrieve neighborhood and "connecting edges"
        neighborhood_edges = G.neighborhood_withedges_onlyundirected(parent)
        for u in neighborhood_edges.keys():
            # If the node has never been visited, set distance from the starting node
            if distances[u] == float('inf'):
                distances[u] = distances[parent] + G.edges_attributes['weigths'][ neighborhood_edges[u] ]

                q.append(u)
                
            # Update number of shortest paths to u 
            if distances[u] == distances[parent] + G.edges_attributes['weigths'][ neighborhood_edges[u] ]:
                paths.update({u: paths[u] + [path + [(parent, u)]] for path in paths[parent]})
    
    if (distances[sink] < float('inf')):
        return (distances[sink] < float('inf')), distances[sink], paths[sink][0]
    else:
        return (distances[sink] < float('inf')), distances[sink], []

def shortestpath_sequence(sequence: list, first_node, last_node, N, G_data=collaboration_data):
    # extract graph class instance from the data in input 
    G = graph(G_data['nodes'], G_data['edges'], {'weigths': G_data['weigths']}, G_data['dir'])

    # extract top N authors 
    topN_list = extract_topN(G, N, 'authors')

    # subgraph of the top N authors
    G_N = G.extract_subgraph(topN_list)


    # Initialize path and path cost
    total_path = []
    total_cost = 0

    sequence = [first_node] + sequence + [last_node]
    
    # check the existence of path P_i and compute shortest path and shortest path's cost if it exists
    for i in range(len(sequence) - 1):
        connected, path_cost, path = shortest_path(G_N, sequence[i], sequence[i+1])
        if not connected: 
            return "There is no such path."
        
        # Update path and path's cost if the graph is connected
        total_path += path
        total_cost += path_cost
    
    return total_cost, total_path

### Functionality 4: Disconnect two nodes in a graph #####

def checkpath_DFS(G, source, sink):
    
    # initialize empty path
    path = []

    # set 'visited' to false for every node in the graph
    visited = dict.fromkeys(G.nodes, False)

    # initilize a stack with only the source and set visited to true for source
    S = [source]
    #visited[source] = True

    while S and not visited[sink]:
        u = S.pop(0)
        # Check if u is already been visited
        if not visited[u]:
            # If not, explore u's neighborhood
            neighborhood = G.get_neighborhood(u)
            if neighborhood == []:
                return visited[sink], path

            for neighbour in neighborhood: 
                if G.edges_attributes['capacity'][(u, neighbour)] > 0 :
                    S.insert(0, neighbour)
            
            # last neighbour inserted will be the first explored at next step 
            path.append( ((u, neighbour), G.edges_attributes['capacity'][(u, neighbour)]) )
            
            # Check if we arrived to the sink 
            if neighbour == sink:
                visited[sink] = True
            
            # Now u has been visited
            visited[u] = True

    # If there's a path from source to sink, visited[sink] will be true, elseway false 
    return visited[sink], path

def FordFulkerson(G, source, sink):
    
    # Construct residual graph from the starting one
    G_res = G.copy().to_directed()
    
    # initialize the flow to zero for all the edges
    original_edges = list(G_res.edges)
    flow = dict.fromkeys(original_edges, 0)
    G_res.edges_attributes.update({'flow': flow})

    # initialize capacity (starting weigths)
    capacity = G_res.edges_attributes['weigths']
    G_res.edges_attributes.update({'capacity': capacity})

    while  checkpath_DFS(G_res, source, sink)[0]:

        # find a simple sink-source path 
        _, path = checkpath_DFS(G_res, source, sink)
        
        # obtain bottleneck on the path
        bottleneck = min([edge[1] for edge in path]) # edge(1) is the capacity of the edge
        
        # augment capacity 
        for edge in path:
            # Update flow
            flow.update({edge[0]: flow[edge[0]] + bottleneck})
            flow.update({edge[0][::-1] : -flow[edge[0]]})

            # Update capacity
            capacity.update({edge[0]: capacity[edge[0]] - flow[edge[0]]}) 
            capacity.update({edge[0][::-1] : capacity[edge[0][::-1]] + flow[edge[0]]  })

        # Update G-res
        G_res.edges_attributes.update({'capacity': capacity})
        G_res.edges_attributes.update({'flow': flow})
        G_res.remove_edges([ edge for edge in capacity if capacity[edge] <= 0])


    return G_res


def node_connected_component(G, node):
        
        # Initialize visited dictionary
        visited = dict.fromkeys(G.nodes, False)
        
        # intialize empty component
        component = []

        # initilize a stack with only the node in input 
        S = [node]

        while S != []:
            # select first element of the stack
            u = S.pop(0)

            # Check if u is already been visited
            if not visited[u]:
                # If not, add u to the current component and "explore" u's neighborhood
                component.append(u)
                
                neighborhood = G.get_neighborhood(u)
                for neighbour in neighborhood:
                    S.insert(0, neighbour)
                
                visited.update({u: True})
                
        
        return component


def disconnect(N, authorA, authorB, G_data=collaboration_data):
    # extract graph class instance from the data in input 
    G = graph(G_data['nodes'], G_data['edges'], {'weigths': G_data['weigths']}, G_data['dir'])

    # extract top N authors 
    topN_list = extract_topN(G, N, 'authors')

    # subgraph of the top N authors
    G_N = G.extract_subgraph(topN_list)
    
    # Run FordFulkerson algorithm 
    G_res_final = FordFulkerson(G_N, authorA, authorB)

    # Construct the cut (G_authorA, G_authorB)
    nodes_authorA = node_connected_component(G_res_final, authorA)
    nodes_authorB = list(set(G_N.nodes).difference(set(nodes_authorA)))


    # Cut capacity 
    cutset = [ edge for edge in G_N.edges if edge[0] in nodes_authorA and edge[1] in nodes_authorB ] + [ edge for edge in G_N.edges if edge[1] in nodes_authorA and edge[0] in nodes_authorB ] 
    cutcapacity = sum([G_N.edges_attributes['weigths'][edge] for edge in cutset])
   
    return cutcapacity, cutset, len(cutset)

####### Functionality 5: Community detection #########
# Function that computes Edge Betweenes Centrality
def EBC(G):

    def EBC_fixedstart(G, starting_node):
        # Initialize dictionary containing shortest paths to each node
        paths = dict.fromkeys(G.nodes, [])
        paths.update({starting_node: [[]]})

        # Initialize dictionary with the weigths for all the nodes(needed to compute EBC)
        nodes_weigths = {node: 0 for node in G.nodes}
        
        #initialize BFS' exploration dictionary using distances from the source
        distances = dict.fromkeys(G.nodes, float('inf'))

        # set distance to 0 for the first node and add it to a queue
        distances.update({starting_node: 0})
        q = [starting_node]

        while q != []:
            # Extract node to explore from the queue
            parent = q.pop(0)

            neighborhood = G.get_neighborhood(parent)
            for u in neighborhood:
                # If the node has never been visited, set distance from the starting node
                if distances[u] == float('inf'):
                    distances[u] = distances[parent] + 1
                    q.append(u)
                
                # Update number of shortest paths to u 
                if distances[u] == distances[parent] + 1:
                    nodes_weigths.update({u: nodes_weigths[u] + 1})
                    paths.update({u: paths[u] + [path + [(parent, u)]] for path in paths[parent]})


        # Initialize a dictionary containing 0 as EBS for each edge
        EBC_partial_dict = dict.fromkeys(G.edges, 0)
    
        M = max(distances.values())
        # If there is more than one connected component in the graph, analyze only the nodes in the connected components of the starting node 
        if M == float('inf'):
            inf_dist = [ node for node in distances if distances[node] == float('inf') ]
            for node in inf_dist: 
                distances.pop(node)

            # Update maximum value of the distance using only nodes in the connected component we have 
            M = max(distances.values())
            
        # Construct a dictionary with the levels created from BFS
        levels = list(range(1, max(distances.values())))
        #level_nodes = [[v for v in distances if distances[v] == level] for level in levels]
        level_dict = dict(zip(levels, [[v for v in distances if distances[v] == level] for level in levels]))

        # modify node weigth of the starting node 
        nodes_weigths.update({starting_node: 1}) 
        
        # compute EBC contribution of the paths starting from this node for each edge
        for i in levels[::-1]:
            current_level = level_dict[i]
            for node in current_level:
                for path in paths[node]:
                    current_edge = path[i-1]
                    edge_weigth = (nodes_weigths[current_edge[1]]/nodes_weigths[current_edge[0]])
                    EBC_partial_dict.update({current_edge : (1 + EBC_partial_dict[current_edge]) * edge_weigth})
                        
                    for edge in path[:i-2]:
                        EBC_partial_dict.update({edge: EBC_partial_dict[edge] + edge_weigth})
                        
        return EBC_partial_dict
        

    # Initialize dictionary with total EBC values
    EBC = dict.fromkeys(G.edges, 0)
    
    # Compute the partial contribution of the EBC from every possible starting node
    for node in G.nodes:
        partial_EBC = EBC_fixedstart(G, node)

        # Update EBC dictionary
        for edge in partial_EBC:
            EBC.update({edge: EBC[edge] + partial_EBC[edge]})
    
    return EBC


# Returns the number of connected components and a list containig all the components (their nodes)
def connected_components(G):
    # Initialize visited parameters for DFS 
    visited = dict.fromkeys(G.nodes, False)

    # Initialize empty list for components
    components = []

    # Iterate on the nodes in the graph to retrieve all the nodes connected to it (if node not already visited)
    def find_connected_component_DFS(node, component):
        # initilize a stack with only the node in input and set visited to true for this node
        S = [node]

        while S != []:
            # select first element of the stack
            u = S.pop(0)

            # Check if u is already been visited
            if not visited[u]:
                # If not, add u to the current component and "explore" u's neighborhood
                component.append(u)

                neighborhood = G.get_neighborhood(u)
                for neighbour in neighborhood :
                    S.insert(0, neighbour)
                
                visited.update({u: True})
                
        
        return component, visited


    while False in visited.values():
        for node in G.nodes:
            # If u has not still be assigned to a component
            if not visited[node]:
                # initialize empty component 
                component = []

                # Compute connected component of node
                component, visited = find_connected_component_DFS(node, component)

                # Add the current component to the list of all connected components
                components.append(component)

    return len(components), components


def extract_communities(N, paper_1, paper_2, G_data = citation_data):
    # extract graph class instance from the data in input 
    G = graph(G_data['nodes'], G_data['edges'], dict(), G_data['dir'])

    # extract top N papers 
    topN_list = extract_topN(G, N, 'papers')

    # subgraph of the top N papers
    G_N = G.extract_subgraph(topN_list)

    # work subgraph
    Gwork = G_N.copy()

    if connected_components(G_N)[0] == N:
        return 'Increase N to be able to find communities', G_N


    # Initial number of connected components of the graph
    nComponents_init, ccs = connected_components(G_N)
    nComponents = nComponents_init


    # Initialize value of edges to drop to 0 
    n_edgestodrop = 0
    it = 1 
    while nComponents <= nComponents_init:
        # Calculate Edge Betweeness Centrality for the graph of top N papers
        EBC_dict = EBC(Gwork)

        # Retrive max centrality
        max_centrality = max(EBC_dict.values())

        # Identify edges with max centrality 
        edges_to_drop = [edge for edge in EBC_dict if EBC_dict[edge] == max_centrality]
        n_edgestodrop += len(edges_to_drop)

        # Remove the edges with maximum centrality 
        Gwork.remove_edges(edges_to_drop)
        nComponents, current_components = connected_components(Gwork)
    
   
    # Check if paper_1 and paper_2 belong to the same community
    same_component = False

    for community in current_components:
        # Find paper_1's connected component 
        if paper_1 in community:
            # Check if paper_2 is in the same connected component
            same_component = bool(paper_2 in community)
            break
    
    return n_edgestodrop, current_components, same_component