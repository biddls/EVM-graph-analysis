from mainLoop import WebScraper
from addressScraping.contractObj import Contract
from tqdm import tqdm
from dataOps import ByteCodeIO

# from concurrent.futures import ThreadPoolExecutor
# from concurrent.futures import as_completed

WS = WebScraper()

# path = input("Enter path to txt file: ")
path = "data/honeybadger.uni.lu_datascience_addresses.txt"

print("Reading file")
with open(path, "r") as f:
    addrs = f.readlines()

conts: list[Contract] = list()
for addr in tqdm(addrs, desc="Processing"):
    cont = Contract([], addr.strip(), "noTags")
    conts.append(cont)

if conts == list():
    raise Exception("No addresses found")

print(f"{len(conts)} contracts found")
with ByteCodeIO() as db:
    res = db.getColumn("contracts", "address")
res = set([addr[0] for addr in res])
print(f"{len(res)} contracts in database")
conts = list(filter(lambda x: x.address not in res, conts))
print(f"{len(conts)} contracts left")

for cont in tqdm(conts, desc="Writing"):
    WS.singleAddr(cont)
