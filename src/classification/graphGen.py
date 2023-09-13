import networkx as nx
from getStackTrace import StackDecoder

tx = "0x9d093325272701d63fdafb0af2d89c7e23eaf18be1a51c580d9bce89987a2dc1"
stack = StackDecoder().getStack(tx)
print(len(stack))
stack = set(filter(lambda x: x._from != tuple(), stack))
print(len(stack))
G = nx.Graph()
for i, transaction in enumerate(stack):
    ...
