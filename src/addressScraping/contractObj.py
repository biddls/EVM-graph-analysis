from typing import Iterator, Self, Union, Literal, Tuple
import evmdasm


class Contract:
    byteCode: evmdasm.EvmInstructions | str = ""
    address: str
    group: str
    description: str
    tags: set[Tuple[str, str]]
    links: set[str] = set()

    def __init__(
        self,
        text: Union[list[str], set[str]],
        addr: str | list[str],
        source: Literal["ultrasound", "etherscanTags", "noTags", "forceSet"],
        byteCode: evmdasm.EvmInstructions | str | None = None,
    ) -> None:
        if not isinstance(addr, str):
            raise TypeError(f"Invalid link type\n{addr = }")

        if byteCode is not None:
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
                    self.tags = {*zip(text[:3], ["ultrasound"] * 3)}

                    self.tags = set(filter(lambda x: x[0] != "", self.tags))

                    self.tags = set(filter(lambda x: "..." not in x[0], self.tags))

                elif len(text) == 3:
                    if "..." in text[0]:
                        self.tags = set()
                    else:
                        self.tags = {(text[0], "ultrasound")}
                else:
                    raise Exception(
                        f"""Invalid contract tag format:"""
                        f"""\n{len(text) = } \n{text = }"""
                    )
            case "etherscanTags":
                if not isinstance(text, set):
                    raise TypeError(
                        f"""Invalid type for text\ntext should be a """
                        f"""{set.__name__} for case: {source}\n{text = }"""
                    )
                self.tags = {*zip(text, ["etherscanTags"] * len(text))}
            case "noTags":
                self.tags = set()
            case "forceSet":
                self.tags = {*zip(text, ["forceSet"] * len(text))}
            case _:
                raise Exception(f"Invalid source: {source}")

    def addByteCode(self, byteCode: evmdasm.EvmInstructions | str) -> None:
        if byteCode is None:
            return
        if len(byteCode) == 2:
            return
        if isinstance(byteCode, str):
            self.byteCode = byteCode

    def dissassemble(self) -> evmdasm.EvmInstructions:
        if isinstance(self.byteCode, evmdasm.EvmInstructions):
            return self.byteCode
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
    def __iter__(self) -> Iterator[Tuple[str, str]]:
        return self.tags.__iter__()

    def __hash__(self) -> int:
        return int(self.address, 16)

    def addLinks(self, links: set[str]) -> None:
        links = set(filter(lambda x: len(x) == 40, links))
        if self.links:
            self.links = self.links | links
        else:
            self.links = links

    def addLink(self, links: str) -> None:
        if len(links) != 40:
            return
        self.links.add(links)
