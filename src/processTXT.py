from mainLoop import WebScraper
from addressScraping.contractObj import Contract
from tqdm import tqdm

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

for cont in tqdm(conts, desc="Writing"):
    WS.singleAddr(cont)

# with ThreadPoolExecutor() as executor:
#     pool = executor.map(WS.singleAddr, tqdm(conts, desc="Starting"))
#     # pool = executor.map(len, tqdm(conts, desc="Starting"))

#     results = list(tqdm(pool, total=len(conts)))
