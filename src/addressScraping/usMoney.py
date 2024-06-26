"""
This function scrapes the data from the labelcloud page of etherscan.io
"""

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import bs4
from selenium.webdriver.chrome.options import Options
from addressScraping.contractObj import Contract


class usMoneyScraper:
    @staticmethod
    def getAddresses() -> list[Contract]:
        """
        This function gets the addresses from ultrasound.money
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(options=chrome_options)
        url = "https://ultrasound.money/"
        contents = driver.get(url)

        sleep(3)

        buttons = driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            if button.text == "5m":
                button.click()
                break
        else:
            # if "break" is not executed
            raise Exception("Button not found")

        sleep(3)

        contents = driver.page_source
        driver.close()
        soup = BeautifulSoup(contents, "lxml")
        soup_links: bs4.element.ResultSet = soup.find_all("a", href=True)

        filteredLinks: set[bs4.element.Tag] = set(
            filter(
                lambda x: x["href"].startswith("https://etherscan.io/address/"),
                soup_links,
            )
        )

        # processed_links: set = set(map(lambda x: x["href"], filteredLinks))

        # addrs: set[str | list[str]] = {
        #     link.split("https://etherscan.io/address/")[-1] for link in processed_links
        # }

        conts: list[Contract] = []

        for link in filteredLinks:
            text = [content.text for content in link.contents]
            # print(f"{text = }")
            # print(f"{link['href'] = }")
            conts.append(Contract(text, link["href"], "ultrasound"))

        return conts


if __name__ == "__main__":
    print("This is a module, not a script")
    conts = usMoneyScraper.getAddresses()
    print(len(conts))
    for cont in conts[:5]:
        print(cont)

    print(f"{conts[0] == conts[1] = }")
    print(f"{conts[0] == conts[0] = }")
    l = 0
    while l == 0:
        l = len(conts[0])

    print(f"{conts[l] + conts[l] = }")
    print(len(conts[l]))
