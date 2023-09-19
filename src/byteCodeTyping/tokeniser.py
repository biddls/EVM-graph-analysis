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

# sorts nGrams by heruistic and then length
nGrams = sorted(nGrams, key=lambda nGram: nGram.heruistic(), reverse=True)
nGrams = sorted(nGrams, key=len, reverse=True)

corpus: dict[str, list[int]] = nGramManager.labeledCont
freq = nGramManager.opCodeFreq.keys()
print(f"Size of corpus is: {len(corpus)}")
print(f"Number of nGrams: {len(nGrams)}")
print(f"Number of opCodes: {len(freq)}")


def tokenise(nGrams: list[nGramObj], code: list[int]) -> tuple[np.ndarray, int]:
    # creates output array
    npCode = np.zeros((len(freq) + len(nGrams), len(code)), dtype=np.bool_)
    for nGramPos, nGram in enumerate(nGrams):
        # for each ngram
        nGramSize = len(nGram)
        # itterates over every opCode in the code with padding
        i = 0
        for i, _ in enumerate(code):
            if i == len(code) - 2:
                continue
            print(f"{i = }", end="\r")
            # for all indicies in the code while taking to account the nGram size
            if nGram.nGramCheck(tuple(code[i : i + nGramSize])):
                # if the nGram matches the code
                npCode[nGramPos + len(freq), i] = True
                npCode[nGramPos + len(freq), i + 1 : i + nGramSize] = np.nan
                # breaks on the first (and best nGRam)
                break
                # npCode[i : i + nGramSize, len(freq) + nGrams.index(nGram)] = True
        # if no nGram is found (no break) then it is a single opCode
        else:
            npCode[code[i], i] = True
    # removes all the columns in npCode that are all nan
    npCode = npCode[:, ~np.all(np.isnan(npCode), axis=0)]
    return npCode, len(code)


done = list(
    map(lambda x: x.split("/")[-1].split(".npy")[0], glob("data/tokenised/*.npy"))
)
corpus = {addr: code for addr, code in corpus.items() if addr not in done}

newSize, oldSize = 0, 0
for addr, code in tqdm(corpus.items(), position=0, leave=True):
    tokenised, _len = tokenise(nGrams, code)
    newSize += tokenised.shape[1]
    oldSize += _len
    # np.save(f"data/tokenised/{addr}.npy", tokenised)
    # print(tokenised)
    # print(tokenised.shape)
    # df = pd.DataFrame(tokenised)
    # df.to_csv("data/tokenised.csv", index=False, header=False)

    fig = px.imshow(tokenised)
    fig.show()
    break
print(f"New size: {newSize}")
print(f"Old size: {oldSize}")
print(f"Compression: {newSize / oldSize}")
