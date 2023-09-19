from n_grams import nGramGen, nGramObj
from tqdm import tqdm
import numpy as np
from glob import glob
import pandas as pd
import plotly.express as px

# exit(0)
# loads in data
nGramManager = nGramGen(2000, 10000, rowsToReadIn=100_000)
nGrams = nGramManager.loadFromCache()

# sorts nGrams by heruistic and then length
nGrams = sorted(nGrams, key=len, reverse=True)
nGrams = sorted(nGrams, key=lambda nGram: nGram.heruistic(), reverse=True)

# filter out bad nGrams
totalHeruistic = sum(map(lambda x: x.heruistic(), nGrams))
nGrams = list(filter(lambda x: x.heruistic() > totalHeruistic / 1000, nGrams))

corpus: dict[str, list[int]] = nGramManager.labeledCont
freq = nGramManager.opCodeFreq.keys()
print(f"Size of corpus is: {len(corpus)}")
print(f"Number of nGrams: {len(nGrams)}")
print(f"Number of opCodes: {len(freq)}")


def tokenise(
    nGrams: list[nGramObj], code: list[int], testing=False
) -> tuple[np.ndarray, int]:
    # creates output array
    npCode = np.zeros((len(freq) + len(nGrams), len(code)), dtype=np.uint8)
    if testing:
        itter = tqdm(enumerate(nGrams), position=1, leave=False, total=len(nGrams))
    else:
        itter = enumerate(nGrams)
    for nGramPos, nGram in itter:
        # for each ngram
        nGramSize = len(nGram)
        # itterates over every opCode in the code with padding
        i = 0
        for i, _ in enumerate(code):
            if i >= len(code) - nGramSize + 1:
                continue
            # for all indicies in the code while taking to account the nGram size
            if nGram.nGramCheck(tuple(code[i : i + nGramSize])):
                # if the nGram matches the code
                npCode[nGramPos + len(freq), i] = 2
                # npCode = np.delete(npCode, np.s_[i + 1 : i + nGramSize], axis=1)
                npCode[nGramPos + len(freq), i + 1 : i + nGramSize] = 1
                # breaks on the first (and best nGRam)
                # break
            # if no nGram is found (no break) then it is a single opCode
            # else:
            # print(code[i], i)
            npCode[code[i], i] = 2
        # print(i, len(code))
    # removes all the columns in npCode that are 1
    if testing:
        print(f"\n{npCode.shape = }")
    # npCode = npCode[:, ~np.all(npCode == 1, axis=0)]

    colsToDrop = np.unique(np.where(npCode == 1)[1])
    if testing:
        print(f"{colsToDrop = }")
        print(f"{colsToDrop.shape = }")
    # npCode = npCode[:, np.where(npCode == 1)[1]]
    npCode = np.delete(npCode, colsToDrop, axis=1)
    if testing:
        print(f"{npCode.shape = }")
    # npCode = npCode == 1
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

    # fig = px.imshow(tokenised)
    # fig.show()
    # break
print(f"New size: {newSize}")
print(f"Old size: {oldSize}")
print(f"Compression: {newSize / oldSize}")
