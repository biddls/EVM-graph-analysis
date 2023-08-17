from typing import Iterator, Self, Union, Literal
import evmdasm


class Contract:
    byteCode: evmdasm.EvmInstructions | str | None = None
    address: str
    group: str
    description: str
    tags: set[str]

    def __init__(
        self,
        text: Union[list[str], set[str]],
        addr: str | list[str],
        source: Literal["ultrasound", "etherscanTags", "noTags", "forceSet"],
        byteCode: evmdasm.EvmInstructions | str | None = None,
    ) -> None:
        if not isinstance(addr, str):
            raise TypeError(f"Invalid link type\n{addr = }")

        if isinstance(byteCode, evmdasm.EvmInstructions):
            self.byteCode = byteCode

        if addr.startswith("https://etherscan.io/address/"):
            self.address: str = addr.split("https://etherscan.io/address/")[-1]
        else:
            self.address = addr

        match source:
            case "ultrasound":
                if isinstance(text, set):
                    raise TypeError(
                        f"""Invalid type for text\ntext should be a """
                        f"""{list.__name__} for case: {source}\n{text = }"""
                    )
                if len(text) == 4:
                    self.tags = {*text[:3]}
                    
                    self.tags = set(
                        filter(lambda x: x != "", self.tags)
                    )
                    
                    self.tags = set(
                        filter(lambda x: "..." not in x, self.tags)
                    )
                    
                elif len(text) == 3:
                    if "..." in text[0]:
                        self.tags = set()
                    else:
                        self.tags = {text[0]}
                else:
                    raise Exception(
                        f"""Invalid contract tag format:"""\
                        f"""\n{len(text) = } \n{text = }"""
                    )
            case "etherscanTags":
                if not isinstance(text, set):
                    raise TypeError(
                        f"""Invalid type for text\ntext should be a """\
                        f"""{set.__name__} for case: {source}\n{text = }"""
                    )
                self.tags = {*text}
            case "noTags":
                self.tags = set()
            case "forceSet":
                self.tags = {*text}
            case _:
                raise Exception(f"Invalid source: {source}")

    def addByteCode(self, byteCode: evmdasm.EvmInstructions | str) -> None:
        self.byteCode = byteCode
        
    def dissassemble(self) -> evmdasm.EvmInstructions:
        if not isinstance(self.byteCode, evmdasm.EvmInstructions):
            raise TypeError(
                f"Invalid type for byteCode\n{self.byteCode = }"
            )
        evmCode = evmdasm.EvmBytecode(self.byteCode)
        return evmCode.disassemble()

    # returns a string representation of the object
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}( {self.address = }, {self.tags = })"

    def __str__(self) -> str:
        return f"{self.address}|{self.tags}"

    # appends the tags of the other contract to this one
    def __add__(self, other: Self) -> Self:
        if not isinstance(other, Contract):
            raise TypeError(f"Invalid type for other\n{other = }")

        if self.address != other.address:
            raise Exception(
                f"Addresses don't match\n{self.address = }\n{other.address = }"
            )

        self.tags = self.tags.union(other.tags)
        return self

    # checks if the address are the same
    def __eq__(self, __value: Self) -> bool:
        return self.address == __value.address

    # returns the length of the tags
    def __len__(self) -> int:
        return len(self.tags)

    # returns the tags as an iterator
    def __iter__(self) -> Iterator[str]:
        return self.tags.__iter__()
