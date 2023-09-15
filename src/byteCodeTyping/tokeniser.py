from n_grams import nGramGen, nGramObj
from tqdm import tqdm
import numpy as np
from glob import glob

# loads in data
nGramManager = nGramGen(2000, 10000)
nGrams = nGramManager.loadFromCache()
nGrams = sorted(nGrams, key=lambda nGram: nGram.heruistic(), reverse=True)

corpus: dict[str, list[int]] = nGramManager.labeledCont
freq = nGramManager.opCodeFreq.keys()
print(f"Size of corpus is: {len(corpus)}")
print(f"Number of nGrams: {len(nGrams)}")
print(f"Number of opCodes: {len(freq)}")


def tokenise(nGrams: list[nGramObj], code: list[int]) -> np.ndarray:
    # creates output array
    npCode = np.zeros((len(code), len(freq) + len(nGrams)), dtype=np.bool_)
    for nGram in nGrams:
        nGramSize = len(nGram)
        for i in range(len(code) - nGramSize):
            if nGram.nGramCheck(tuple(code[i : i + nGramSize])):
                npCode[i : i + nGramSize, len(freq) + nGrams.index(nGram)] = True
    return npCode


done = list(
    map(lambda x: x.split("/")[-1].split(".npy")[0], glob("data/tokenised/*.npy"))
)
corpus = {addr: code for addr, code in corpus.items() if addr not in done}
for addr, code in tqdm(corpus.items(), position=0, leave=True):
    tokenised = tokenise(nGrams, code)
    np.save(f"data/tokenised/{addr}.npy", tokenised)
