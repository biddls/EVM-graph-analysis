import networkx as nx
from getStackTrace import StackDecoder
from pyvis.network import Network


def __str__(addr: tuple[str, str]):
    if addr[0] == addr[1]:
        return addr[0][:9]
    else:
        return addr[1][:9]


txs = {
    "Harvest FI": "0x9d093325272701d63fdafb0af2d89c7e23eaf18be1a51c580d9bce89987a2dc1",
    "Euler": "0x47ac3527d02e6b9631c77fad1cdee7bfa77a8a7bfd4880dccbda5146ace4088f",
    "Uniswap Skim": "0x3228cfb5b1b5413181c8b3abb6fd4d241917b537770aa99f5ab6a10b76ad1d27",
    "iearn yUSD": "0x3755f81d15d1dfd7257240d1858fd3b6e960ea1d1d68f3ff31d18600f697bb4e",
    "SushiSwap": "0xea3480f1f1d1f0b32283f8f282ce16403fe22ede35c0b71a732193e56c5c45e8",
    "Euler 2": "0xc310a0affe2169d1f6feec1c63dbc7f7c62a887fa48795d327d4d2da2d6b111d",
    "PolyChain": "0x390def749b71f516d8bf4329a4cb07bb3568a3627c25e607556621182a17f1f9",
}


class GraphGen:
    G = nx.MultiDiGraph()
    colour_map = list()

    def __init__(self, tx: str, exploitName: str = str()) -> None:
        if tx == str():
            return
        elif exploitName == str():
            raise ValueError("exploitName must be set if tx is set")
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


graphs = list()
for name, tx in txs.items():
    graph = GraphGen(tx, name)
    graphs.append(graph.G)

GraphGen(str()).showAll(graphs)
