from dataclasses import dataclass, field
from functools import total_ordering
from typing import Generator, List, Tuple, Self, Dict
from itertools import product

# from collections.abc import Iterator
# from tqdm import tqdm
import numpy as np


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
        for frontToken, backToken in product(opCodeList, repeat=2):
            yield nGramObj(
                self.nGram + (backToken,),
                0,
                corpus,
                opCodeList,
                genChildren=True,
            )

            yield nGramObj(
                (frontToken,) + self.nGram,
                0,
                corpus,
                opCodeList,
                genChildren=True,
            )

    def heruistic(self) -> int:
        return self.count * (len(self.nGram) - 1)

    def runOnCorpus(self, corpus: List[list[int]]) -> int:
        _nGram = np.array(self.nGram, dtype=np.uint8) + 1
        for elem in corpus:
            # tiles the elem array by the width of the nGram due to the sliding window
            elem = np.array(elem, dtype=np.uint8)
            mod = elem.size % len(self.nGram)
            # if mod is 0 return 1 else do nothing
            # avoids the missing of the sliding window
            elem = np.pad(elem + 1, (0, len(self.nGram) + mod + 1))
            elem = np.tile(elem, _nGram.size)
            # repeats the nGram to cover more than the array
            div = elem.size // len(self.nGram)
            nGram = np.tile(_nGram, div + 1)
            # gets the length diff
            diff = nGram.size - elem.size
            # print(f"{nGram.size - elem.size = }")
            # print(f"{nGram.size = }")
            # print(f"{elem.size = }")
            # exit(0)
            # pads out to length
            elem = np.pad(elem, (0, diff))
            # gets diff
            elem = elem - nGram
            # finds all runs of zeros
            ranges = self.zero_runs(elem)
            # process them into run length
            diff = ranges[:, 1] - ranges[:, 0]
            diff = np.sum(diff // len(self.nGram))
            self.count += int(diff)
        return self.count

    @staticmethod
    def zero_runs(a):
        # Create an array that is 1 where a is 0, and pad each end with an extra 0.
        iszero = np.pad(np.equal(a, 0, dtype=np.bool_), 1)
        absdiff = np.abs(np.diff(iszero))
        # Runs start and end where absdiff is 1.
        ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
        return ranges
