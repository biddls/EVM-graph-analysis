from n_grams import nGramGen, nGramObj
from tqdm import tqdm
import numpy as np
from glob import glob
import pandas as pd
import plotly.express as px

# exit(0)
# loads in data
nGramManager = nGramGen(2000, 10000)
nGrams = nGramManager.loadFromCache()

nGrams = sorted(nGrams, key=lambda nGram: nGram.heruistic(), reverse=True)
nGrams = sorted(nGrams, key=len, reverse=True)

corpus: dict[str, list[int]] = nGramManager.labeledCont
freq = nGramManager.opCodeFreq.keys()
print(f"Size of corpus is: {len(corpus)}")
print(f"Number of nGrams: {len(nGrams)}")
print(f"Number of opCodes: {len(freq)}")


def tokenise(nGrams: list[nGramObj], code: list[int]) -> np.ndarray:
    # creates output array
    npCode = np.zeros((len(code), len(freq) + len(nGrams)), dtype=np.bool_)
    for nGram in nGrams:
        # for each ngram
        nGramSize = len(nGram)
        for i in range(len(code) - nGramSize):
            # for all indicies in the code while taking to account the nGram size
            if nGram.nGramCheck(tuple(code[i : i + nGramSize])):
                npCode[i : i + nGramSize, len(freq) + nGrams.index(nGram)] = True
            else:
                npCode[i, code[i]] = True
    return npCode


done = list(
    map(lambda x: x.split("/")[-1].split(".npy")[0], glob("data/tokenised/*.npy"))
)
corpus = {addr: code for addr, code in corpus.items() if addr not in done}


for addr, code in tqdm(corpus.items(), position=0, leave=True):
    tokenised = tokenise(nGrams, code)
    # np.save(f"data/tokenised/{addr}.npy", tokenised)
    # print(tokenised)
    # print(tokenised.shape)
    # df = pd.DataFrame(tokenised)
    # df.to_csv("data/tokenised.csv", index=False, header=False)

    fig = px.imshow(tokenised.T)
    fig.show()
    break
