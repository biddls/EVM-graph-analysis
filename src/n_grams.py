from getData import getOpCodes
from dataOps import ByteCodeIO
import os
from tqdm import tqdm
import collections
from typing import Self, List, TypedDict
from itertools import product
from classification.nGramObj import nGramObj


class nGramGen:
    def __init__(self, cutOff: float = .02):
        # loads in cached data if it exists else generates it
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

        # all the data
        self.conts: list[list[int]] = conts
        contsFlat = [item for sublist in conts for item in sublist]
        opCodeFreq = dict(collections.Counter(contsFlat))

        # sort by most frequent
        self.opCodeFreq = dict(sorted(opCodeFreq.items(), key=lambda value: value[1], reverse=True))
        
        self.lenContsFlat = sum(opCodeFreq.values())

        # filter out opCodes that are too rare to find inital set of nGrams
        self.filteredOpCodeProp: dict[int, float] = {
            k: v/self.lenContsFlat
            for k, v in opCodeFreq.items()
            if v/self.lenContsFlat > cutOff}
        
        self.majority_opCodes: set[int] = set(self.filteredOpCodeProp.keys())
    
    def gen_all_nGrams(self, size: int) -> List[nGramObj]:
        return list(
            map(
                lambda x: 
                    nGramObj(x, self.lenContsFlat, None),
                product(
                    self.majority_opCodes,
                    repeat=size
                )
            )
        )

    # def calcHeuristic(nGram: tuple) -> int:
    #     pass

# Holds all the different nGrams with auto replacement
# if a longer engram with a better heruistic is found it will replace the old one
class nGramStorage(TypedDict):
    data: List[Self] | nGramObj
    
    # def __setitem__(self, __key: List[Tuple[int, ...]], __value: nGramObj) -> None:
    #     key = self.data[__key[0]]
    #     for nGram in __key:
    #         # if it is already "beaten" skip it
    #         if isinstance(key, nGramObj):
    #             continue
    #         # write over it and update it
    #         if key < __value:
    #             # write over it with the new nGram object
    #             self.data[nGram] = __value
    #             return
    #         key = self.data[nGram]      

    #     return super().__setitem__(__key, __value)


if __name__ == "__main__":
    nGram = nGramGen()
    first = nGram.gen_all_nGrams(3)
    if (len(first) != (len(nGram.majority_opCodes)**3)):
        raise ValueError("nGrams are not being generated correctly")
    exit(0)
    temp = {0: 1, 1: 2, 2: 3}
    a = nGramStorage(temp)
    print(a)
