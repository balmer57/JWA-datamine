from utilities import *

boosted = list()
with open(BASE_DIR + "decoded_streams/GetCreatureList.json") as f:
    data = json.load(f)
    cl = data[1]["p"]["p"]["cl"]
    for creature in cl:
        if creature["caeps"]:
            name = find_name(creature["cid"].split()[0])
            boosted.append([name, creature["caeps"]])

boosted.sort(key=lambda x: sum(x[1].values()), reverse=True)
for creature in boosted:
    name = creature[0]
    a = creature[1]["aepa"] // 100 if "aepa" in creature[1].keys() else 0
    h = creature[1]["aeph"] // 100 if "aeph" in creature[1].keys() else 0
    s = creature[1]["aeps"] // 100 if "aeps" in creature[1].keys() else 0
    print(f"{name:<20}: Att: {a:>2}  HP: {h:>2}  Spd: {s:>2}")
