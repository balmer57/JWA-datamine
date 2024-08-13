from utilities import *
import os

moves_dict = {"Common": {2: [], 3: [], 4: [], 5: [], 6: [], 7: []},
              "Rare": {2: [], 3: [], 4: [], 5: [], 6: [], 7: []},
              "Epic": {2: [], 3: [], 4: [], 5: [], 6: [], 7: []},
              "Legendary": {2: [], 3: [], 4: [], 5: [], 6: [], 7: []},
              "Unique": {2: [], 3: [], 4: [], 5: [], 6: [], 7: []},
              "Apex": {2: [], 3: [], 4: [], 5: [], 6: [], 7: []},
              "Omega": {2: [], 3: [], 4: [], 5: [], 6: [], 7: []}}

for path, _, files in os.walk(DATA_DIR + "CreaturesStaticData"):
    for file in files:
        with open(path + "/" + file) as f:
            data = json.load(f)
            if data["el"]:
                attacks = len(data["rl"][0]["al"])
                if data["rl"][0]["sia"]:
                    attacks += 1
                if data["rl"][0]["ac"]:
                    attacks += 1
                if data["rl"][0]["aooe"]:
                    attacks += 1
                rarity = guid_map[data["r"]["guid"]]
                rarity = os.path.split(rarity)[1][1:-5]
                name = localization[data["lkn"]]
                moves_dict[rarity][attacks].append(name)

for rarity in moves_dict.keys():
    s = f"{rarity:<9}: "
    moves_count = moves_dict[rarity]
    for count in moves_count.keys():
        if len(moves_count[count]) > 0:
            s += f"{count}: {len(moves_count[count]):<2}  "
    print(s)

print('\n')

for rarity in moves_dict.keys():
    s = f"{rarity:<9}: "
    moves_count = moves_dict[rarity]
    for count in moves_count.keys():
        if 10 > len(moves_count[count]) > 0:
            s += f"{count}: {' '.join(moves_count[count])}  "
    print(s)

print('\n')

for rarity in moves_dict.keys():
    s = f"{rarity:<9}\t"
    moves_count = moves_dict[rarity]
    for count in moves_count.keys():
        s += f"{len(moves_count[count]):<2}\t"
    print(s)

