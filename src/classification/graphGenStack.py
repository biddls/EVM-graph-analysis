import networkx as nx

# from classification.getStackTrace import StackDecoder
from getStackTrace import StackDecoder
from pyvis.network import Network
from exploits import txs

# from classification.exploits import txs


def __str__(addr: tuple[str, str]):
    return addr[0]
    if addr[0] == addr[1]:
        return addr[0][:9]
    else:
        return addr[1][:9]


class GraphGen:
    G = nx.MultiDiGraph()
    colour_map = list()

    def __init__(self, tx: str, exploitName: str = str()) -> None:
        if tx == str():
            return
        elif exploitName == str():
            raise ValueError("exploitName must be set if tx is set")
        print(f"Generating graph for {exploitName}")
        self.tx = tx
        stack = StackDecoder().getStack(tx)
        self.dangerNode = __str__(stack[1]._from)
        # print(stack[1], dangerNode)
        self.stack = list(filter(lambda x: x._from != tuple(), stack))

        for i, transaction in enumerate(self.stack):
            if __str__(transaction._too) == self.dangerNode:
                self.G.add_node(
                    __str__(transaction._too),
                    color="red",
                    dangerous=True,
                    exploitName=exploitName,
                )
                self.G.add_node(
                    __str__(transaction._from),
                    color="green",
                    dangerous=False,
                    exploitName=exploitName,
                )
            else:
                self.G.add_node(
                    __str__(transaction._too),
                    color="green",
                    dangerous=False,
                    exploitName=exploitName,
                )
            if __str__(transaction._from) == self.dangerNode:
                self.G.add_node(
                    __str__(transaction._from),
                    color="red",
                    dangerous=True,
                    exploitName=exploitName,
                )
                self.G.add_edge(
                    __str__(transaction._from),
                    __str__(transaction._too),
                    order=i,
                    function=transaction._func,
                    exploitName=exploitName,
                )
            else:
                self.G.add_edge(
                    __str__(transaction._from),
                    __str__(transaction._too),
                    order=i,
                    function=transaction._func,
                    exploitName=exploitName,
                )

        for node in self.G:
            # print(n)
            if node == self.dangerNode:
                self.colour_map.append("red")
            else:
                self.colour_map.append("blue")

    def show(self):
        net = Network()
        net.from_nx(self.G)
        net.show(f"data/STACKS/exploits/graph {self.tx}.html", notebook=False)

    def showAll(self, graphs: list[nx.MultiDiGraph]) -> None:
        net = Network("700", "100%")
        G = nx.MultiDiGraph()
        for graph in graphs:
            G = nx.compose(G, graph)
        net.from_nx(G)
        print(f"{len(net.edges)} edges")
        print(f"{len(net.nodes)} nodes")
        net.show(f"data/STACKS/exploits/total graph.html", notebook=False)


if __name__ == "__main__":
    graphs = list()
    for name, tx in txs.items():
        graph = GraphGen(tx, name)
        graphs.append(graph.G)

    GraphGen(str()).showAll(graphs)
