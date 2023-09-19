from dataclasses import dataclass, field
from functools import total_ordering
from typing import Generator, List, Tuple, Self
from itertools import product
import numpy as np
from multiprocessing import Pool
from collections import Counter


# defines the nGramObj class
@total_ordering
@dataclass
class nGramObj:
    nGram: Tuple[int, ...] = field(default_factory=tuple, init=True)
    count: int = field(default=0, init=True)
    children: Generator[Self, None, None] = field(init=False)

    def __init__(
        self,
        nGram: Tuple[int, ...],
        count: int,
        corpus: List[list[int]],
        opCodes: list[int],
        runOnCorpus: bool = False,
        genChildren: bool = False,
    ) -> None:
        self.nGram = nGram
        self.count = count

        if runOnCorpus:
            self.count += self.runOnCorpus(corpus)

        if genChildren:
            self.children = self.makeChildren(corpus, opCodes)

    def __str__(self) -> str:
        return f"({self.nGram}, {self.count})"

    def __hash__(self) -> int:
        return hash(self.nGram)

    def __eq__(self, __value: Self) -> bool:
        if not isinstance(__value, nGramObj):
            raise TypeError(f"__value must be of type {nGramObj}")
        return self.heruistic() == __value.heruistic()

    def __lt__(self, __value: Self) -> bool:
        if not isinstance(__value, nGramObj):
            raise TypeError(f"__value must be of type {nGramObj}")
        return self.heruistic() < __value.heruistic()

    def __len__(self) -> int:
        return len(self.nGram)

    def nGramCheck(self, nGram: Tuple[int, ...]) -> bool:
        """compares the object with a given nGram

        Args:
            nGram (Tuple[int, ...]): nGram being passed

        Returns:
            bool: true if they match, false if they dont
        """
        if len(self) != len(nGram):
            print(f"{self.nGram = }")
            print(f"{nGram = }")
            print(f"{len(self) = } {len(nGram) = }")
            raise ValueError("nGrams must be the same length to be compared")
        return self.nGram == nGram

    def __repr__(self) -> str:
        return f"nGramObj({self.nGram}, {self.count})"

    # def __add__(self, __value: Self) -> Self:
    #     if self != __value:
    #         raise ValueError("nGrams must be the same to be added")
    #     if self.nGram != __value.nGram:
    #         raise ValueError("nGrams must be the same to be added")
    #     self.count += __value.count
    #     return nGramObj(self.nGram, self.count + __value.count, None, None)

    def __iadd__(self, __value: Self) -> Self:
        if self != __value:
            raise ValueError("nGrams must be the same to be added")
        if self.nGram != __value.nGram:
            raise ValueError("nGrams must be the same to be added")
        self.count += __value.count
        return self

    def __int__(self) -> int:
        return self.count

    def __float__(self) -> float:
        return float(self.count)

    def __bool__(self) -> bool:
        return bool(self.count)

    def makeChildren(
        self, corpus: List[list[int]], opCodeList: list[int]
    ) -> Generator[Self, None, None]:
        try:
            # orders the opcodes in the corpus by frequency
            contsFlat = [item for sublist in corpus for item in sublist]
            opCodeFreq = dict(Counter(contsFlat))
            opCodePairs = list(product(opCodeList, repeat=2))
            opCodePairs = sorted(
                opCodePairs,
                key=lambda pair: opCodeFreq[pair[0]] + opCodeFreq[pair[1]],
                reverse=True,
            )
            # gernerates the new opCodes
            for frontToken, backToken in opCodePairs:
                yield nGramObj(
                    self.nGram + (backToken,),
                    0,
                    corpus,
                    opCodeList,
                    runOnCorpus=True,
                    genChildren=True,
                )

                yield nGramObj(
                    (frontToken,) + self.nGram,
                    0,
                    corpus,
                    opCodeList,
                    runOnCorpus=True,
                    genChildren=True,
                )
        except KeyboardInterrupt:
            return

    def heruistic(self) -> int:
        return self.count * (len(self.nGram) - 1)

    def runOnCorpus(self, corpus: List[list[int]]) -> int:
        self.count = localRunOnCorpus(corpus, self.nGram)
        return self.count


def localRunOnCorpus(corpus: List[list[int]], selfNgram: Tuple[int, ...]) -> int:
    _nGram = np.array(selfNgram, dtype=np.uint8) + 1
    count = 0
    cores = 12
    pool = Pool(cores)
    params = [(elem, selfNgram, _nGram) for elem in corpus]
    count = pool.imap_unordered(runParalell, params, chunksize=len(corpus) // cores)
    # for elem in corpus:
    #     param = (elem, selfNgram, _nGram)
    #     count += runSingle(*param)
    return sum(count)


def runParalell(param) -> int:
    try:
        return runSingle(*param)
    except KeyboardInterrupt:
        return 0


def runSingle(_elem: list[int], selfNgram: Tuple[int, ...], _nGram: np.ndarray) -> int:
    # tiles the elem array by the width of the nGram due to the sliding window
    elem = np.array(_elem, dtype=np.uint8)
    mod = elem.size % len(selfNgram)
    # if mod is 0 return 1 else do nothing
    # avoids the missing of the sliding window
    elem = np.pad(elem + 1, (0, len(selfNgram) + mod + 1)).astype(np.uint8)
    elem = np.tile(elem, _nGram.size)
    # repeats the nGram to cover more than the array
    div = elem.size // len(selfNgram)
    nGram = np.tile(_nGram, div + 1)
    # gets the length diff
    diff = nGram.size - elem.size
    # print(f"{nGram.size - elem.size = }")
    # print(f"{nGram.size = }")
    # print(f"{elem.size = }")
    # exit(0)
    # pads out to length
    elem = np.pad(elem, (0, diff)).astype(np.uint8)
    # gets diff
    elem = np.subtract(elem, nGram).astype(np.uint8)
    # finds all runs of zeros
    ranges = zero_runs(elem)
    # process them into run length
    diff = np.subtract(ranges[:, 1], ranges[:, 0])
    diff = np.sum(diff // len(selfNgram))
    return int(diff)


def zero_runs(a: np.ndarray) -> np.ndarray:
    # Create an array that is 1 where a is 0, and pad each end with an extra 0.
    iszero = np.pad(np.equal(a, 0), 1)
    absdiff = np.abs(np.diff(iszero))
    # Runs start and end where absdiff is 1.
    ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
    return ranges
