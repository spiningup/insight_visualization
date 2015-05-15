import snap
import commands
import numpy as np
from graph_helper import graph_helper
import random
random.seed(0)

def build_graph(edge_file='edges_4hop', weighted=False):

    d = np.loadtxt(edge_file)
    # get the number of nodes and edges
    NNodes = int(max(max(d[:,0]), max(d[:,1]))) + 1
    NEdges = len(d)
    print 'number of nodes and edges :', NNodes, NEdges
    
    # construct graph
    Graph = snap.TNEANet.New(NNodes, NEdges)
    
    # add nodes
    for i in xrange(NNodes):
        Graph.AddNode(i)

    print 'finishes adding nodes'
    # add edges
    for i in xrange(NEdges):
        n1, n2 = d[i,0], d[i,1]
        if n1 > n2:
            n1, n2 = n2, n1
        if not Graph.IsEdge(int(n1), int(n2)):
            EdgeId = Graph.AddEdge(int(n1), int(n2))
    print 'number of edges', Graph.GetEdges()
    
    return Graph


def get_subgraph(Graph, SeedNodeId, depth=2):

    g = graph_helper(Graph)

    bfs_nodes = set([SeedNodeId])
    for ns in g.bfs_nodes(SeedNodeId, depth=depth):
        bfs_nodes = bfs_nodes.union(ns)

    NIdV = snap.TIntV()
    for i in bfs_nodes:
        NIdV.Add(i)

    SubGraph = snap.GetSubGraph(Graph, NIdV)
    gsub = graph_helper(SubGraph)

    return SubGraph

def make_json(g, SeedNodeId, filename='graph.json'):
    Graph = g.Graph

    NNodes = Graph.GetNodes()
    NEdges = Graph.GetEdges()
    print 'number of subgraph nodes and edges', NNodes, NEdges
    f2 = open(filename,'w')

    one_hop = g.get_neighbors(SeedNodeId)

    nodes = []
    for NI in Graph.Nodes():
        i = NI.GetId()
        nodes.append(i)

    edges = []
    for NJ in Graph.Edges():
        EdgeId = NJ.GetId()
        i = NJ.GetSrcNId()
        j = NJ.GetDstNId()
        edges.append([i,j])

    x = np.argsort(nodes)
    idx = {}
    for id in x:
        idx[nodes[x[id]]] = id


    seednode_sorted = idx[SeedNodeId]
    one_hop_sorted = [idx[i] for i in one_hop]

    clustering_coef = []
    NIdCCfH = g.get_clustering_coeffs()
    for item in NIdCCfH:
        clustering_coef.append(NIdCCfH[item])

    triads = [i[1] for i in g.get_triads()]

    print >> f2, '{'
    print >> f2, '  "text": ['
    print >> f2, '    {"x":20, "y":30, "textvalue": "Number of Nodes : %d"},'%(NNodes) 
    print >> f2, '    {"x":20, "y":50, "textvalue": "Number of Edges : %d"},'%(NEdges)
    print >> f2, '    {"x":20, "y":70, "textvalue": "Number of One-hop Nodes : %d"},'%(len(one_hop)) 
    print >> f2, '    {"x":20, "y":90, "textvalue": "Min Clustering Coef : %5.2f"},'%(min(clustering_coef))
    print >> f2, '    {"x":20, "y":110, "textvalue": "Max Clustering Coef : %5.2f"},'%(max(clustering_coef))
    print >> f2, '    {"x":20, "y":130, "textvalue": "Avg Clustering Coef : %5.2f"},'%(np.mean(clustering_coef))
    print >> f2, '    {"x":20, "y":150, "textvalue": "Std Clustering Coef : %5.2f"},'%(np.std(clustering_coef))
    print >> f2, '    {"x":20, "y":170, "textvalue": "Min Triads : %d"},'%(min(triads))
    print >> f2, '    {"x":20, "y":190, "textvalue": "Max Triads : %d"},'%(max(triads))
    print >> f2, '    {"x":20, "y":210, "textvalue": "Avg Triads : %5.2f"},'%(np.mean(triads))
    print >> f2, '    {"x":20, "y":230, "textvalue": "Std Triads : %5.2f"},'%(np.std(triads))
    print >> f2, '    {"x":20, "y":250, "textvalue": "Sum Triads : %d"}'%(np.sum(triads))
    print >> f2, '  ],'
    print >> f2, '  "nodes":['
    id = 0
    for i in range(NNodes):
        if i == seednode_sorted:
            group = 1
        elif i in one_hop_sorted:
            group = 2
        else:
            group = 3
        if id == NNodes -1: 
            print >> f2, '    {"name":"%s","group":%s}'%(i, group)
        else:
            print >> f2, '    {"name":"%s","group":%s},'%(i, group)
        id += 1
    print >> f2, '  ],'

    print >> f2, '  "links":['
    id = 0
    for NJ in Graph.Edges():
        EdgeId = NJ.GetId()
        i = NJ.GetSrcNId()
        j = NJ.GetDstNId()

        if id == NEdges - 1:
            print >> f2, '    {"source":%d,"target":%d,"value":1}'%(idx[i],idx[j])
        else:
            print >> f2, '    {"source":%d,"target":%d,"value":1},'%(idx[i],idx[j])
        id += 1
    print >> f2, '  ]'
    print >> f2, '}'


if __name__ == '__main__':

    Graph = build_graph()

    # true seednode id
    SeedNodeId = 302
    TwohopGraph = get_subgraph(Graph, SeedNodeId, depth=2)
    
    i_graph = 0
    for NI in TwohopGraph.Nodes():
        SeedNodeId = NI.GetId()
        SubGraph = get_subgraph(Graph, SeedNodeId, depth=2)
        g = graph_helper(SubGraph)
        one_hop = g.get_neighbors(SeedNodeId)
        if SubGraph.GetNodes() > 100 and len(one_hop) > 10:
            make_json(g, SeedNodeId, filename='graph_%s.json'%(i_graph))    
            print 'seed node Id', SeedNodeId
            print 'number of one, two hop nodes', len(one_hop), SubGraph.GetNodes()
            i_graph += 1
        else:
            print SeedNodeId, SubGraph.GetNodes()
