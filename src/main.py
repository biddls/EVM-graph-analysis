"""
This checks N sources for address and or tags and staored the data in an SQL database
"""

from time import sleep, time
from typing import Any
from addressScraping.contractObj import Contract
from addressScraping import usMoney
from addressScraping.contTagScraping import TagGetter
from codeParsing.addrLookup import EthGetCode, ByteCodeIO
from tqdm import tqdm


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
        print(f"{len(contracts)} contracts found from ultrasound.money")
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
                enumerate(contracts), desc="Getting ByteCode", total=len(contracts)
            ):
                if db.inColumn("contracts", "address", cont.address):
                    code = EthGetCode.getCode(cont.address, i)
                    contracts[i].addByteCode(code)

        return contracts

    def tagsFromEtherscan(self, contracts: list[Contract]) -> list[Contract]:
        """
        This function gets the tags from etherscan.io

        Args:
            list[Contract]: List of contract objects

        Returns:
            list[Contract]: List of contract objects
        """
        contracts = list(
            map(
                lambda x: x + self.tagGetter.getTags(x.address),
                tqdm(contracts, desc="Getting Tags"),
            )
        )
        return contracts

    def addContractsToDB(self, contracts: list[Contract]) -> None:
        """
        This function adds the contracts to the database

        Args:
            list[Contract]: List of contract objects
        """
        with self.db() as db:
            # writes to "contracts" sheet
            for cont in tqdm(contracts, desc="Writing Contracts"):
                db.writeContract(cont)
            # wrties tags to "addressTags" sheet
            for cont in tqdm(contracts, desc="Writing Tags"):
                db.addTags(cont.address, cont.tags)

    def __call__(self, *args: Any, **kwds: Any):
        start = time()
        while True:
            self.main()
            start += 60 * 5  # 5 mins
            if time() < start:
                start = time()
            else:
                sleep(start - time())

    def main(self):
        contracts = self.getAddrsFromUltrasound()
        contracts = self.getByteCode(contracts)

        contracts = self.tagsFromEtherscan(contracts)
        self.addContractsToDB(contracts)


if __name__ == "__main__":
    scraper = WebScraper()

    import cProfile
    import pstats
    import os

    prof = cProfile.Profile()
    prof.run("scraper.main()")
    prof.dump_stats("output.prof")

    stream = open("output.csv", "w")
    stats = pstats.Stats("output.prof", stream=stream)
    stats.sort_stats("cumtime")
    stats.print_stats()
