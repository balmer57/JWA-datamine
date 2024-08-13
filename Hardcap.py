from utilities import *

limit_dict = dict()
level_map = dict()
dna_map = [100, 150, 200, 250, 300, 350, 400, 500, 750, 1000, 1250, 1500, 2000, 2500, 3000, 3500, 4000, 5000, 7500, 10000, 12500, 15000, 20000, 25000, 30000, 35000, 40000, 50000, 75000]
coin_map = [5, 10, 25, 50, 100, 200, 400, 600, 800, 1000, 2000, 4000, 6000, 8000, 10000, 15000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 120000, 150000, 200000, 250000]
rarity_shift = {"Common": 1, "Rare": 6, "Epic": 11, "Legendary": 16}
rarity_amount = {"Common": 1, "Rare": 4, "Epic": 15, "Legendary": 50}

with open(BASE_DIR + "/decoded_streams/GetCreatureList.json") as f:
    messages = json.load(f)
    for message in messages:
        if message["p"]["c"] == "j.clcgl":
            if "cl" in message["p"]["p"].keys():
                data = message["p"]["p"]["cl"]
                for item in data:
                    guid = item["cid"].split()[0]
                    level = item["level"]
                    level_map[guid] = level

for cur_dir, dirs, files in os.walk(DATA_DIR + "/Resource/Dna"):
    for file in files:
        with open(cur_dir + "/" + file) as f:
            dna_json = json.load(f)
            if dna_json["$type"].startswith("CrDNARe"):
                if dna_json["l"]:
                    limit = dna_json["l"]["vis"]
                    hard_limit = dna_json["l"]["inv"]
                    guid = dna_json["cr"]["guid"]
                    name = find_name(guid)
                    rarity = find_rarity(guid)
                    id = dna_json["TypeId"]
                    level = level_map[guid] if guid in level_map.keys() else 0
                    dna_25 = 0
                    coeff = 0
                    coins = 0
                    if rarity in rarity_shift.keys():
                        shift = rarity_shift[rarity]
                        dna_25 = sum(dna_map[level - shift:25 - shift])
                        coins = sum(coin_map[level - 1:25 - 1])
                        coeff = rarity_amount[rarity]
                    limit_dict[id] = {"id": id, "guid": guid, "rarity": rarity, "name": name, "limits": [limit, hard_limit], "dna": 0, "level": level, "dna_25": dna_25, "coeff": coeff, "coins": coins}

with open(BASE_DIR + "/decoded_streams/GetResources.json") as f:
    messages = json.load(f)
    for message in messages:
        if message["p"]["c"] == "j.crg":
            if "res" in message["p"]["p"].keys():
                data = message["p"]["p"]["res"]
                for item in data:
                    if item["t"] in limit_dict.keys():
                        limit_dict[item["t"]]["dna"] = item["a"]

dna = sorted(limit_dict.values(), key=lambda x: x["dna"]/x["limits"][1], reverse=True)
for item in dna:
    if item["dna"] > 0:
        print("\t".join(map(str, [item["rarity"], item["name"], item["dna"], item["limits"][1], item["level"], (item["dna"] - item["dna_25"])*item["coeff"]/75000, item["coins"]])))
