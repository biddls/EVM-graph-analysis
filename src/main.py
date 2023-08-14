"""
This checks N sources for address and or tags and staored the data in an SQL database
"""

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

    @staticmethod
    def getByteCode(contracts: list[Contract]) -> list[Contract]:
        """
        This function finds and attaches the bytecode to the contracts

        Args:
            list[Contract]: List of contract objects

        Returns:
            list[Contract]: List of contract objects
        """
        for i, cont in tqdm(
            enumerate(contracts), desc="Getting ByteCode", total=len(contracts)
        ):
            code = EthGetCode.getCode(cont.address, i)
            cont.addByteCode(code)

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


if __name__ == "__main__":
    scraper = WebScraper()
    contracts = scraper.getAddrsFromUltrasound()
    contracts = scraper.getByteCode(contracts)

    temp: list[Contract]
    index = 0
    while True:
        if contracts[index].byteCode is not None:
            temp = scraper.tagsFromEtherscan([contracts[index]])
            if len(temp[0].tags) > 0:
                break
        index += 1
    # contracts = scraper.tagsFromEtherscan(contracts)
    # scraper.addContractsToDB(contracts)
    scraper.addContractsToDB(temp)
