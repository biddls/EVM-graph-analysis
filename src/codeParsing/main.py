from addrLookup import EthGetCode, ByteCodeIO
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    addrs = pd.read_csv('../addrs.csv', skiprows=1, usecols=['ContractAddress', 'ContractName'])
    # print(addrs)
    # TODO: send off to be parsed
    for i, (addr, name) in addrs.iterrows():
        i: int = int(i)
        name: str = str(name)
        addr: str = str(addr)
        logging.info(f"{name = }\n{addr = }")
        # exit(0)
        # todo check for addr being processed previously
        byteCode = EthGetCode.getCode(addr, int(i))
        ByteCodeIO.writeCode(addr, byteCode, Name=name)

        # todo: log addr as parsed
    # TODO: save parse data
    pass