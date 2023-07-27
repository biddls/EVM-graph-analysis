import json
# import evmDasm
import requests
import evmdasm
import os
from dotenv import load_dotenv
import logging

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
    def getCode(_addr: str, _id: int) -> evmdasm.EvmInstructions:
        paylode = EthGetCode.__payload
        paylode['id'] = _id
        paylode['params'][0] = _addr
        logging.info(json.dumps(paylode, indent=4))
        response = requests.post(
            EthGetCode.__url,
            json=paylode,
            headers=EthGetCode.__headers)

        if response.status_code != 200:
            error = json.loads(response.text)['error']
            raise requests.HTTPError(f"\n{response.status_code = }\n{error['code'] = }\n{error['message'] = }")

        byteCode = json.loads(response.text)['result']
        evmCode = evmdasm.EvmBytecode(byteCode)
        evmInstructions = evmCode.disassemble()

        return evmInstructions


class ByteCodeIO:
    contractsPath = "contractsParsed.jsonl"

    @staticmethod
    def writeCode(_addr: str, instructions: evmdasm.EvmInstructions, **kwargs):
        cont = {
            'Code':
                [{
                    'Name': instr.name,
                    'Operand': instr.operand
                } for instr in instructions],
            'Addr': _addr,
        }
        for key, value in zip(kwargs.keys(), kwargs.values()):
            if key in ['Code', 'Addr']:
                continue
            cont[key] = value

        # todo: add appending to JsonL file
        ByteCodeIO.__writeDict(cont)
        logging.info("Code not completed for writeCode function")
        exit()

    @staticmethod
    def __writeDict(data: dict):
        del data['Code']
        if not os.path.exists(ByteCodeIO.contractsPath):
            with open(ByteCodeIO.contractsPath, 'w+') as f:
                pass
        with open(ByteCodeIO.contractsPath, 'r+') as contracts:
            line = contracts.readline()

            if line == '':
                jout = json.dumps(data)
                contracts.write(jout + '\n')
                logging.info("File empty")
                return
            found = False
            while line:
                if json.loads(line)['Addr'] == data['Addr']:
                    logging.info("address already found")
                    jout = json.dumps(data)
                    contracts.writelines(jout + '\n')
                    exit(0)
                else:
                    line = contracts.readline()
                    logging.info(f"Cont is not found: {line}")
                    contracts.writelines(line + '\n')
                line = contracts.readline()

    @staticmethod
    def readCode(path: str):
        pass


if __name__ == '__main__':
    addr = '0x4da27a545c0c5B758a6BA100e3a049001de870f5'
    code = EthGetCode.getCode(addr, 0)
    ByteCodeIO.writeCode(addr, code)
