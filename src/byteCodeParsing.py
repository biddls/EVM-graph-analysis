from typing import Any
from codeParsing.dataOps import ByteCodeIO
from addressScraping.contractObj import Contract
from tqdm import tqdm
import logging

# to shutup the logger
logging.basicConfig(level=logging.CRITICAL)

class graphGen:
    @staticmethod
    def findLinks(cont: Contract) -> Contract:
        """finds addresses in the bytecode

        Args:
            cont (Contract): contract object to be checked

        Returns:
            list[str]: list of addresses its found
        """
        byteCode = cont.dissassemble()
        # print(byteCode is None)
        links: set[str] = set()
        for op in byteCode:
            if len(op.operand) != 40:
                pass
            elif op.operand == 'ffffffffffffffffffffffffffffffffffffffff':
                pass
            elif graphGen.checkAddrForValidity(op.operand):
                links.add(op.operand)
        if links:
            cont.addLinks(links)
        return cont

    @staticmethod
    def checkAddrForValidity(addr: str) -> bool:
        """checks if the address is valid
        Does this address have any bytecode?
        Does this address  have any transactions/ether?

        Args:
            addr (str): address to be checked

        Returns:
            bool: True if valid, False otherwise
        """
        # TODO: check if address has any bytecode
        # TODO: check if address has any transactions
        # TODO: check if address has any ether
        # TODO: check if address has already been checked
        return True


if __name__ == "__main__":
    with ByteCodeIO() as db:
        contracts = db.getColumn("contracts", "address, byteCode")

    linksFound: int = 0
    
    loop: tqdm = tqdm(
        enumerate(contracts),
        desc=f"Links found: {linksFound}",
        total=len(contracts)
    )
    
    for i, (addr, byteCode) in loop:
        cont = Contract([], addr, 'noTags', byteCode=byteCode)
        graphGen.findLinks(cont)
        linksFound += len(cont.links)
        
        
        loop.set_description(f"Links: {linksFound}, Interconectivity: {linksFound/(i+1):.2f}")
        
