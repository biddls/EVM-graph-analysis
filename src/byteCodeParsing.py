from typing import Any
from dataOps import ByteCodeIO
from addressScraping.contractObj import Contract
from tqdm import tqdm
import logging
from classification import graphGenStack
import networkx as nx
from mainLoop import WebScraper

# to shutup the logger
logging.basicConfig(level=logging.CRITICAL)


class GraphGen:
    db: ByteCodeIO

    def __init__(self) -> None:
        self.db = ByteCodeIO()

    def findLinks(self, cont: Contract) -> Contract:
        """finds addresses in the bytecode and writes them to the contract

        Args:
            cont (Contract): contract object to be checked

        Returns:
            Contract: contract object with links added
        """
        byteCode = cont.dissassemble()
        # print(byteCode is None)
        links: set[str] = set()
        for op in byteCode:
            if len(op.operand) != 40:
                pass
            elif len(set(op.operand)) == 1:
                pass
            elif self.checkAddrForValidity(op.operand):
                links.add(op.operand)
        if links:
            cont.addLinks(links)
        return cont

    def checkAddrForValidity(self, addr: str) -> bool:
        """checks if the address is valid
        Does this address have any bytecode?
        Does this address  have any transactions/ether?

        Args:
            addr (str): address to be checked

        Returns:
            bool: True if valid, False otherwise
        """
        # checks if address has any bytecode
        if self.db.inColumn("contracts", "address", addr):
            # add recursion here
            # self.db.getElem(

            # )

            # TODO: get bytecode and process it
            return True
        # TODO: check if address has any transactions
        # TODO: check if address has any ether
        # TODO: check if address has already been checked
        return True


if __name__ == "__main__":
    with ByteCodeIO() as db:
        contracts = db.getColumn("contracts", "address, byteCode")

    linksFound: int = 0
    # contracts = contracts[:500]
    loop: tqdm = tqdm(
        enumerate(contracts),
        desc=f"Links found: {linksFound}",
        total=len(contracts),
    )
    graphGen = GraphGen()
    G = nx.MultiDiGraph()
    conts: list[Contract] = list()
    for i, (addr, byteCode) in loop:
        if byteCode == "None":
            continue
        cont = Contract([], addr, "noTags", byteCode=byteCode)
        cont = graphGen.findLinks(cont)
        linksFound += len(cont.links)

        loop.set_description(
            f"Links: {linksFound}, Interconectivity: {linksFound/(i+1):.2f}"
        )
        for edge in cont.links:
            G.add_edge(addr, edge)
        conts.append(cont)

    # takes the found links and gets the bytecode for them
    WS = WebScraper()
    newconts = list()

    for cont in conts:
        if cont.links != set():
            cont = Contract([], cont.address, "noTags")
            newconts.append(cont)
    print(f"Found {len(newconts)} new contracts")
    newconts = WS.batch(newconts, getTags=False)
    if newconts is not None:
        print(f"Written {len(newconts)} new contracts")
    # exit()
    graphs = list()
    for name, tx in graphGenStack.txs.items():
        graph = graphGenStack.GraphGen(tx, name)
        graphs.append(graph.G)

    graphs.append(G)
    for graph in graphs:
        G = nx.compose(G, graph)

    exit(0)
    graphGenStack.GraphGen(str()).showAll(graphs)
