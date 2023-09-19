from n_grams import nGramGen
from tqdm import tqdm

# import numpy as np
# from glob import glob
# import plotly.express as px
import json
import os

# loads in data
nGramManager = nGramGen(2_000, 10_000)
nGrams = nGramManager.loadFromCache()

# sorts nGrams by heruistic and then length
nGrams = sorted(nGrams, key=len, reverse=True)
nGrams = sorted(nGrams, key=lambda nGram: nGram.heruistic(), reverse=True)

# filter out bad nGrams
# totalHeruistic = sum(map(lambda x: x.heruistic(), nGrams))
# nGrams = list(filter(lambda x: x.heruistic() > totalHeruistic / 1000, nGrams))

corpus: dict[str, list[int]] = nGramManager.labeledCont
freq = nGramManager.opCodeFreq.keys()

# take top nGrams
nGrams = nGrams[: 512 - len(freq)]

print(f"Size of corpus is: {len(corpus)}")
print(f"Number of nGrams: {len(nGrams)}")
print(f"Number of opCodes: {len(freq)}")
print(f"Depth of nGrams: {len(nGrams) + len(freq)}")


def tokenise(code: list[int]) -> tuple[list[int], int]:
    # print("Entered")
    tokens = list()
    skip = 0
    for codeIndex, opCode in enumerate(code):
        if skip > 0:
            skip -= 1
            continue
        itter = enumerate(nGrams, start=len(freq))
        for nGramPos, nGram in itter:
            if codeIndex >= len(code) - len(nGram) + 1:
                continue
            if nGram.nGramCheck(tuple(code[codeIndex : codeIndex + len(nGram)])):
                tokens.append(nGramPos)
                skip = len(nGram) - 1
                break
        # if no nGram was found
        else:
            tokens.append(opCode)

    # tokens = np.array(tokens, dtype=np.uint)
    # # print(np.max(tokens), len(freq) + len(nGrams))

    # # creating a 2D array filled with 0's
    # npCode = np.zeros((len(freq) + len(nGrams), tokens.size), dtype=np.bool_)

    # # replacing 0 with a 1 at the index of the original array
    # npCode[tokens, np.arange(tokens.size)] = True

    return tokens, len(code)


# done = list(
#     map(lambda x: x.split("/")[-1].split(".npy")[0], glob("data/tokenised/*.npy"))
# )
if os.path.exists("data/tokenised.json"):
    with open("data/tokenised.json", "r") as f:
        done: dict[str, list[int]] = json.load(f)
else:
    done: dict[str, list[int]] = dict()

corpus = {addr: code for addr, code in corpus.items() if addr not in done.keys()}
# sort corpus by value length
# corpus = dict(sorted(corpus.items(), key=lambda x: len(x[1]), reverse=True))
newSize, oldSize = 0, 0
itter = tqdm(corpus.items())
try:
    for addr, code in itter:
        tokenised, _len = tokenise(code)
        newSize += len(tokenised)
        oldSize += _len
        itter.set_description(f"Ratio:{100 * newSize / oldSize: 5.1f}%")
        done[addr] = tokenised
        # fig = px.imshow(tokenised)
        # fig.show()
        # break
except KeyboardInterrupt:
    pass
finally:
    with open("data/tokenised.json", "w") as f:
        json.dump(done, f)
