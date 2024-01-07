import matplotlib.pyplot as plt
from prettytable import PrettyTable
import networkx as nx
import pickle
import ipywidgets as widgets
from IPython.display import display, clear_output
import json
import numpy as np

from class_graph import graph
import backend

# Load data that is in input as default 
file = open("citation.pkl",'rb')
citation_data = pickle.load(file)
file.close()

file = open("collaboration.pkl",'rb')
collaboration_data = pickle.load(file)
file.close()

file = open("graphdata.pkl", 'rb')
graph_data = pickle.load(file)
file.close()

# Citation graph (as networkx graph)
file = open("citation_graph.json", 'r') 
graph_data = json.load(file)
file.close()
#create graph from the data -- citation graph 
G = nx.node_link_graph(graph_data)

# Collaboration graph (as networkx graph)
# Read the graph data from the JSON file
file = open("collaboration_graph.json", 'r')
graph_data = json.load(file)
file.close()
#create graph from the data -- collaboration graph 
N = nx.node_link_graph(graph_data)

# Dictionaries for visualization
file = open('papersd.pkl', 'rb')
papers_dict = pickle.load(file)
file.close()

file = open('authorsd.pkl', 'rb')
authors_dict = pickle.load(file)
file.close()

# Functionality 2.3 - Shortest path
#function that will output the result in a very pretty way :)
def plot_shortest_path(result):
    # Extract data from the result
    total_cost, shortest_path = result

    # Create a PrettyTable for the cost
    cost_table = PrettyTable(["Cost"])
    cost_table.add_row([total_cost])

    # Create a PrettyTable for the nodes and path
    path_table = PrettyTable(["Edge", "From Node", "To Node"])
    for edge in shortest_path:
        path_table.add_row([f"({edge[0]}, {edge[1]})", edge[0], edge[1]])

    # Print the tables
    print("Cost Table:")
    print(cost_table)
    
    print("\nPath Table:")
    print(path_table)


#function for the visualisation of the graph
def shortestpath_visualize_result(result, G_data=collaboration_data):
    G = graph(G_data['nodes'], G_data['edges'], {'weigths': G_data['weigths']}, G_data['dir'])
    cost, edges = result
    #create it
    G_result = nx.Graph()
    #add nodes and edges
    for edge in edges:
        G_result.add_edge(edge[0], edge[1])

    #plot
    pos = nx.spring_layout(G_result)
    nx.draw(G_result, pos, with_labels=True, font_weight='bold', node_color='skyblue', node_size=1000, font_size=8, edge_color='gray', width=2)
    plt.title(f"Graph Visualization\nTotal Cost: {cost}")
    plt.show()



# Functionality 2.4: Disconnect two nodes in a graph

def disconnect_frontend(N, authorA, authorB, G_data=collaboration_data):
    print("Please wait: this functionality could take some minutes.")
    
    # Get results from the backend function
    cutcapacity, cutset, n_edges = backend.disconnect(N, authorA, authorB, G_data=collaboration_data)

    # Print number of links that should be disconnected (and the capacity of the cut)
    print('The number of the links that should be disconnected is', n_edges, 'and the capacity of the cutset retrieved is', cutcapacity)

    # Plot the original graph
    # STEP 1: retrieve data to construct the original graph as a networkx graph
    # extract graph class instance from the data in input 
    G = graph(G_data['nodes'], G_data['edges'], {'weigths': G_data['weigths']}, G_data['dir'])
    # extract top N authors 
    topN_list = backend.extract_topN(G, N, 'authors')
    # subgraph of the top N authors (used to retrieve list of nodes, edges and attributes to construct networkx graph for visualization)
    G_N = G.extract_subgraph(topN_list)

    # STEP 2: Construct networkx Graph instance of the original graph
    Gauthors_original = nx.Graph()
    Gauthors_original.add_nodes_from(G_N.nodes)
    Gauthors_original.add_edges_from(G_N.edges)
    nx.set_edge_attributes(Gauthors_original, G_N.edges_attributes['weigths'], name='weigths')
    
    # STEP 3: Plot the original graph
    global authors_dict
    plt.clf()
    positions = nx.circular_layout(Gauthors_original)
    nx.draw(Gauthors_original, pos= positions, node_color = 'skyblue')
    nx.draw_networkx_edge_labels(Gauthors_original, pos= positions, edge_labels = nx.get_edge_attributes(Gauthors_original, 'weigths') )
    nx.draw_networkx_labels(Gauthors_original, pos= positions, labels = {n:lab for n,lab in authors_dict.items() if n in positions})

    plt.title('Original Graph')
    plt.show()

    # Plot the graph after removing the links and identify the two nodes

    # STEP 1: crte a copy of the orignal networkx graph and remove the edes in the cutset
    Gauthors_final = Gauthors_original.copy()
    Gauthors_final.remove_edges_from(cutset)

    # Create a list with all the nodes except from authorA and authorB (used for plot)
    nodes_withouth_sourcesink = G_N.nodes
    nodes_withouth_sourcesink.remove(authorA)
    nodes_withouth_sourcesink.remove(authorB)
    

    # Plot the final graph (identification of source and sink is made by changing their color in the plot)
    
    plt.clf()
    positions = nx.circular_layout(Gauthors_final)
    nx.draw_networkx_nodes(Gauthors_final, pos= positions, nodelist = [authorA, authorB], node_color = 'darkblue')
    nx.draw_networkx_nodes(Gauthors_final, pos= positions, nodelist = nodes_withouth_sourcesink,  node_color = 'skyblue')
    nx.draw_networkx_edges(Gauthors_final, pos= positions)
    nx.draw_networkx_labels(Gauthors_final, pos= positions, labels = {n:lab for n,lab in authors_dict.items() if n in positions})
    nx.draw_networkx_edge_labels(Gauthors_final, pos= positions, edge_labels = nx.get_edge_attributes(Gauthors_final, 'weigths') )
    
    plt.axis('off')
    plt.title('Final Graph')
    plt.show()



# Functionality 2.5 : Community detection
def communities_frontend(N, paper_1, paper_2, G_data = citation_data):

    
    # TRetrieve data from the backend function
    n_edgestodrop, current_components, same_component = backend.extract_communities(N, paper_1, paper_2, G_data = citation_data)

    # Print the number of links that should be removed to have the communities
    print( 'The numbers of edges that has to be dropped to form communities is:', n_edgestodrop )

    # Table with communities and paper of each community

    global papers_dict
    communities_table = PrettyTable(["Community nodes"])
    for community in current_components: 
        communities_table.add_row( [[ papers_dict[node] for node in community ]])
    
    # Print the tables
    print('Communities Table: each row of the following table contains the papers in a "community" ')
    print(communities_table)
    


    # Original graph
    # STEP 1: retrieve data to construct the original graph as a networkx graph
    # extract graph class instance from the data in input 
    G = graph(G_data['nodes'], G_data['edges'], dict(), G_data['dir'])
    # extract top N papers 
    topN_list = backend.extract_topN(G, N, 'papers')
    # subgraph of the top N papers
    G_N = G.extract_subgraph(topN_list)

    # STEP 2: Construct networkx Graph instance of the original graph
    Gpapers_original = nx.MultiDiGraph()
    Gpapers_original.add_nodes_from(G_N.nodes)
    Gpapers_original.add_edges_from(G_N.edges)
    
    # STEP 3: Plot the original graph
    plt.clf()
    positions = nx.circular_layout(Gpapers_original)
    nx.draw(Gpapers_original, pos = positions, with_labels = True, node_color='skyblue')
    
    plt.title('Original Graph')
    plt.show()


    # Final graph and community/communities of Paper_1 and Paper_2
    # STEP1: identify the edges removed while creating the communities

    # Retrieve original connected components in the graph
    _, original_ccs = backend.connected_components(G_N)

    # To find the removed edges, compare the original connected components with the ones retrieved from the communities
    original_ccs_set = [component for component in original_ccs]
    current_components_set = [component for component in current_components]

    new_components = [component for component in current_components_set if component not in original_ccs_set ]
   

    # Removed edges are the ones between the newo components
    removed_edges = [edge for edge in G_N.edges if (edge[0] in new_components[0] and edge[1] in new_components[1]) or (edge[1] in new_components[0] and edge[0] in new_components[1]) ]
    
    # STEP2: crate a copy of the original graph and remove the edges removed to create communities
    Gpapers_final = Gpapers_original.copy()
    Gpapers_final.remove_edges_from(removed_edges)
    
    # Identify components of the two papers wrt same component
    if same_component: 
        # find component with the two papers
        for component in current_components:
            if paper_1 in component:
                papers_component= component
                break

        # Plot final graph
        plt.clf()
        positions = nx.circular_layout(Gpapers_final)
        nx.draw_networkx_nodes(Gpapers_final, pos=positions, nodelist = papers_component, node_color = 'darkblue')
        nx.draw_networkx_nodes(Gpapers_final, pos=positions, nodelist = [node for node in G_N.nodes if node not in papers_component], node_color='skyblue')
        nx.draw_networkx_edges(Gpapers_final)
        nx.draw_networkx_labels(Gpapers_final, pos = positions)

        plt.axis('off')
        plt.title('Final Graph')
        plt.show()
    else: 
        # Find components of the two papers 
        for component in current_components:
            if paper_1 in component:
                component1 = component
            if paper_2 in component:
                component2 = component

        # Plot the final graph
        plt.clf()
        positions = nx.circular_layout(Gpapers_final)
        nx.draw_networkx_nodes(Gpapers_final, pos= positions, nodelist = component1 , node_color = 'violet')
        nx.draw_networkx_nodes(Gpapers_final, pos=positions,  nodelist = component2 , node_color = 'darkblue')
        nx.draw_networkx_nodes(Gpapers_final, pos=positions, nodelist = [node for node in G_N.nodes if node not in component1 and node not in component2], node_color='skyblue')
        nx.draw_networkx_edges(Gpapers_final, pos= positions)
        nx.draw_networkx_labels(Gpapers_final, pos = positions)
        
        plt.axis('off')
        plt.title('Final Graph')
        plt.show()

    
    

# VISUALIZATION SYSTEM
    
###############VISUALISATION##############################
# HOME PAGE
#create the two buttons of the home page
btn_visualization_system = widgets.Button(description="Visualization System", button_style='info')
btn_exit = widgets.Button(description="Exit", button_style='danger')

#define what the exit button does 
def exit_clicked(b):
    clear_output(wait=True)
    print("System exited")
    # You can add additional cleanup or exit code here

#define what the visualisation system button does
def display_buttons(b=None):
    clear_output(wait=True)
    display(btn_visualization_system, btn_exit)


#create the other buttons to show in the second page: Graph selection or return
btn_collaboration_graph = widgets.Button(description="Collaboration Graph", button_style='primary')
btn_citation_graph = widgets.Button(description="Citation Graph", button_style='success')
btn_return = widgets.Button(description="Return", button_style='warning')

#define the second page
def visualization_system_clicked(b):
    clear_output(wait=True)
    print("Select the graph you want to investigate:")
    #display buttons of the second page
    display(btn_collaboration_graph, btn_citation_graph, btn_return)

#if clicked, do this.(home page buttons)
btn_exit.on_click(exit_clicked)
btn_visualization_system.on_click(visualization_system_clicked)


#create buttons of the THIRD PAGE (graph-specific)
# Functionality 1    
btn_table = widgets.Button(description="General Information", button_style='primary')
btn_hubs = widgets.Button(description="Graph's Hubs", button_style='primary')
btn_citation_received = widgets.Button(description="Citations Received Plot", button_style='primary')
btn_citation_gived = widgets.Button(description="Citations Gived Plot", button_style='primary')
btn_collaborations = widgets.Button(description="Collaborations Plot", button_style='primary')
# Functionality 2
btn_centrality = widgets.Button(description="Centrality measures", button_style='primary')   
# Functionality 3 (only on collaboration graph)
btn_shortestpath = widgets.Button(description="Shortest path", button_style='primary')
# Functionality 4 (only on collaboration graph)
btn_disconnect = widgets.Button(description="Disconnect two nodes", button_style='primary')
# Functionality 5 (only on citation graph)
btn_communities =  widgets.Button(description="Detect communities", button_style='primary')
# Retrun Button
btn_return = widgets.Button(description="Return", button_style='warning')

# Define second page buttons functionalities
selected_graph = None
#define first button graph
def display_graph_options(b):
    clear_output(wait=True)
    # Save which graph has been selected
    global selected_graph
    selected_graph = b.description
    if selected_graph == 'Collaboration Graph':
        display(btn_table, btn_hubs, btn_collaborations, btn_centrality, btn_shortestpath, btn_disconnect, btn_return)
    elif selected_graph == "Citation Graph":
        display(btn_table, btn_hubs, btn_citation_received, btn_citation_gived, btn_centrality, btn_communities, btn_return )

#define the return button 
def return_clicked(b):
    clear_output(wait=True)
    display_buttons()  


#when the button is clicked, do its functions
btn_collaboration_graph.on_click(display_graph_options)
btn_citation_graph.on_click(display_graph_options)
btn_return.on_click(return_clicked)


# THIRD PAGE : selection of the functionality to perform, given the selected graph

# Define buttons functionalities 

# Buttons corresponding to functionality 1 of th hw
def graph_info_functionalities(b):
    clear_output(wait=True)

    global selected_graph
    if selected_graph == 'Collaboration Graph': 
        graph = N
        graph_name = "Collaboration Graph"
    elif selected_graph == 'Citation Graph':
        graph = G
        graph_name = 'Citation Graph'
    
    

#create the button to display the general info 
def table_clicked(b):
    clear_output(wait=True)

    global selected_graph
    if selected_graph == 'Collaboration Graph': 
        graph = N
        graph_name = "Collaboration Graph"
    elif selected_graph == 'Citation Graph':
        graph = G
        graph_name = 'Citation Graph'
    clear_output(wait=True)
    print(backend.graph_features(graph, graph_name))

#display hubs
def hubs_clicked(b):
    clear_output(wait=True)
    global selected_graph
    if selected_graph == 'Collaboration Graph': 
        graph = N
        graph_name = "Collaboration Graph"
    elif selected_graph == 'Citation Graph':
        graph = G
        graph_name = 'Citation Graph'


    hubs = nx.degree(graph)
    hubs = [node for node, degree in hubs if degree > 0]  
    print(f"Graph Hubs for '{graph_name}':\n{hubs}")
    
#plot of the citation received
def citation_received_clicked(b):
    clear_output(wait=True)
    #it will be visible only for the citation graph, so to remind the user it is a graph-specific feature, I remind it here
    print("\033[91;1mWARNING: THIS FEATURE IS AVAILABLE ONLY FOR THE CITATION GRAPH!!!\033[0m")
    #exploit the structure of the graph
    in_degrees = dict(G.in_degree())
    in_degree_values = list(in_degrees.values())

    #plot
    plt.figure(figsize=(16, 6))
    plt.hist(in_degree_values, bins=100, color='red', alpha=0.7)        
    plt.title('Citations Received by Papers')
    plt.xlabel('In-Degree (Number of Citations Received)')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.xlim(0,70)
    plt.show()

#plot the citation gived
def citation_gived_clicked(b):
    clear_output(wait=True)
    #it will be visible only for the citation graph, so to remind the user it is a graph-specific feature, I remind it here
    print("\033[91;1mWARNING: THIS FEATURE IS AVAILABLE ONLY FOR THE CITATION GRAPH!!!\033[0m")        #exploit the structure of the greph 
    out_degrees = dict(G.out_degree())
    out_degree_values = list(out_degrees.values())

    #plot
    plt.figure(figsize=(16, 6))
    plt.hist(out_degree_values, bins="auto", color='r', alpha=0.7)
    plt.title('Citations Given by Papers')
    plt.xlabel('Out-Degree (Number of Citations Given)')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.xlim(0,43)
    plt.xticks(np.arange(0, 43))
    plt.show()

#plot collaborations
def collaborations_clicked(b):
    clear_output(wait=True)
    #it will be visible only for the collaboration graph, so to remind the user it is a graph-specific feature, I remind it here
    print("\033[91;1mWARNING: THIS FEATURE IS AVAILABLE ONLY FOR THE COLLABORATION GRAPH!!!\033[0m")
    degrees = dict(N.degree())
    #I retrieve only the top 50 as the graph is pretty big
    top_nodes = sorted(degrees, key=degrees.get, reverse=True)[:50]
    
    plt.figure(figsize=(16, 6))
    plt.hist([degrees[node] for node in top_nodes], bins=100, color='red', alpha=0.7)
    plt.title('N collaborations for Top 50 Authors')
    plt.xlabel('N')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.xticks(np.arange(235, 261))  
    plt.xlim(240,260)
    plt.show()

#if clicked, do this
btn_table.on_click(table_clicked)
btn_hubs.on_click(hubs_clicked)
btn_citation_received.on_click(citation_received_clicked)
btn_citation_gived.on_click(citation_gived_clicked)
btn_collaborations.on_click(collaborations_clicked)
btn_return.on_click(return_clicked)

# Functionality of the centrality button 
#create buttons for the input part
input_node = widgets.IntText(value=1, description='Node Number:', style={'description_width': 'initial'})
btn_return_result = widgets.Button(description="Submit", button_style='warning')

def centrality_needinput(b):
    clear_output(wait=True)
    display(input_node, btn_return_result)

btn_centrality.on_click(centrality_needinput)

#when the result is inputed, first, print a message to ask some patient,
#then, check which graph has been selected
def centrality_clicked(b): 
    clear_output(wait=True)
    node = input_node.value
    print("Retrieving results; this could take some minutes, please wait...")
    global selected_graph
    #if citation graph has been selected
    if selected_graph == "Citation Graph":
        #perfrom the function with the correct graph 
        result = backend.centrality(G, node, "Citation Graph")
    #if collaboration graph has been selected
    elif selected_graph == "Collaboration Graph":
        #perfrom the function with the correct graph 
        result = backend.centrality(N, node, "Collaboration Graph")

    #show results 
    print(f"Result for node {node} in the {selected_graph}:")
    print(result)

# Button action
btn_return_result.on_click(centrality_clicked)


# Shortest path functionality

# Create buttons for the input part
input_node1 = widgets.IntText(value=1, description='Starting Node:', style={'description_width': 'initial'})
input_node2 = widgets.IntText(value=1, description='Destination Node:', style={'description_width': 'initial'})
input_sequence = widgets.Text(value='', description='Sequence:', style={'description_width': 'initial'})  # Updated input widget
input_N = widgets.IntText(value=1, description='N authors:', style={'description_width': 'initial'})
btn_submit_sp = widgets.Button(description="Submit", button_style='success')

def shortestpath_input(b):
    clear_output(wait=True)
    # Print name and instructions on what to do
    print("Please input the two nodes you want to calculate the shortest path:")
    print("Please input the sequence authors with comma separated values:")
    print("Please input number of top authors whose data should be considered (integer):")
    
    # Display input buttons and sequence input on the same line
    display(widgets.HBox([input_node1, input_node2, input_sequence, input_N]))
    
    # Display buttons below the input widgets
    display(widgets.HBox([btn_submit_sp]))

# Get input for the shortest path function
btn_shortestpath.on_click(shortestpath_input)

# When the result is inputted, first, print a message to ask some patience,
# then, check which graph has been selected
def shortestpath_return_result_clicked(b):
    clear_output(wait=True)
    node1 = input_node1.value
    node2 = input_node2.value
    N = input_N.value
    seq_input = [int(x.strip()) for x in input_sequence.value.split(',')]
    print("Retrieving results; this could take some minutes, please wait...")

    # Results
    result = backend.shortestpath_sequence(seq_input, node1, node2, N)
    print(f"Shortest path for {node1} and {node2}:")
    plot_shortest_path(result)

    #plot
    shortestpath_visualize_result(result)

btn_submit_sp.on_click(shortestpath_return_result_clicked)


# Disconnect two nodes functionality 

# Define buttons to show for the input 
input_N_disc = widgets.IntText(value=1, description='Number of top authors to consider', style={'description_width': 'initial'})
input_author1_d = widgets.IntText(value=1, description='Insert id of one of the two authors', style={'description_width': 'initial'})
input_author2_d= widgets.IntText(value=1, description='Insert id of the other author', style={'description_width': 'initial'})
btn_submit_disc = widgets.Button(description="Submit", button_style='success')

# Show interface of the inputs when the disconnect button is clicked
def disconnect_input(b):
    clear_output(wait=True)
    display(input_N_disc, input_author1_d, input_author2_d, btn_submit_disc)

btn_disconnect.on_click(disconnect_input)

# Plot the results
def disconnect_results(b):
    clear_output(wait = True)
    author1 = input_author1_d.value
    author2 = input_author2_d.value
    n = input_N_disc.value

    disconnect_frontend(n, author1, author2)

btn_submit_disc.on_click(disconnect_results)

# Community detection functionality 

# Define buttons for the input
input_N_com = widgets.IntText(value=1, description='Number of top papers to consider', style={'description_width': 'initial'})
input_paper1 = widgets.IntText(value=1, description='Insert id of one of the two papers', style={'description_width': 'initial'})
input_paper2 = widgets.IntText(value=1, description='Insert id of the other paper', style={'description_width': 'initial'})
btn_submit_com = widgets.Button(description="Submit", button_style='success')

# Input button functionality
def communities_input(b):
    clear_output(wait=True)
    display(input_N_com, input_paper1, input_paper2, btn_submit_com)

btn_communities.on_click(communities_input)

# Show the results
def communities_results(b):
    clear_output(wait = True)

    print('Please wait, this functionality could take a few seconds')

    paper1 = input_paper1.value
    paper2 = input_paper2.value
    n = input_N_com.value

    communities_frontend(n, paper1, paper2)

btn_submit_com.on_click(communities_results)

#show the buttons of the homepage
display_buttons()