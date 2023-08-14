from bs4 import BeautifulSoup


## Get the links from the labelcloud page
with open("./src/addressScraping/data/Label Word Cloud Etherscan.html", "r") as f:
    contents = f.read()

soup = BeautifulSoup(contents, "lxml")
mydivs = soup.findAll("div", {"class": "col-md-4 col-lg-3 mb-3 secondary-container"})
soup = BeautifulSoup(str(mydivs), "lxml")
links = [link["href"] for link in soup.findAll("a", href=True)]

links = [
    link for link in links if not link.startswith("https://etherscan.io/txs/label/")
]
print(links[0])
print(len(links))
