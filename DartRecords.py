import re

from utilities import *

records = list()
rarities = set()

with open(BASE_DIR + "/decoded_streams/CreatureDex.json") as f:
    messages = json.load(f)
    for message in messages:
        if message["p"]["c"] == "j.cgdhs":
            if "hsm" in message["p"]["p"].keys():
                data = message["p"]["p"]["hsm"]
                for guid in data.keys():
                    record = int(re.findall("^\\d+", data[guid])[0])
                    dino = get_json_from_guid(guid)
                    dino_name = localization[dino["lkn"]]
                    rarity_guid = dino["r"]["guid"]
                    rarity = get_json_from_guid(rarity_guid)
                    rarity_name = rarity["devName"]
                    rarities.add(rarity_name)
                    records.append({"name": dino_name, "rarity": rarity_name, "record": record})

for rarity in rarities:
    print(rarity)
    selection = sorted(filter(lambda x: x["rarity"] == rarity, records), key=lambda x: x["record"], reverse=True)
    for dino in selection:
        print(f"{dino['name']}\t{dino['record']}")
    print("")
