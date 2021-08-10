


def get_graph_img(n, e, edges):
#    print(f"n={n} e={e}")
    import networkx as nx
    import matplotlib.pyplot as plt
    from datetime import datetime
    G = nx.DiGraph()
    positions = [ [5, 7], [5, 6], [4, 5], [6, 5], [3, 4], [4, 4], [6, 4], [7, 4], [4, 3], [6, 3], [5, 2], [5, 1] ]
    for node in range(n):
        G.add_node(node, pos = positions[node])
    for e in edges:
        G.add_edge(e[0], e[1], weight = e[2])

    values = ['lightgrey' for node in G.nodes()]
    values[0] = values[-1] = 'lightblue'
    pos=nx.get_node_attributes(G,'pos')
    nx.draw_networkx_nodes(G, pos, node_color = values, node_size = 300)
    edge_labels = dict([((u,v,),d['weight']) for u,v,d in G.edges(data=True)])
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edge_labels(G, pos, edge_labels = edge_labels)
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color='r', arrows=True)
    dt = str(datetime.now())
    name = f"static/mg-{dt}.png"
    plt.savefig(name)
    return name
