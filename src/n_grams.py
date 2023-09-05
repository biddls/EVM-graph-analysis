from getData import getOpCodes
from dataOps import ByteCodeIO
import os
from tqdm import tqdm
import collections
from itertools import product
from classification.nGramObj import nGramObj
from typing import List
from classification.PCA import getDiffers


class nGramGen:
    nGrams: List[nGramObj] = list()
    done_nGrams: set[nGramObj] = set()

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
                conts = list(map(eval, tqdm(f.readlines())))
            print("")
        else:
            with ByteCodeIO() as db:
                _byteCodes: list[str] = db.getColumn("contracts", "byteCode")
            conts = getOpCodes(_byteCodes)
            with open("data\\opCodes.txt", "w") as f:
                for cont in conts:
                    f.write(str(cont) + "\n")

        conts = list(filter(lambda x: len(x) != 0, conts))
        best = getDiffers(conts, dims=10, n_clusters=50)
        conts = list(map(lambda x: conts[x], best))

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
        self.nGrams += list(
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
        self.cull(self.maxCount)
        print("nGrams generated")

    def loadFromCache(self) -> None:
        with open("nGrams.txt", "r") as f:
            temp: list[tuple[tuple[int, ...], int]] = list(map(eval, f.readlines()))
        self.nGrams += list(
            map(
                lambda nGram: nGramObj(
                    *nGram, self.corpus, self.opCodes, genChildren=True
                ),
                temp,
            )
        )
        print(f"{len(self.nGrams)} nGrams loaded from file")

        with open("done_nGrams.txt", "r") as f:
            temp: list[tuple[tuple[int, ...], int]] = list(map(eval, f.readlines()))
        self.done_nGrams = set(
            map(
                lambda nGram: nGramObj(*nGram, self.corpus, self.opCodes),
                temp,
            )
        )
        print(f"{len(self.done_nGrams)} processed nGrams loaded from file")

    def genBetter_nGrams(self, batchSize: int = 10) -> None:
        itters = len(self.nGrams)
        itter = tqdm(initial=itters)
        try:
            while True:
                _max = max(set(self.nGrams) - self.done_nGrams)
                for _ in range(batchSize):
                    try:
                        child = next(_max.children)
                    except StopIteration:
                        self.cull(self.maxCount)
                        self.done_nGrams.add(_max)
                        self.nGrams.remove(_max)
                        break
                    self.nGrams.append(child)

                itter.update(batchSize)
                itters += batchSize
                if len(self.nGrams) > self.maxCount * 1.5:
                    self.cull(self.finalCount)
                    av = round(
                        sum([nGram.heruistic() for nGram in self.nGrams])
                        / len(self.nGrams),
                        2,
                    )
                    best = _max.heruistic()
                    longest = len(max(self.nGrams, key=lambda nGram: len(nGram.nGram)))
                    itter.set_description_str(
                        f"{av = } | {best = } | maxLen = {longest}"
                    )
        except KeyboardInterrupt:
            itter.close()
            self.cull(self.maxCount)
            print("SAVING PROGRESS")
            self.save(self.nGrams, "nGrams.txt")
            self.save(self.done_nGrams, "done_nGrams.txt")

    def save(self, nGramList: List[nGramObj] | set[nGramObj], path: str) -> None:
        with open(path, "w") as f:
            for nGram in nGramList:
                f.write(str(nGram) + "\n")
        print(f"{len(nGramList)} nGrams saved to {path}")

    def cull(self, _max) -> None:
        temp = list(set(self.nGrams))
        self.nGrams = list(filter(lambda nGram: nGram.count > 0, temp))
        self.nGrams = sorted(self.nGrams, key=None, reverse=True)[:_max]


if __name__ == "__main__":
    nGramManager = nGramGen(2000, 10000)
    if (os.path.exists("nGrams.txt")) and (os.path.exists("done_nGrams.txt")):
        nGramManager.loadFromCache()
    else:
        nGramManager.gen_all_nGrams(3)

    nGramManager.genBetter_nGrams()

# todo convert this into nGrams of nGrams instead as that is likely to be faster, ah well
