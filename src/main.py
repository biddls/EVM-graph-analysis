"""
This checks N sources for address and or tags and staored the data in an SQL database
"""

from addressScraping.contractObj import Contract
from addressScraping import usMoney

## TO DO:
## Get addresses from https://ultrasound.money/
## Get tags from https://etherscan.io/


def getAddrsFromUltrasound() -> list[Contract]:
    """
    This function gets the addresses from ultrasound.money

    Returns:
        list[Contract]: List of contract objects
    """
    contracts = usMoney.getAddresses()
    return contracts


def tagsFromEtherscan(contracts: list[Contract]) -> list[Contract]:
    """
    This function gets the tags from etherscan.io

    Args:
        list[Contract]: List of contract objects

    Returns:
        list[Contract]: List of contract objects
    """
    ...


def checkIfInDB(contracts: list[Contract]) -> list[Contract]:
    """
    This function checks if the contracts are in the database

    Args:
        list[Contract]: List of contract objects

    Returns:
        list[Contract]: List of contract objects
    """
    ...


def addContractsToDB(contracts: list[Contract]) -> None:
    """
    This function adds the contracts to the database

    Args:
        list[Contract]: List of contract objects
    """
    ...


def getByteCode(contracts: list[Contract]) -> list[Contract]:
    """
    This function finds and attaches the bytecode to the contracts

    Args:
        list[Contract]: List of contract objects

    Returns:
        list[Contract]: List of contract objects
    """
    ...
