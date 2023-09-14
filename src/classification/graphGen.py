import networkx as nx
from getStackTrace import StackDecoder
from pyvis.network import Network


def __str__(addr: tuple[str, str]):
    if addr[0] == addr[1]:
        return addr[0][:9]
    else:
        return addr[1]


tx = "0x9d093325272701d63fdafb0af2d89c7e23eaf18be1a51c580d9bce89987a2dc1"
tx = "0x47ac3527d02e6b9631c77fad1cdee7bfa77a8a7bfd4880dccbda5146ace4088f"
tx = "0x3228cfb5b1b5413181c8b3abb6fd4d241917b537770aa99f5ab6a10b76ad1d27"
tx = "0x3755f81d15d1dfd7257240d1858fd3b6e960ea1d1d68f3ff31d18600f697bb4e"
tx = "0xb540507de5d925bb8cbe60bc6dac03f10af2806b9bad132ea44c17d3afe95713"
stack = StackDecoder().getStack(tx)
dangerNode = __str__(stack[1]._from)
# print(stack[1], dangerNode)
stack = list(filter(lambda x: x._from != tuple(), stack))

G = nx.MultiDiGraph()
colour_map = list()
for i, transaction in enumerate(stack):
    if __str__(transaction._from) == dangerNode:
        G.add_edge(
            __str__(transaction._from),
            __str__(transaction._too),
            order=i,
            function=transaction._func,
            dangerous=True,
        )
    else:
        G.add_edge(
            __str__(transaction._from),
            __str__(transaction._too),
            order=i,
            function=transaction._func,
            dangerous=False,
        )

for node in G:
    # print(n)
    if node == dangerNode:
        colour_map.append("red")
    else:
        colour_map.append("blue")

net = Network()  # notebook=False, cdn_resources="in_line")
net.from_nx(G)
net.show(f"data\\STACKS\\graph {tx}.html", notebook=False)
