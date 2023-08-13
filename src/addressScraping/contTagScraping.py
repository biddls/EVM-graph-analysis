"""
This function scrapes the data from the labelcloud page of etherscan.io
"""

from bs4 import BeautifulSoup as bs
import undetected_chromedriver as uc
from time import sleep


def getTags(addr: str) -> set[str]:
    if not addr.startswith("0x"):
        raise Exception(f"Invalid address format:\n{addr = }")
    if len(addr) != 42:
        raise Exception(f"Invalid address length should be 42:\n{addr = }")

    ## Get tags from the tokens page
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    driver = uc.Chrome(use_subprocess=True, options=options)
    driver.get(f"https://etherscan.io/address/{addr}")
    sleep(5)
    contents = driver.page_source
    driver.close()
    soup = bs(contents, "lxml")


if __name__ == "__main__":
    print("This is a module, not a script")
    # 0x protocol
    tags = getTags("0xdef1c0ded9bec7f1a1670819833240f027b25eff")
