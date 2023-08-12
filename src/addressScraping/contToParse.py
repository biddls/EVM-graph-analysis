class Contract:
    def __init__(self, text: list[str], link: str | list[str]) -> None:
        if not isinstance(link, str):
            raise TypeError(f"Invalid link type\n{link = }")

        self.link: str = link.split("https://etherscan.io/address/")[-1]

        if len(text) == 4:
            # process it with typing
            self.name = text[0]
            self.group = text[1]
            self.description = text[2]
            pass
        elif len(text) == 3:
            # process it without typing
            self.name = text[0]
            pass
        else:
            raise Exception(f"Invalid contract format\n{text = } \n{len(text) = }")
