import json
import requests
import evmdasm as evmDasm
import os
from dotenv import load_dotenv

load_dotenv()


class EthGetCode:
    __url = f"https://eth-mainnet.g.alchemy.com/v2/{os.getenv('alchemyApiKey')}"
    __payload = {
        "id": 0,
        "jsonrpc": "2.0",
        "params": [None, "latest"],
        "method": "eth_getCode"
    }
    __headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    @staticmethod
    def getCode(_addr: str, _id: int) -> evmDasm.EvmBytecode:
        paylode = EthGetCode.__payload
        paylode['id'] = _id
        paylode['params'][0] = _addr
        response = requests.post(
            EthGetCode.__url,
            json=EthGetCode.__payload,
            headers=EthGetCode.__headers)

        if response.status_code != 200:
            error = json.loads(response.text)['error']
            raise requests.HTTPError(f"\n{response.status_code = }\n{error['code'] = }\n{error['message'] = }")

        byteCode = json.loads(response.text)['result']
        evmCode = evmDasm.EvmBytecode(byteCode)
        evmInstructions = evmCode.disassemble()

        for instr in evmInstructions:
            print(instr.name, instr.operand)

        return evmInstructions


class ByteCodeIO:
    @staticmethod
    def writeCode(code: evmDasm.EvmBytecode, **kwargs):
        pass

    @staticmethod
    def readCode(path: str):
        pass



if __name__ == '__main__':
    EthGetCode.getCode('0x4da27a545c0c5B758a6BA100e3a049001de870f5', 0)
