from addrLookup import EthGetCode, ByteCodeIO
import pandas as pd
import logging
from tqdm import tqdm


logging.basicConfig(level=logging.CRITICAL)


if __name__ == "__main__":
    addrs = pd.read_csv(
        "./src/addrs.csv", skiprows=1, usecols=["ContractAddress", "ContractName"]
    )
    with ByteCodeIO() as db:
        to_do = db.inNames(list(addrs["ContractName"].values))
        addrs = addrs[addrs["ContractName"].isin(to_do)]

        for i, (addr, name) in tqdm(
            addrs.iterrows(), total=len(addrs), smoothing=1, mininterval=1
        ):
            i: int = int(i)
            name: str = str(name)
            addr: str = str(addr)

            # if db.inNames(name):
            #     continue

            logging.info(f"{name = }\n{addr = }")

            # if addr in all_conts:
            #     continue

            byteCode = EthGetCode.getCode(addr, int(i))

            db.writeCode(addr, byteCode, Name=name)

"""
Multiple graphs
And compare them across them all
Edges can be of different types for different similarity metrics
Compare to walks of a single type of similarity

JSON Lines
high perf storage python
SQL light

"""
