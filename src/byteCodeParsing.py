from typing import Any
from codeParsing.dataOps import ByteCodeIO
from addressScraping.contractObj import Contract


def findLinks(cont: Contract) -> list[str]:
    """finds addresses in the bytecode

    Args:
        cont (Contract): contract object to be checked

    Returns:
        list[str]: list of addresses its found
    """
    ...

def parseByteCode(cont: Contract) -> Any:
    """takes in a ContractObj and parses the bytecode
    into a list of opcodes and their arguments

    Args:
        cont (Contract): contract object to be processed

    Returns:
        Any: _description_
    """

def checkAddrForValidity(addr: str) -> bool:
    """checks if the address is valid
    Does this address have any bytecode?
    Does this address  have any transactions/ether?

    Args:
        addr (str): address to be checked

    Returns:
        bool: True if valid, False otherwise
    """
    ...


if __name__ == "__main__":
    with ByteCodeIO() as db:
        contracts = db.getColumn("contracts", "address, byteCode")

    for addr, byteCode in contracts:
        contract = Contract([], addr, 'noTags', byteCode=byteCode)
