"""
_summary_ : 
Given a TX, it coverted it into a graph from the stack trace of the transaction
"""

from typing import Iterator
import undetected_chromedriver as uc
import bs4 as bs

from classification.transactionObj import Transaction

# from transactionObj import Transaction
from glob import glob
import os


def suppress_exception_in_del(uc):
    old_del = uc.Chrome.__del__

    def new_del(self) -> None:
        try:
            old_del(self)
        except:
            pass

    setattr(uc.Chrome, "__del__", new_del)


suppress_exception_in_del(uc)


class StackDecoder:
    def getStack(self, tx: str) -> list[Transaction]:
        if glob(f"data/STACKS/exploits/{tx}.html"):
            print("using saved file")
            with open(f"data/STACKS/exploits/{tx}.html", "r") as file:
                contents: str = file.read()
        else:
            options = uc.ChromeOptions()
            options.add_argument("--headless")  # type: ignore
            driver = uc.Chrome(
                # driver_executable_path=".\\src\\chromedriver.exe", # windows
                driver_executable_path="src/chromedriver",  # linux
                options=options,
            )
            print("scraping from web")
            driver.get(f"https://ethtx.info/mainnet/{tx}/")
            contents: str = driver.page_source
            with open(f"data/STACKS/exploits/{tx}.html", "w") as file:
                file.write(str(contents))
        soup = bs.BeautifulSoup(contents, "lxml")

        tree = soup.find(
            "ul",
            attrs={
                "class": "tree ui-fancytree-source fancytree-helper-hidden",
            },
        )

        if not isinstance(tree, bs.element.Tag):
            os.remove(f"data/STACKS/exploits/{tx}.html")
            raise TypeError(f"tree is not a bs4.element.Tag\n{tx}")
        print("generating stack")
        return list(StackDecoder.itterTree(tree))

    @staticmethod
    def itterTree(
        _tree: bs.element.Tag, _from: Transaction | None = None
    ) -> Iterator[Transaction]:
        transaction: Transaction | None = None
        for child in _tree.children:
            if isinstance(child, bs.element.Tag):
                # print(child.name)
                if child.name == "p":
                    # print("enter")
                    # get detail on transaction and yeild it
                    transaction = StackDecoder.processTransaction(child)
                    if _from is not None:
                        # print("parent")
                        transaction.setFrom(_from._too)
                    # if parent is None:
                    # print("no parent")
                    yield transaction

                # print(f"{transaction = }")
                _from = _from if transaction is None else transaction
                for elem in StackDecoder.itterTree(child, _from):
                    # print("HAI")
                    # print(elem)
                    yield elem

    @staticmethod
    def processTransaction(tag: bs.element.Tag) -> Transaction:
        # print(f"\n{tag.text = }")
        children: list[bs.element.Tag] = list(
            filter(lambda child: child.text != "\n", tag.children)
        )  # type: ignore
        _too: tuple[str, str] | None = None
        _params: list[tuple[str, str]] = list()
        _func: str = str()
        _isDelegate: bool = False
        # print(f"{len(children)}")
        for i, child in enumerate(children):
            try:
                style = child.get("style")
                if isinstance(style, str):
                    style = style.split(": ")[1]
                    # skip if its the gas amount
                    if style == "slategray":
                        continue
                    # process func call
                    elif style == "darkgreen":
                        # todo: processing for parameters
                        if _func is str():
                            _func = f"{child.text[1:]}()"
                            # print(f"\t{i}FUNC_|{_func}")
                        else:
                            raise AssertionError("Only 1 fun is allowed")
                        continue
                    elif style == "darkorange":
                        if not _isDelegate:
                            _isDelegate = True
                            # print(f"\t{i}DELEG|{child = }")
                            continue

                elif isinstance(style, list):
                    raise TypeError(f"style is a list\n\t{style = }")
                elif style is not None:
                    raise TypeError(f"style is not a str or None\n\t{style = }")
            except AttributeError:
                # print(f"\t{i}ATTRE|{child = }")
                continue

            # check for link
            if child.name == "a":
                href = child.get("href")
                if not isinstance(href, str):
                    raise TypeError(f"is supposed to be a str\n\t{href = }")
                href = href.split("https://etherscan.io/address/")[-1]
                text = child.text
                if href in text:
                    text = href
                if _too is None:
                    _too = (href, text)
                else:
                    _params.append((href, text))
                # print(f"\t{i}LINK_|{text}|{href}")
                continue
            else:
                links = child.find_all("a")
                for link in links:
                    href = link.get("href")
                    if not isinstance(href, str):
                        raise TypeError(f"is supposed to be a str\n\t{href = }")
                    href = href.split("https://etherscan.io/address/")[-1]
                    text = link.text
                    if href in text:
                        text = href
                    if _isDelegate:
                        _too = (href, text)
                        _isDelegate = False
                    else:
                        _params.append((href, text))
                    # print(f"\t{i}S_LNK|{text}|{href}")

                if len(links) == 0:
                    ...
                    # print(f"\t{i}NONE_|{child = }")
                continue

        if _too is None:
            raise AssertionError("from cannot be None")
        # print(f"{_from = }\n{_func = }\n{_too = }")
        return Transaction(_too, _params, _func)


if __name__ == "__main__":
    tx = "0x9d093325272701d63fdafb0af2d89c7e23eaf18be1a51c580d9bce89987a2dc1"
    stack = StackDecoder().getStack(tx)

    for i, transaction in enumerate(stack):
        print(f"{i = }")
        print(transaction)
