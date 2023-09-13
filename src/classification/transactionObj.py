from dataclasses import dataclass, field


@dataclass
class Transaction:
    # the parent calling contract
    _from: tuple[str, str] = field(default_factory=tuple, init=False)
    # the contract being called
    _too: tuple[str, str] = field(default_factory=tuple)
    # any addrs in the param of the call
    _params: list[tuple[str, str]] = field(default_factory=list)
    # name of the function call
    _func: str = str()

    # sets the from variable as that cant be set at init due to the recursive nature of the tree
    def setFrom(self, _from: tuple[str, str]):
        self._from = _from

    def __hash__(self) -> int:
        return hash(self._from[0] + self._too[0] + self._func)
