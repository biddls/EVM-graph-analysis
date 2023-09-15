from matplotlib import pyplot as plt
from typing import Any


def getDiffers(conts=None, dims=3, n_clusters=100) -> list[int] | Any:
    import numpy as np
    from sklearn.decomposition import PCA
    from tqdm import tqdm
    from collections import Counter
    from sklearn.cluster import KMeans

    if conts is None:
        with open("data/opCodes.txt", "r") as f:
            conts = map(eval, tqdm(f.readlines()[:500]))
        conts = list(map(lambda x: x[1], conts))
    prog = tqdm(range(4))
    # all the data
    conts = list(filter(lambda x: len(x) != 0, conts))

    contsFlat = [item for sublist in conts for item in sublist]
    opCodeFreq = dict(Counter(contsFlat))
    prog.update(1)
    X = np.zeros((len(conts), len(opCodeFreq)))
    for i, cont in enumerate(conts):
        _len = len(cont)
        _opCodeFreq = {k: 0 for k in opCodeFreq.keys()}
        _opCodeFreq.update(dict(Counter(cont)))
        values = np.array(list(map(lambda x: _opCodeFreq[x] / _len, opCodeFreq.keys())))
        X[i] = values
    prog.update(1)

    pca = PCA(n_components=dims)
    out = pca.fit_transform(X) * 1000
    prog.update(1)

    kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init="auto")
    labels = kmeans.fit_predict(out)
    centroids = kmeans.cluster_centers_
    prog.update(1)

    u_labels = np.unique(labels)
    if len(u_labels) == 0:
        raise Exception("No labels found")
    prog.close()
    centers = list()
    for group, centroid in zip(u_labels, centroids):
        temp = out[labels == group]
        # chosen = np.where(labels == group)
        distances = np.linalg.norm(temp - centroid, axis=1)
        centers.append(np.argmax(distances).astype(int))

    if __name__ == "__main__":
        return dims, out, u_labels, labels, centroids
    else:
        return centers


if __name__ == "__main__":
    dims, out, u_labels, labels, centroids = getDiffers()
    raise Exception("Doesnt work")
    if dims > 3:
        exit()
    print("Starting Scatter Plot")
    fig = plt.figure()
    if dims == 3:
        ax = fig.add_subplot(projection="3d")
    else:
        ax = fig.add_subplot()
    for i in u_labels:
        x = out[labels == i, 0]
        y = out[labels == i, 1]
        if dims == 3:
            z = out[labels == i, 2]

            ax.scatter(x, y, z, label=i)
        else:
            ax.scatter(x, y, label=i)
    if dims == 3:
        ax.scatter(centroids[:, 0], centroids[:, 1], centroids[:, 2], s=40, c="k")  # type: ignore
    else:
        ax.scatter(centroids[:, 0], centroids[:, 1], s=40, c="k")
    plt.savefig("data/PCA.png")
