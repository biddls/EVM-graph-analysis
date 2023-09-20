from dataOps import ByteCodeIO
from collections import Counter
import json
import os

# raise Exception("This script is not finished")

# loads in all the tags captured
with ByteCodeIO() as db:
    tags = db.getColumn("addressTags", "tag")
tags = Counter(tags)
tags = dict(sorted(tags.items(), key=lambda x: x[1]))
# filters them to only the important ones
tags = {k[0]: v for k, v in tags.items() if v > 2}
print(json.dumps(tags, indent=4))
print(f"{sum(tags.values())} tags counted")
# loads already processed tags
if os.path.exists("data/labels.json"):
    with open("data/labels.json", "r") as f:
        # grouped labels
        groups = json.loads(f.read())
    # filter out from tags already processes ones
    processed = list(groups.values())
    processed = [item for sublist in processed for item in sublist]
    # print(processed)
    tags = {k: v for k, v in tags.items() if k not in processed}
else:
    groups = dict()

print(groups)
# groups: dict[str, list[str]] = dict()
# exit(0)
for k in reversed(tags.keys()):
    k = str(k)
    print(list(groups.keys()))
    _groups = input(f"What group does '{k}' belong to? ")
    _groups = _groups.split(",")
    for group in _groups:
        if group == "":
            group = "other"
        if group not in groups.keys():
            groups[group] = list()
        groups[group].append(k)

        with open("data/labels.json", "w") as f:
            f.write(json.dumps(groups, indent=4))
