from dataclasses import dataclass, field
from functools import total_ordering
from typing import List, Tuple, Self

# defines the nGramObj class
@total_ordering
@dataclass
class nGramObj:
    nGram: Tuple[int, ...]
    dataLength: int
    parentNgram: Self | None = field(default=None, init=True)
    count: int = field(default=0, init=False)

    def __hash__(self) -> int:
        return hash(self.nGram)
    
    def __eq__(self, __value: Self) -> bool:
        if not (self.nGram == __value.nGram):
            raise ValueError("nGrams must be the same to be compared")
        return self.count == __value.count
    
    def __lt__(self, __value: Self) -> bool:
        if not (self.nGram == __value.nGram):
            raise ValueError("nGrams must be the same to be compared")
        return self.count < __value.count
    
    def __len__(self) -> int:
        return len(self.nGram)
    
    def __add__(self, __value: Self) -> Self:
        if self != __value:
            raise ValueError("nGrams must be the same to be added")
        self.count += __value.count
        return nGramObj(self.nGram, self.count + __value.count, self.parentNgram)
    
    def __iadd__(self, __value: Self) -> Self:
        if self != __value:
            raise ValueError("nGrams must be the same to be added")
        self.count += __value.count
        return self
    
    def __int__(self) -> int:
        return self.count
    
    def __float__(self) -> float:
        return float(self.count)
    
    def __bool__(self) -> bool:
        return bool(self.count)
    
    def getPath(self) -> List[Tuple[int, ...]]:
        if self.parentNgram is None:
            return [self.nGram]
        return [*self.parentNgram.getPath(), self.nGram]