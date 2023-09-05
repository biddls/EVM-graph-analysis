from getData import getOpCodes
from dataclasses import field
from dataOps import ByteCodeIO
import os
from tqdm import tqdm
import collections
from itertools import product
from classification.nGramObj import nGramObj
from typing import List


class nGramGen:
    nGrams: List[nGramObj] = field(default_factory=list, init=False)

    def __init__(self, finalCount: int, maxCount: int, cutOff: float = 0.02):
        # loads in cached data if it exists else generates it
        if finalCount > maxCount:
            raise ValueError(
                f"finalCount ({finalCount}) must be less than or equal to maxCount ({maxCount})"
            )
        self.finalCount = finalCount
        self.maxCount = maxCount

        if os.path.exists("data\\opCodes.txt"):
            with open("data\\opCodes.txt", "r") as f:
                conts = list(map(eval, tqdm(f.readlines()[:5])))
            print("")
        else:
            with ByteCodeIO() as db:
                _byteCodes: list[str] = db.getColumn("contracts", "byteCode")
            conts = getOpCodes(_byteCodes)
            with open("data\\opCodes.txt", "w") as f:
                for cont in conts:
                    f.write(str(cont) + "\n")

        # all the data
        self.corpus: list[list[int]] = conts
        contsFlat = [item for sublist in conts for item in sublist]
        opCodeFreq = dict(collections.Counter(contsFlat))

        # sort by most frequent
        self.opCodeFreq = dict(
            sorted(opCodeFreq.items(), key=lambda value: value[1], reverse=True)
        )

        self.lenContsFlat = sum(opCodeFreq.values())
        self.opCodes = list()
        for k, _ in self.opCodeFreq.items():
            # print(k, v)
            self.opCodes.append(k)

        # filter out opCodes that are too rare to find inital set of nGrams
        self.filteredOpCodeProp: dict[int, float] = {
            k: v / self.lenContsFlat
            for k, v in opCodeFreq.items()
            if v / self.lenContsFlat > cutOff
        }

        self.majority_opCodes: set[int] = set(self.filteredOpCodeProp.keys())

        print("data loaded")

    def gen_all_nGrams(self, size: int) -> None:
        self.nGrams = list(
            map(
                lambda nGram: nGramObj(
                    nGram,
                    0,
                    self.corpus,
                    self.opCodes,
                    runOnCorpus=True,
                    genChildren=True,
                ),
                tqdm(
                    product(self.majority_opCodes, repeat=size),
                    total=len(self.majority_opCodes) ** size,
                ),
            )
        )
        print("nGrams generated")

    def loadFromCache(self) -> None:
        with open("nGrams.txt", "r") as f:
            temp: list[tuple[tuple[int, ...], int]] = list(map(eval, f.readlines()))
        self.nGrams = list(
            map(
                lambda nGram: nGramObj(
                    *nGram, self.corpus, self.opCodes, genChildren=True
                ),
                temp,
            )
        )
        print(f"{len(self.nGrams)} nGrams loaded from file")
        for i, child in enumerate(self.nGrams):
            if not isinstance(child, nGramObj):
                raise ValueError(f"None child found in nGrams @ {i} | {child = }")

    def genBetter_nGrams(self, batchSize: int = 100) -> None:
        itters = len(self.nGrams)
        itter = tqdm(initial=itters)
        try:
            while True:
                _max = max(self.nGrams)
                for _ in range(batchSize):
                    try:
                        child = next(_max.children)
                    except StopIteration:
                        self.cull(self.maxCount)
                        break
                    self.nGrams.append(child)

                if _max != (temp := max(self.nGrams)):
                    itter.set_description_str(f"New MAX {temp.heruistic()}")

                itter.update(batchSize)
                itters += batchSize
                if len(self.nGrams) > self.maxCount * 1.5:
                    self.cull(self.finalCount)
                    itter.set_description_str(
                        f"Cull @ {itters} | av {len(self.nGrams)/sum([nGram.heruistic() for nGram in self.nGrams]):.2f}"
                    )
        except KeyboardInterrupt:
            itter.close()
            self.cull(self.maxCount)
            print("SAVING PROGRESS")
            print(f"{len(self.nGrams) = } Saved to file")
            self.save()

    def save(self) -> None:
        with open("nGrams.txt", "w") as f:
            for nGram in self.nGrams:
                f.write(str(nGram) + "\n")

    def cull(self, _max) -> None:
        temp = list(set(self.nGrams))
        self.nGrams = list(filter(lambda nGram: nGram.count > 0, temp))
        self.nGrams = sorted(self.nGrams, reverse=True)[:_max]


if __name__ == "__main__":
    nGramManager = nGramGen(2000, 10000)
    if os.path.exists("nGrams.txt"):
        nGramManager.loadFromCache()
    else:
        nGramManager.gen_all_nGrams(3)
        if len(nGramManager.nGrams) != (len(nGramManager.majority_opCodes) ** 3):
            raise ValueError("nGrams are not being generated correctly")

    nGramManager.genBetter_nGrams()
