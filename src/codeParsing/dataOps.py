"""
this class is used to lookup the bytecode of a contract.
It uses the alchemy api to get the bytecode and then uses evmDasm to disassemble it.

Raises:
    requests.HTTPError: _description_
    Exception: _description_
"""

import json
from time import time
import sqlite3
import requests
import evmdasm
import os
from dotenv import load_dotenv
import logging
from itertools import chain
from addressScraping.contractObj import Contract
from typing import Tuple, Union

load_dotenv()

logging.basicConfig(
    level=logging.CRITICAL,
    #format=f"%(asctime)s %(levelname)s %(message)s",
)


class EthGetCode:
    __url = f"https://eth-mainnet.g.alchemy.com/v2/{os.getenv('alchemyApiKey')}"
    __payload = {
        "id": 0,
        "jsonrpc": "2.0",
        "params": [None, "latest"],
        "method": "eth_getCode",
    }
    __headers = {"accept": "application/json", "content-type": "application/json"}

    @staticmethod
    def getCode(
        _addr: str,
        _id: int,
        convert: bool = False
        ) -> evmdasm.EvmInstructions:
        paylode = EthGetCode.__payload
        paylode["id"] = _id
        paylode["params"][0] = _addr
        # logging.info(json.dumps(paylode, indent=4))

        response = requests.post(
            EthGetCode.__url, json=paylode, headers=EthGetCode.__headers
        )

        if response.status_code != 200:
            error = json.loads(response.text)["error"]
            raise requests.HTTPError(
                f"\n{response.status_code = }\n{error['code'] = }\n{error['message'] = }"
            )

        byteCode = json.loads(response.text)["result"]
        
        if not convert:
            return byteCode
        
        evmCode = evmdasm.EvmBytecode(byteCode)
        evmInstructions = evmCode.disassemble()

        return evmInstructions
    
    @staticmethod
    def convertCode(
        byteCode: str
        ) -> evmdasm.EvmInstructions:
        evmCode = evmdasm.EvmBytecode(byteCode)
        evmInstructions = evmCode.disassemble()
        return evmInstructions


class ByteCodeIO:
    def __init__(
        self,
        dbPath: str = "contStore.db"
        ):
        self.sqliteConnection = sqlite3.connect("contStore.db")
        self.cursor = self.sqliteConnection.cursor()
        # logging.info("Connected to SQLite")

    def __enter__(
        self
        ):
        return self

    def writeContract(
        self,
        cont: Contract,
        noForce: bool = False,
        **kwargs
        ) -> int:
        if noForce:
            command: str = "INSERT"
        else:
            command: str = "INSERT OR REPLACE"
        sqlite_insert_query = f"""{command} INTO contracts
                            (address, name, bytecode) 
                            VALUES (?, ?, ?);"""
        record: tuple[str, str, str] = (
            cont.address,
            kwargs.get("Name", ""),
            str(cont.byteCode),
        )
        
        if noForce:
            sqlite_select_query = """SELECT * from contracts where address = ?"""
            self.cursor.execute(sqlite_select_query, (cont.address,))

            records = self.cursor.fetchall()
            if len(records) > 0:
                # logging.info("Record already exists in contracts table")
                return 0

        # logging.info("Inserting record into contracts table")
        try:
            self.cursor.execute(sqlite_insert_query, record)
            self.sqliteConnection.commit()
            return 1
        except sqlite3.OperationalError as e:
            raise e
        except sqlite3.Error as error:
            # logging.critical("Failed to insert record into sqlite table\n", error)
            raise (error)

    def writeTags(
        self,
        _addr: str,
        tags: Union[
                list[str],
                set[str]
            ]
        ) -> int:
        if len(tags) == 0:
            return 0

        # check for existing tags
        sqlite_select_query = """SELECT tag from addressTags where address = ?"""
        self.cursor.execute(sqlite_select_query, (_addr,))
        records = self.cursor.fetchall()

        if len(records) > 0:
            # if there are existing tags, add the new tags to the list
            records = set(chain.from_iterable(records))
            # print(records)
            tags = set(tags) - records
            # print(tags)

        if len(tags) == 0:
            return 0

        record: set[Tuple[str, str]] = set(zip([_addr] * len(tags), tags))
        # if there are no existing tags, create a new record
        sqlite_insert_query = """INSERT INTO addressTags
                            (address, tag) 
                            VALUES (?, ?);"""

        try:
            self.cursor.executemany(sqlite_insert_query, record)
            self.sqliteConnection.commit()
            return len(tags)
        except sqlite3.OperationalError as e:
            raise e
        except sqlite3.Error as error:
            # logging.critical("Failed to insert records into sqlite table\n", error)
            raise (error)

    def inNames(
        self,
        name: str | list[str]
    ) -> bool | list[str]:
        if isinstance(name, str):
            sqlite_select_query = """SELECT * from contracts where name = ?"""
            self.cursor.execute(sqlite_select_query, (name,))
            records = self.cursor.fetchall()
            return len(records) > 0
        if isinstance(name, list):
            sqlite_select_query = """SELECT name from contracts"""
            self.cursor.execute(sqlite_select_query)
            records = self.cursor.fetchall()
            records = list(chain.from_iterable(records))
            # find all values in name that are not in records
            return [n for n in name if n not in records]

    def inColumn(
        self,
        table: str,
        column: str,
        value: str
    ) -> bool:
        if not isinstance(value, str):  # or isinstance(value, list)):
            raise Exception("name must be of type str or list[str]")

        sqlite_select_query = f"""SELECT * from {str(table)} where {str(column)} = ?"""
        self.cursor.execute(sqlite_select_query, (value,))
        records = self.cursor.fetchall()
        return len(records) > 0

    def getColumn(
        self,
        table: str,
        column: str
    ) -> list[str]:
        sqlite_select_query = f"""SELECT {str(column)} from {str(table)}"""
        self.cursor.execute(sqlite_select_query)
        records = self.cursor.fetchall()
        return records

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):
        if self.cursor:
            self.cursor.close()
            # logging.info("The SQLite cursor is closed")
        if self.sqliteConnection:
            self.sqliteConnection.close()
            # logging.info("The SQLite connection is closed")


if __name__ == "__main__":
    raise Exception("This file should not be run as main")
    # addr = '0x4da27a545c0c5B758a6BA100e3a049001de870f5'
    # code = EthGetCode.getCode(addr, 0)
    # ByteCodeIO.writeCode(addr, code)
