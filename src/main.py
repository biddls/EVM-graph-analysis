"""
This checks N sources for address and or tags and staored
the data in an SQL database
"""

from time import sleep, time
from typing import Any
from addressScraping.contractObj import Contract
from addressScraping import usMoney
from addressScraping.contTagScraping import TagGetter
from codeParsing.dataOps import EthGetCode, ByteCodeIO
from tqdm import tqdm
from itertools import chain


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
        contracts = usMoney.getAddresses()
        # print(f"{len(contracts)} contracts found from ultrasound.money")
        return contracts

    def getByteCode(self, contracts: list[Contract]) -> list[Contract]:
        """
        This function finds and attaches the bytecode to the contracts

        Args:
            list[Contract]: List of contract objects

        Returns:
            list[Contract]: List of contract objects
        """
        with self.db() as db:
            for i, cont in tqdm(
                enumerate(contracts),
                desc="Getting ByteCode",
                total=len(contracts),
                leave=False,
            ):
                if not db.inColumn("contracts", "address", cont.address):
                    code = EthGetCode.getCode(cont.address, i)
                    contracts[i].addByteCode(code)

        return contracts

    def tagsFromEtherscan(
        self,
        contracts: list[Contract],
        site: str = "etherscan",
        maxDuration: float = 5
    ) -> list[Contract]:
        """
        This function gets the tags from etherscan.io

        Args:
            list[Contract]: List of contract objects

        Returns:
            list[Contract]: List of contract objects
        """
        contracts = list(
            map(
                lambda x: x + self.tagGetter.getTags(x.address, site, maxDuration),
                tqdm(contracts, desc="Getting Tags", leave=False),
            )
        )
        return contracts

    def addContractsToDB(
        self,
        contracts: list[Contract],
        writeTags: bool = False,
        writeCode: bool = False,
        noForce: bool = True,
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
            contsAdded = 0
            with self.db() as db:
                # writes to "contracts" sheet
                for cont in tqdm(contracts, desc="Writing Contracts", leave=False):
                    contsAdded += db.writeContract(cont, noForce=noForce)

                print(f"{contsAdded} contracts added to database")

        if writeTags:
            tagsAdded = 0
            with self.db() as db:
                # wrties tags to "addressTags" sheet
                for cont in tqdm(contracts, desc="Writing Tags", leave=False):
                    tagsAdded += db.writeTags(cont.address, cont.tags)

                print(f"{tagsAdded} tags added to database")

    def __call__(self, *args: Any, **kwds: Any):
        start = time()
        counter = 0
        while True:
            print(f"Starting run {counter}")
            self.main()

            start += 60 * 5  # 5 mins
            if time() > start:
                start = time()
            else:
                dur = start - time()
                print(f"Sleeping for {dur:.0f} seconds")
                sleep(dur)

            counter += 1

    def main(self):
        contracts = self.getAddrsFromUltrasound()
        contracts = self.getByteCode(contracts)

        contracts = self.tagsFromEtherscan(contracts)
        self.addContractsToDB(contracts)

    def fullTagUpdate(self):
        with self.db() as db:
            addrs = db.getColumn("contracts", "address")

        addrs: list[str] = list(chain.from_iterable(addrs))

        contracts: list[Contract] = []

        for addr in tqdm(addrs, desc="Creating Contract Objects",  leave=False):
            cont = Contract([], addr, "noTags")
            contracts.append(cont)

        contracts = self.tagsFromEtherscan(contracts, maxDuration=3)
        self.addContractsToDB(contracts, writeTags=True)
        print(f"{len(contracts)} tags added to database")
        
    def reaplceByteCodeWithRaw(self):
        with self.db() as db:
            result = db.getColumn("contracts", "address, name")
        
        conts: list[Contract] = [
            Contract([name], addr, "forceSet")
            for addr, name in result
        ]
        
        print(f"{len(conts)} contracts found")
        conts = self.getByteCode(conts)
        self.addContractsToDB(conts, writeCode=True, noForce=False)



if __name__ == "__main__":
    scraper = WebScraper()
    scraper.fullTagUpdate()
    # scraper.reaplceByteCodeWithRaw()
    scraper()
