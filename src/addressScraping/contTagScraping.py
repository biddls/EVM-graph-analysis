"""
This function scrapes the data from the labelcloud page of etherscan.io
"""
import bs4 as bs
import undetected_chromedriver as uc
import time
from addressScraping.contractObj import Contract


def suppress_exception_in_del(uc):
    old_del = uc.Chrome.__del__

    def new_del(self) -> None:
        try:
            old_del(self)
        except:
            pass

    setattr(uc.Chrome, "__del__", new_del)


suppress_exception_in_del(uc)


class TagGetter:
    def __init__(self):
        # uc.Chrome(driver_executable_path=ChromeDriverManager().install(), options=options)
        options = uc.ChromeOptions()
        options.add_argument("--headless")  # type: ignore
        self.driver = uc.Chrome(
            driver_executable_path=".\\src\\chromedriver.exe", options=options
        )

    def getTags(
        self, addr: str, site: str = "etherscan", maxDuration: float = 5
    ) -> Contract:
        if not addr.startswith("0x"):
            raise Exception(f"Invalid address format:\n{addr = }")
        if len(addr) != 42:
            raise Exception(f"Invalid address length should be 42:\n{addr = }")

        match site:
            case "etherscan":
                address = self.etherScanGetter(addr, maxDuration, "address")
                token = self.etherScanGetter(addr, maxDuration, "token")
                return address + token
            case _:
                raise Exception(f"Invalid site:\n{site = }")

    def etherScanGetter(
        self, addr: str, maxDuration: float, addrToken: str
    ) -> Contract:
        self.driver.get(f"https://etherscan.io/{addrToken}/{addr}")
        start: float = time.time()
        while True:
            contents: str = self.driver.page_source

            soup = bs.BeautifulSoup(contents, "lxml")

            # find elemet div with class d-flex flex-wrap align-items-center gap-1
            div: bs.element.Tag | bs.element.NavigableString | None = soup.find(
                "div", {"class": "d-flex flex-wrap align-items-center gap-1"}
            )

            if div is None:
                if time.time() - start > maxDuration:
                    return Contract(set(), addr, "noTags")
                continue
            elif not isinstance(div, bs.element.Tag):
                raise Exception(f"Invalid div type:\n{type(div) = }")

            spans: bs.ResultSet = div.find_all("span")
            tags: set[str] = {span.text for span in spans}

            if len(tags) > 0:
                cont = Contract(tags, addr, "etherscanTags")
                return cont

            if time.time() - start > maxDuration:
                return Contract(set(), addr, "noTags")


if __name__ == "__main__":
    print("This is a module, not a script")
    # 0x protocol
    tagGetter = TagGetter()
    start = time.time()
    tags = tagGetter.getTags("0xdef1c0ded9bec7f1a1670819833240f027b25eff")
    end = time.time()
    print(f"Scrape time: {end - start:.2f}s")
    print(tags)
