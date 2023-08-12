"""
This function scrapes the data from the labelcloud page of etherscan.io
"""

from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import time

# with open("./src/addressScraping/data/Label Word Cloud Etherscan.html", "r") as f:
#     contents = f.read()

# soup = BeautifulSoup(contents, "lxml")
# mydivs = soup.findAll("div", {"class": "col-md-4 col-lg-3 mb-3 secondary-container"})
# soup = BeautifulSoup(str(mydivs), "lxml")
# links = [link["href"] for link in soup.findAll("a", href=True)]

# links = [
#     link for link in links if not link.startswith("https://etherscan.io/txs/label/")
# ]
# print(links[0])
# print(len(links))


# options = uc.ChromeOptions()
# options.add_argument("--headless")
# driver = uc.Chrome(use_subprocess=True, options=options)
# driver.get("https://etherscan.io/address/0xdef1c0ded9bec7f1a1670819833240f027b25eff")
# time.sleep(5)
# contents = driver.page_source
# driver.close()
# soup = BeautifulSoup(contents, "lxml")
