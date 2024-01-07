class graph:
    def __init__(self, V: list, E: list, attributes: dict, directed: bool):
        self.nodes = V
        self.edges = E
        self.edges_attributes = attributes
        
        # Flag to indicate if the graph is directed
        self.isdirected = directed
    
    def set_edges_attribute(self, edges, values, name=None):
        # Add an attribute (as dictionary) to the graph
        attribute_dict = dict.fromkeys(self.edges, None)
        for (edge, value) in zip(edges, values):
            attribute_dict[edge] = value
            self.edges_attributes.update({name : attribute_dict})
    
    def extract_subgraph(self, subgraph_nodes):
        # The subgraph will be directed iff the original graph is directed
    
        # retrieve edges with both end in the list of nodes of the subgraph
        subgraph_edges = [edge for edge in self.edges if (edge[0] in subgraph_nodes and edge[1] in subgraph_nodes) ]

        # Update attributes for the subraph
        subgraph_attributes = dict()
        for attribute in self.edges_attributes: 
            original_attribute = self.edges_attributes[attribute]
            subgraph_attributes[attribute] = {edge: original_attribute[edge] for edge in subgraph_edges}

        subgraph = graph(subgraph_nodes, subgraph_edges, subgraph_attributes, self.isdirected)
        return subgraph

    def remove_edges(self, edges_todel_list):
        # old edges
        edges = self.edges

        # list containing the old edges without the ones to delete
        new_edges = [edge for edge in edges if edge not in edges_todel_list]
        
        # set new edges as 'edges' attribute of the graph
        self.edges = new_edges

    def get_neighborhood(self, vertex): # Different cases if the graph is directed or not
        if self.isdirected:
            neigborhood = [edge[1] for edge in self.edges if edge[0] == vertex]
            return neigborhood
        
        # not directed case
        neigborhood = [edge[1] for edge in self.edges if edge[0] == vertex] + [edge[0] for edge in self.edges if edge[1] == vertex]
        neigborhood = list(set(neigborhood))

        return neigborhood
    
    def neighborhood_withedges_onlyundirected(self, vertex):
        # Rettuns a {neighrbor : edge between vertex and neighbor } dictionary
        if not self.isdirected:
            neigborhood_withedges = {edge[1]: edge for edge in self.edges if edge[0] == vertex}
            neigborhood_withedges.update({edge[0]: edge for edge in self.edges if edge[1] == vertex})

            return neigborhood_withedges

    def indegree(self, node):
        if self.isdirected:
            indegree = len([edge for edge in self.edges if edge[1] == node])
            return indegree
        
        
    def to_directed(self):
        if self.isdirected:
            return self
        
        # Define "backwards" edges of the graph and add them to the original ones
        new_edges = set(edge[::-1] for edge in self.edges)
        total_edges = list(set(self.edges).union(new_edges))
        # set edges attribute 
        self.edges = total_edges

        # Update new edges' attributes by adding the "backwards" edges to the attributes and setting their weight as the same of their corresponding original edge
        new_edges = list(new_edges)
        updated_attributes = dict()
        for attribute in self.edges_attributes:
            attr_dict = self.edges_attributes[attribute]
            new_edges_attr = dict({new_edge: attr_dict[new_edge[::-1]] for new_edge in new_edges})
            new_edges_attr.update(attr_dict)
            updated_attributes.update( { attribute: new_edges_attr } )

        self.edges_attributes = updated_attributes
        # set 
        self.isdirected = True
        return self
    
    def copy(self):
        return graph(self.nodes, self.edges, self.edges_attributes, self.isdirected)
    