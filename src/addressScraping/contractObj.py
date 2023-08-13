from typing import Iterator, Self
import evmdasm


class Contract:
    byteCode: evmdasm.EvmInstructions
    address: str
    name: str
    group: str
    description: str
    tags: set[str]

    def __init__(
        self,
        text: list[str],
        link: str | list[str],
        byteCode: evmdasm.EvmInstructions | None = None,
    ) -> None:
        if not isinstance(link, str):
            raise TypeError(f"Invalid link type\n{link = }")

        if isinstance(byteCode, evmdasm.EvmInstructions):
            self.byteCode = byteCode

        self.address: str = link.split("https://etherscan.io/address/")[-1]
        # print(f"{text = }")
        if len(text) == 4:
            # process it with typing
            self.name = text[0]
            self.group = text[1]
            self.description = text[2]
            self.tags = {*text[:3]}
            self.tags = set(filter(lambda x: x != "", self.tags))
            self.tags = set(filter(lambda x: "..." not in x, self.tags))
        elif len(text) == 3:
            # process it without typing
            self.name = text[0]

            if "..." in self.name:
                self.tags = set()
            else:
                self.tags = {self.name}
        else:
            raise Exception(f"Invalid contract tag format:\n{len(text) = } \n{text = }")

    def addByteCode(self, byteCode: evmdasm.EvmInstructions) -> None:
        self.byteCode = byteCode

    # returns a string representation of the object
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.tags = }, {self.address = })"

    def __str__(self) -> str:
        tagsExName = self.tags.difference({self.name})
        if len(tagsExName) == 0:
            return f"{self.address}|{self.name}"
        return f"{self.address}|{self.name}|{tagsExName}"

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