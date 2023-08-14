from itertools import chain


records = [("Unibot: Router",), ("Unibot",)]
records = set(chain.from_iterable(records))
tags = {"Unibot", "DEX 2", "Tokenlon", "DEX", "DeFi", "Tokenlon: DEX 2", "Source Code"}
print(records)
print(tags)

# remove all the elemets in records from tags
tags = tags - records
print(tags)
