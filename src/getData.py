from dataOps import ByteCodeIO, opCodeLookup
from tqdm import tqdm
import evmdasm
import os
import collections
from matplotlib import pyplot as plt


def getOpCodes(byteCodes: list[str]) -> list[list[int]]:
    """gets all the opcodes from the bytecode

    Args:
        byteCodes (list[str]): list of bytecode from contracts

    Returns:
        list[list[int]]: list of list of opcodes
    """
    opCodeList: list[list[int]] = list(
        map(
            lambda x: getOpCode(x[0]),
            tqdm(byteCodes)
        )
    )
    return opCodeList

def getOpCode(byteCode: str) -> list[int]:
    evmCode = evmdasm.EvmBytecode(byteCode)
    evmCode = evmCode.disassemble()
    return list(map(lambda x: x.opcode, evmCode))

def recursiveNgramGen(contList: list[list[int]]) -> dict[tuple[int], int]:
    """generates most widley used n ngrams

    Args:
        contList (list[list[int]]): list of contracts opcodes
        n (int): size of list of ngrams

    Returns:
        dict[tuple[int]]: list of ngrams
    """
    ngrams: dict[tuple[int], int] = {}

    for cont in tqdm(contList, desc="Generating ngrams"):
        for i in range(len(cont) - 1):
            pass

    return ngrams

def getStats(_conts, p=True):
    # temp = _conts[0]
    # codes = []
    # for code in temp:
    #     try:
    #         codes.append(opCodeLookup.convertOpCode(code))
    #     except KeyError:
    #         pass
    # print(f'|{"|".join(codes)}|')
    # print(f"{len(codes) = }, {len(temp) = }")
    exit(0)
    lenConts = len(_conts)
    minLength = len(min(_conts, key=lambda x: len(x)))
    maxLength = len(max(_conts, key=lambda x: len(x)))
    lengths = [len(x) for x in _conts]
    averageLength = int(sum(lengths) / lenConts)
    contsFlat = [item for sublist in _conts for item in sublist]
    lenContsFlat = len(contsFlat)
    opCodeFreq = dict(collections.Counter(contsFlat))
    opCodeFreq = dict(sorted(opCodeFreq.items(), key=lambda value: value[1], reverse=True))

    if not p:
        return
    print(f"{lenConts = }")
    print(f"{minLength = }")
    print(f"{maxLength = }")
    print(f"{averageLength = }")
    print(f"{lenContsFlat = }")
    print(f"{averageLength * lenConts = }")

    # removes the long tail of opCodes that are used very infrequently
    cutOff = 0.02
    filteredOpCodeFreq = {
        k: v/lenContsFlat
        for k, v in opCodeFreq.items()
        if v/lenContsFlat > cutOff}
    
    names = list(filteredOpCodeFreq.keys())
    # print(names)
    names = [opCodeLookup.convertOpCode(x) for x in names]
    # print(names)
    values = list(filteredOpCodeFreq.values())
    print(f"At {cutOff = } The toal proportion left is:{round(sum(values), 3) = }")
    print(f"This is captured by only {len(names)} opCodes")
    
    return
    
    _, ax = plt.subplots(1)
    ax.bar(range(len(filteredOpCodeFreq)), values, tick_label=names)
    plt.title(f"opCode porpotion use, for all contracts, this data shows the top {round(sum(values)*100)}% by opCode use")
    plt.xlabel("opCode")
    plt.ylabel("prorortion of opCodes")
    ax.set_ylim(0, max(filteredOpCodeFreq.values()) * 1.1)
    plt.show()

    plt.hist(lengths, bins=20)
    plt.title("histogram of contract length")
    plt.xlabel("number of opCodes in contract")
    plt.ylabel("frequency")
    plt.show()


if __name__ == "__main__":
    # print(opCodeLookup.convertOpCode(0))
    # print(opCodeLookup.opCodeTable)
    # exit(0)
    if os.path.exists("data\\opCodes.txt"):
        with open("data\\opCodes.txt", "r") as f:
            conts = list(map(eval, tqdm(f.readlines()[:10])))
        print("")
    else:
        with ByteCodeIO() as db:
            _byteCodes: list[str] = db.getColumn("contracts", "byteCode")
        conts = getOpCodes(_byteCodes)
        with open("data\\opCodes.txt", "w") as f:
            for cont in conts:
                f.write(str(cont) + "\n")
    getStats(conts)
