import numpy as np
import json
import os
from typing import Final
from tqdm import tqdm

DEPTH: Final[int] = 512

if os.path.exists("data/tokenised.json"):
    with open("data/tokenised.json", "r") as f:
        done: dict[str, list[int]] = json.load(f)
else:
    raise FileNotFoundError("data/tokenised.json not found")


def convertTo_npArr(item: tuple[str, list[int]]) -> tuple[str, np.ndarray]:
    tokens = np.array(item[1], dtype=np.uint)
    # print(np.max(tokens), len(freq) + len(nGrams))

    # creating a 2D array filled with 0's
    npCode = np.zeros((DEPTH, tokens.size), dtype=np.bool_)

    # replacing 0 with a 1 at the index of the original array
    npCode[tokens, np.arange(tokens.size)] = True
    return item[0], npCode


loaded = dict(
    map(
        convertTo_npArr,
        tqdm(done.items(), desc="converting to np array"),
    )
)

# load in the labels
if os.path.exists("data/labels.json"):
    with open("data/labels.json", "r") as f:
        labels: dict[str, int] = json.load(f)
else:
    raise FileNotFoundError("data/labels.json not found")

print(json.dumps(labels, indent=4))
