#Get the largest connected subgraph
python -c "import networkx as nx; G = nx.read_edgelist('grapho.txt'); connected_components = list(nx.connected_components(G)); largest_component = max(connected_components, key=len); G_largest = G.subgraph(largest_component); nx.write_edgelist(G_largest, 'largest_component.edgelist')"


#4.1
#Get the betweenness centrality score for every node
python -c "import networkx as nx; G_largest = nx.read_edgelist('largest_component.edgelist'); centrality = nx.betweenness_centrality(G_largest); print('\n'.join([f'{node}:{centralityscore}' for node, centralityscore in centrality.items()]))" > centrality.txt

#Sort the centrality scores  in descending order
sort -t: -k2 -rn centrality.txt > sorted_centrality.txt

#Get the node with the highest betweenness centrality
most_con_node=$(head -n 1 sorted_centrality.txt | awk -F':' '{print $1}')
highest_score=$(head -n 1 sorted_centrality.txt | awk -F':' '{print $2}')

#Print the result
printf "The node with the highest betweenness centrality score is: '%s'\n" "$most_con_node"
printf "It has a betweenness centrality score of: '%s'\n" "$highest_score"


#4.2 
# Create a file with the count of incoming edges
#The new file incoming_edges.txt that is created has two "columns" the first one is the node id the second one the count of incoming edges to that node
awk '{count[$2]++} END {for (node in count) print node, count[node]}' grapho.txt > incoming_edges.txt

# Sort the list by the count and store it in a new file
sort -rn -k2 incoming_edges.txt > sorted_node_count.txt

# Get the difference of how it varies
highest_count=$(head -n 1 sorted_node_count.txt | awk '{print $2}')
lowest_count=$(tail -n 1 sorted_node_count.txt | awk '{print $2}')
diff=$((highest_count - lowest_count))

# Get the average
average=$(awk '{total += $2; count++} END {if (count > 0) print total/count}' incoming_edges.txt)

# Get the standard deviation
std_dev=$(awk '{total += $2; total_squares += ($2)^2; count++} END {if (count > 0) print sqrt(total_squares/count - (total/count)^2)}' incoming_edges.txt)

# Print the results
printf "Difference of most and least cited paper is: '%s'\n" "$diff"
printf "The average of incoming nodes is: '%s'\n" "$average"
printf "The standard deviation is: '%s'\n" "$std_dev"


#4.3
#
python -c "import networkx as nx; G_largest = nx.read_edgelist('largest_component.edgelist');  avg_shortest_path_length = nx.average_shortest_path_length(G_largest); print(f\"The average shortest path length of the largest connected subgraph is: {avg_shortest_path_length}\")"