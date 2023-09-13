from dataOps import ByteCodeIO
from collections import Counter
import json

with ByteCodeIO() as db:
    tags = db.getColumn("addressTags", "tag")

tags = Counter(tags)
tags = dict(sorted(tags.items(), key=lambda x: x[1]))
tags = {k[0]: v for k, v in tags.items() if v > 2}
print(json.dumps(tags, indent=4))
print(f"{sum(tags.values())} tags counted")
