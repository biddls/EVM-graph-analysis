from dataOps import ByteCodeIO
from collections import Counter
import json
import os

raise Exception("This script is not finished")

with ByteCodeIO() as db:
    tags = db.getColumn("addressTags", "tag")
tags = Counter(tags)
tags = dict(sorted(tags.items(), key=lambda x: x[1]))
tags = {k[0]: v for k, v in tags.items() if v > 2}
print(json.dumps(tags, indent=4))
print(f"{sum(tags.values())} tags counted")
if os.path.exists("data/labels.json"):
    with open("data/labels.json", "r") as f:
        temp = json.loads(f.read())

groups = {k: [k] for k in tags.keys()}
groups: dict[str, list[str]] = dict()

for k in reversed(tags.keys()):
    print(groups.keys())
    _groups = input(f"What group does '{k}' belong to? ").split(", ")
    for group in _groups:
        if group == "":
            group = "other"
        if group not in groups.keys():
            groups[group] = list()
        groups[group].append(k)

        with open("data/labels.json", "w") as f:
            f.write(json.dumps(groups, indent=4))
