import snap

class graph_helper():
    def __init__(self, Graph):
        self.Graph = Graph
        self.two_hop_nodes = None

    # get neighbors of a certain node with node id
    # un-directional
    def get_neighbors(self, id):
        node = self.Graph.GetNI(id)
        return [node.GetNbrNId(x) for x in range(node.GetDeg())] 
    
    # helper function for bfs search
    def bfs_nodes_helper(self, queue, visited):
        visited.update(queue)
        new_queue = set([n for o in queue for n in self.get_neighbors(o) if n not in visited])
        
        if len(new_queue):
            yield new_queue
            for b in self.bfs_nodes_helper(new_queue, visited):
                yield b
        del new_queue
    
    # bfs search from a certain seedId with depth
    def bfs_nodes(self, seedId, depth = None): # A is a Node
        visited = set([seedId])
        queue = set(self.get_neighbors(seedId))
    
        yield(queue)
        for i, b in enumerate(self.bfs_nodes_helper(queue, visited)):
            if depth == None or i+1 < depth:
                yield b

    # a temporary function for calculating influence
    def influence_helper(self, node):
        node_degree = 1. * sum(w
                               for (n1, n2, e, w) in self.get_edges(node)
                               if (n1 not in self.two_hop_nodes) or (n2 not in self.two_hop_nodes))

        sum_weights = 1. * sum(self.get_edge_attr(e, 'Weight')
                               for (n1, n2, e, w) in self.get_edges(node)
                               if (n1 not in self.two_hop_nodes) or (n2 not in self.two_hop_nodes))
        if sum_weights == 0:
            sum_weights = 1.

        return node_degree, sum_weights

    # helper recursive function for set_influence
    def dfs_influence(self, node, weight, decay_function, degree_function, visited, label, max_depth):
        node_value = self.get_node_attr(node, label) + weight
        self.set_node_attr(node, node_value, label)
    
        if len(visited) >= max_depth:
            return

        node_degree, sum_weights = self.influence_helper(node)
        
        for n1, n2, e, w in self.get_edges(node):
            # exclude 2hop-2hop edges
            if (n1 in self.two_hop_nodes) and (n2 in self.two_hop_nodes): continue
            
            # if incoming edges, switch direction
            if n2 == node:
                n1, n2 = n2, n1
                
            if n2 in visited: continue

            visited.add(n2)
            self.dfs_influence(n2, degree_function(node_degree) 
                               * decay_function(weight) * 
                               (self.get_edge_attr(e, 'Weight') / sum_weights), 
                               decay_function, degree_function, visited, label, max_depth)
            visited.remove(n2)

    # set influence for each node
    def set_influence(self, seed, decay_function, degree_function, label='Influ', max_depth=5):
        for NodeId in self.get_nodes():
            self.set_node_attr(NodeId, 0.0, label)
    
        visited = set([seed])

        node_degree, sum_weights = self.influence_helper(seed)

        for n1, n2, e, w in self.get_edges(seed):
            # exclude 2hop-2hop edges
            if (n1 in self.two_hop_nodes) and (n2 in self.two_hop_nodes): continue

            if seed == n2:
                n1, n2 = n2, n1
                
            visited.add(n2)
            self.dfs_influence(n2, degree_function(node_degree) * 
                                   self.get_edge_attr(e, 'Weight') / sum_weights, 
                                   decay_function, degree_function, visited, label, max_depth)
            visited.remove(n2)


    
    # get all edges for a certain nodeId or all node ids
    # return (from_nodeid, to_nodeid, edge)
    def get_edges(self, NodeId = None):
        if NodeId is None:
            for NI in self.Graph.Nodes():
                NodeId = NI.GetId()
                for i, NJ in enumerate(NI.GetOutEdges()):
                    n2 = NI.GetOutNId(i)
                    if self.Graph.IsEdge(n2, NodeId):
                        w = 0.5
                    else:
                        w = 1.0
                    yield (NodeId, n2, self.Graph.GetEId(NodeId, NJ), w)

                for i, NJ in enumerate(NI.GetInEdges()):
                    n2 = NI.GetInNId(i)
                    if self.Graph.IsEdge(NodeId, n2):
                        w = 0.5
                    else:
                        w = 1.0
                    yield (n2, NodeId, self.Graph.GetEId(NJ, NodeId), w)
        else:
            NI = self.Graph.GetNI(NodeId)
            for i, NJ in enumerate(NI.GetOutEdges()): 
                n2 = NI.GetOutNId(i)
                if self.Graph.IsEdge(n2, NodeId):
                    w = 0.5
                else:
                    w = 1.0
                yield (NodeId, NI.GetOutNId(i), self.Graph.GetEId(NodeId, NJ), w)
            for i, NJ in enumerate(NI.GetInEdges()): 
                n2 = NI.GetInNId(i)
                if self.Graph.IsEdge(NodeId, n2):
                    w = 0.5
                else:
                    w = 1.0
                yield (NI.GetInNId(i), NodeId, self.Graph.GetEId(NJ, NodeId), w)

    def get_nodes(self, NodeId = None):
        if NodeId is None:
            for NI in self.Graph.Nodes():
                yield NI.GetId()
        else:
            print "Not Implemented"
            XX

    def get_node_attr(self, NodeId, field):
        if field in Int_attributes:
            return self.Graph.GetIntAttrDatN(NodeId, field)
        if field in Flt_attributes:
            return self.Graph.GetFltAttrDatN(NodeId, field)

    def get_edge_attr(self, e, field):
        if field in Int_attributes:
            return self.Graph.GetIntAttrDatE(e, field)
        if field in Flt_attributes:
            return self.Graph.GetFltAttrDatE(e, field)

    def set_node_attr(self, NodeId, value, field):
        if field in Int_attributes:
            self.Graph.AddIntAttrDatN(NodeId, value, field)
        if field in Flt_attributes:
            self.Graph.AddFltAttrDatN(NodeId, value, field)

    def set_edge_attr(self, e, value, field):
        if field in Int_attributes:
            self.Graph.AddIntAttrDatE(e, value, field)
        if field in Flt_attributes:
            self.Graph.AddFltAttrDatE(e, value, field)

    def get_2hop_to_2hop_edges(self, two_hop_nodes):
        for NJ in self.Graph.Edges():
            n1 = NJ.GetSrcNId()
            n2 = NJ.GetDstNId()
            if (n1 in two_hop_nodes) and (n2 in two_hop_nodes):
                yield 1

    def get_double_direction_edges(self, two_hop_nodes):
        for NJ in self.Graph.Edges():
            n1 = NJ.GetSrcNId()
            n2 = NJ.GetDstNId()
            e = NJ.GetId()
            if (n1 not in two_hop_nodes) or (n2 not in two_hop_nodes):
                if self.Graph.IsEdge(n2, n1):
                    yield (n1, n2, e)

    # get node degree distribution for the entire graph
    def get_node_degree_distribution(self, direction='all'):
        DegToCntV = snap.TIntPrV()
        if direction == 'all':
            snap.GetDegCnt(self.Graph, DegToCntV)
        elif direction == 'in':
            snap.GetInDegCnt(self.Graph, DegToCntV)
        elif direction == 'out':
            snap.GetOutDegCnt(self.Graph, DegToCntV)
        else:
            return None
        return DegToCntV
    
    # get diameter of the graph using different number of test nodes
    def get_diameter(self, ntestnodes = [10,]):
        # diameter is calculated by samping a few test nodes
        # here we output list of diameters for all number of testnodes
        diam = [0,] * len(ntestnodes)
        for i, ntestnode in enumerate(ntestnodes):
            diam[i] = snap.GetBfsFullDiam(self.Graph, ntestnode)
        return diam
    
    # get triads for each node or for the entire graph
    def get_triads(self, all=False):
        if all:
            # get total number of triads
            return snap.GetTriads(self.Graph)
    
        # get triads for each node
        triads = []
        for NI in self.Graph.Nodes():
            triads.append([NI.GetId(), snap.GetNodeTriads(self.Graph, NI.GetId())])
        return triads
    
    # get clustering coefficients for each node or for the entire graph
    def get_clustering_coeffs(self, all=False):
        if all:
            # get average clustering coefficients for the entire graph
            return snap.GetClustCf(self.Graph)
    
        NIdCCfH = snap.TIntFltH()
        snap.GetNodeClustCf(self.Graph, NIdCCfH)
        return NIdCCfH
