"""
This checks N sources for address and or tags and stored
the data in an SQL database
"""

from time import sleep, time
from typing import Any
from addressScraping.contractObj import Contract
from addressScraping.usMoney import usMoneyScraper
from addressScraping.contTagScraping import TagGetter
from dataOps import EthGetCode, ByteCodeIO
from tqdm import tqdm
from itertools import chain
from addressScraping.readFromCSV import Reader


class WebScraper:
    def __init__(self) -> None:
        self.tagGetter = TagGetter()
        # init DB object
        self.db = ByteCodeIO

    @staticmethod
    def getAddrsFromUltrasound() -> list[Contract]:
        """
        This function gets the addresses from ultrasound.money

        Returns:
            list[Contract]: List of contract objects
        """
        contracts = usMoneyScraper.getAddresses()
        # print(f"{len(contracts)} contracts found from ultrasound.money")
        return contracts

    def getByteCode(self, contracts: list[Contract], progBar=True) -> list[Contract]:
        """
        This function finds and attaches the bytecode to the contracts

        Args:
            list[Contract]: List of contract objects

        Returns:
            list[Contract]: List of contract objects
        """
        with self.db() as db:
            contracts = list(
                filter(
                    lambda x: not db.inColumn("contracts", "address", x.address),
                    contracts,
                )
            )
        if progBar:
            itter = tqdm(
                enumerate(contracts),
                desc="Getting ByteCode",
                total=len(contracts),
                leave=False,
            )
        else:
            itter = enumerate(contracts)
        for i, cont in itter:
            code = EthGetCode.callEvmApi(cont.address, "eth_getCode")
            if code is None:
                continue
            contracts[i].addByteCode(code)

        contracts = list(filter(lambda x: x.byteCode != "", contracts))

        return contracts

    def tagsFromEtherscan(
        self,
        contracts: list[Contract],
        site: str = "Etherscan",
        maxDuration: float = 5,
        progBar=True,
    ) -> list[Contract]:
        """
        This function gets the tags from etherscan.io

        Args:
            list[Contract]: List of contract objects

        Returns:
            list[Contract]: List of contract objects
        """
        with self.db() as db:
            addrsAndTags = db.getColumn("addressTags", "address, source")
        addrsAndTags = {k: v for k, v in addrsAndTags if v is not site}
        addrsAndTags = set(addrsAndTags.keys())
        # print(addrsAndTags)
        # print(f"{len(contracts)} contracts before filtering")
        contracts = list(filter(lambda x: x.address not in addrsAndTags, contracts))
        # print(f"{len(contracts)} contracts after filtering")
        if progBar:
            itter = tqdm(contracts, desc="Getting Tags", leave=False)
        else:
            itter = contracts
        contracts = list(
            map(
                lambda x: x + self.tagGetter.getTags(x.address, site, maxDuration),
                itter,
            )
        )
        return contracts

    def addContractsToDB(
        self,
        contracts: list[Contract],
        writeTags: bool = False,
        writeCode: bool = False,
        noForce: bool = True,
        progBar=True,
    ) -> None:
        """
        This function adds the contracts to the database

        Args:
            list[Contract]: List of contract objects
        """
        if not (writeTags or writeCode):
            raise Exception(
                f"Must write tags or code or both\n{writeTags = }\n{writeCode = }"
            )

        if writeCode:
            if progBar:
                itter = tqdm(contracts, desc="Writing Contracts", leave=False)
            else:
                itter = contracts
            contsAdded = 0
            with self.db() as db:
                # writes to "contracts" sheet
                for cont in itter:
                    contsAdded += db.writeContract(cont, noForce=noForce)
            if progBar:
                print(f"\t{contsAdded} contracts added to database")

        if writeTags:
            if progBar:
                itter = tqdm(contracts, desc="Writing Tags", leave=False)
            else:
                itter = contracts
            tagsAdded = 0
            with self.db() as db:
                # wrties tags to "addressTags" sheet
                for cont in itter:
                    tagsAdded += db.writeTags(cont.address, cont.tags)
            if progBar:
                print(f"\t{tagsAdded} tags added to database")

    def __call__(self, *args: Any, **kwds: Any):
        start = time()
        counter = 0
        while True:
            print(f"Starting run: {counter}")
            self.main()
            counter += 1
            continue

            start += 60 * 5  # 5 mins
            if time() > start:
                start = time()
            else:
                dur = start - time()
                print(f"Sleeping for {dur:.0f} seconds")
                sleep(dur)

    def main(self):
        print("\tgetAddrsFromUltrasound")
        contracts = self.getAddrsFromUltrasound()
        print("\tgetByteCode")
        contracts = self.getByteCode(contracts)

        print("\ttagsFromEtherscan")
        contracts = self.tagsFromEtherscan(contracts, maxDuration=3)
        print("\taddContractsToDB")
        self.addContractsToDB(contracts, writeTags=True, writeCode=True)

    def fullTagUpdate(self):
        with self.db() as db:
            addrs = db.getColumn("contracts", "address")

        addrs: list[str] = list(chain.from_iterable(addrs))

        contracts: list[Contract] = []

        for addr in tqdm(addrs, desc="Creating Contract Objects", leave=False):
            cont = Contract([], addr, "noTags")
            contracts.append(cont)

        contracts = self.tagsFromEtherscan(contracts, maxDuration=3)
        self.addContractsToDB(contracts, writeTags=True)
        print(f"{len(contracts)} contracts tags added to database")

    def reaplceByteCodeWithRaw(self):
        raise Exception("This code is only meant to be run once")
        with self.db() as db:
            result = db.getColumn("contracts", "address")

        conts: list[Contract] = [Contract([name], addr, "forceSet") for addr in result]

        print(f"{len(conts)} contracts found")
        conts = self.getByteCode(conts)
        self.addContractsToDB(conts, writeCode=True, noForce=False)

    def runCSV_scipt(self):
        # raise Exception ("Incomplete function")
        contracts: list[Contract] = list(Reader.main())
        for cont in tqdm(contracts):
            self.singleAddr(cont, getTags=False)

    def singleAddr(self, cont: Contract, getTags=True, progBar=False):
        contract = list([cont])
        # print('\tgetByteCode')
        contract = self.getByteCode(contract, progBar=progBar)
        if len(contract) == 0:
            return
        # print('\ttagsFromEtherscan')
        if getTags:
            contract = self.tagsFromEtherscan(contract, maxDuration=3, progBar=progBar)
            # print('\taddContractsToDB')
            if len(contract) == 0:
                return
            self.addContractsToDB(
                contract, writeTags=True, writeCode=True, progBar=progBar
            )
        else:
            if len(contract) == 0:
                return
            self.addContractsToDB(
                contract, writeTags=False, writeCode=True, progBar=progBar
            )
        return Contract

    def batch(self, conts: list[Contract], getTags=True):
        conts = self.getByteCode(conts, progBar=True)
        if len(conts) == 0:
            return
        # print('\ttagsFromEtherscan')
        if getTags:
            conts = self.tagsFromEtherscan(conts, maxDuration=3, progBar=True)
            # print('\taddContractsToDB')
        if len(conts) == 0:
            return
        self.addContractsToDB(conts, writeTags=getTags, writeCode=True, progBar=True)

        return conts


if __name__ == "__main__":
    scraper = WebScraper()
    # scraper.reaplceByteCodeWithRaw()
    scraper.runCSV_scipt()
    scraper.fullTagUpdate()
    scraper()
