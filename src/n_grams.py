from getData import getOpCodes
from dataOps import ByteCodeIO
import os
from tqdm import tqdm
import collections


class nGramGen:
    def __init__(self, cutOff: float = .02):
        if os.path.exists("data\\opCodes.txt"):
            with open("data\\opCodes.txt", "r") as f:
                conts = list(map(eval, tqdm(f.readlines()[:100])))
            print("")
        else:
            with ByteCodeIO() as db:
                _byteCodes: list[str] = db.getColumn("contracts", "byteCode")
            conts = getOpCodes(_byteCodes)
            with open("data\\opCodes.txt", "w") as f:
                for cont in conts:
                    f.write(str(cont) + "\n")

        self.conts: list[list[int]] = conts
        contsFlat = [item for sublist in conts for item in sublist]
        opCodeFreq = dict(collections.Counter(contsFlat))
        self.opCodeFreq = dict(sorted(opCodeFreq.items(), key=lambda value: value[1], reverse=True))
        
        lenContsFlat = len(contsFlat)

        self.filteredOpCodeProp = {
            k: v/lenContsFlat
            for k, v in opCodeFreq.items()
            if v/lenContsFlat > cutOff}
    
    # def gen_all_nGrams(self, size: int) -> dict[tuple, int]:
    #     pass

    # def calcHeuristic(nGram: tuple) -> int:
    #     pass


if __name__ == "__main__":
    nGram = nGramGen()
