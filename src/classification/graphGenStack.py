import networkx as nx

from classification.getStackTrace import StackDecoder
from collections import Counter
import pickle

# from getStackTrace import StackDecoder
from pyvis.network import Network
from addressScraping.contractObj import Contract
from tqdm import tqdm
import numpy as np
import os

# from exploits import txs
from mainLoop import WebScraper

from classification.exploits import txs


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
        self.dangerNode = __str__(stack[1]._too)
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

    def showAll(self, graphs: list[nx.MultiDiGraph], show=False) -> nx.MultiDiGraph:
        net = Network("700", "100%")
        G = nx.MultiDiGraph()
        for graph in graphs:
            G = nx.compose(G, graph)
        net.from_nx(G)
        print(f"{len(net.edges)} edges")
        print(f"{len(net.nodes)} nodes")
        with open("data/STACKS/addrs.txt", "w") as f:
            for node in net.nodes:
                f.write(f"{node['id']}\n")

        if show:
            net.show(f"data/STACKS/exploits/total graph.html", notebook=False)

        vectors = self.vectoriseConts(list(G.nodes))
        keep = vectors.keys()
        G = G.subgraph(keep)
        G = nx.MultiDiGraph(G)
        # print(G.nodes)
        for node in tqdm(G.nodes):
            vector = np.array(vectors[node])
            G.nodes[node]["vector"] = vector / np.sum(vector)

        return G

    def vectoriseConts(self, conts: list[str]) -> dict[str, list[int]]:
        with open("data/opCodes.txt", "r") as f:
            opCodes = list(map(eval, tqdm(f.readlines(), desc="Reading opCodes")))
            opCodes = list(filter(lambda x: x[0] in conts, opCodes))

        vectors: dict[str, list[int]] = dict()
        print(len(conts), len(opCodes))
        for cont in tqdm(opCodes, desc="Vectorising contracts"):
            addr: str = cont[0]
            cont = cont[1:][0]
            # print(len(cont))
            freq = dict(Counter(cont[1:]))
            vector: list[int] = [
                freq[i] if i in freq.keys() else 0 for i in range(0, 256)
            ]
            vectors[addr] = vector

        with open("data/vectorsForOneClass.txt", "w") as f:
            for addr, vector in vectors.items():
                cont = [addr, vector]
                f.write(f"{str(cont)}\n")

        return vectors


if False:  # os.path.exists("data/graphs.pickle"):
    with open("data/graphs.pickle", "rb") as f:
        G: nx.MultiDiGraph = pickle.load(f)
    print("First nodes data:")
    for node in G.nodes.data():
        input(node)

else:
    graphs = list()
    for name, tx in txs.items():
        graph = GraphGen(tx, name)
        graphs.append(graph.G)
    G = GraphGen(str()).showAll(graphs, show=True)
    empty = list(filter(lambda x: np.sum(x[1]["vector"]) == 0, G.nodes.data()))
    print(empty)
    with open("data/graphs.pickle", "wb") as f:
        pickle.dump(G, f)
    addrs = G.nodes
    WS = WebScraper()

    # dangerous = addrs.data()
    # dangerous = list(filter(lambda x: x[1]["dangerous"], dangerous))
    # print(dangerous)
    for node in addrs.data():
        if np.sum(node[1]["vector"]) == 0:
            print(node)
            raise ValueError("Empty vector")
    # for addr in dangerous[::-1]:
    #     addr = Contract([], addr[0], "noTags")
    #     print(addr)
    #     byteCode = WS.getByteCode([addr])
    #     print(byteCode)
    #     WS.addContractsToDB(byteCode, writeCode=True, noForce=False)
    #     out = WS.singleAddr(addr, progBar=True)
    #     print(out)

    # for addr in addrs:
    #     addr = Contract([], addr, "noTags")
    #     WS.singleAddr(addr)
