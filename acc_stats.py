import json
from utilities import *


level_cost = [0, 5, 10, 25, 50, 100, 200, 400, 600, 800, 1000, 2000, 4000, 6000, 8000, 10000, 15000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000, 120000, 150000, 200000, 250000, 100000, 150000, 200000, 250000, 350000]
level_base = {"Common": 1, "Rare": 6, "Epic": 11, "Legendary": 16, "Unique": 21, "Apex": 26, "Omega": 1}
omega_cost = [800, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 5000, 7000, 8000, 10000, 12000, 15000, 20000, 25000, 30000, 35000, 45000, 50000, 65000, 80000, 95000, 120000, 150000, 180000, 210000, 250000, 300000, 350000]


def generate_stats():
    with open("../json/players.json") as f:
        data = json.load(f)

    for player in list(data.values()):
        money = 0
        boosts = 0
        creatures_25 = 0
        for creature in player["Creatures"]:
            rarity = find_rarity(creature["id"])
            if rarity != "Omega":
                # continue
                pass
            if (creature["Level"] >= 25) and (rarity in ["Common", "Rare", "Epic", "Legendary"]):
                creatures_25 += 1
            start_level = 0
            if rarity in level_base:
                start_level = level_base[rarity]
            if rarity == "Omega":
                money += sum(omega_cost[start_level:creature["Level"]])
            else:
                money += sum(level_cost[start_level:creature["Level"]])
            boosts += sum(creature["Boosts"])
            # boosts += (creature["Boosts"][2])
            # if (creature["Level"] >= 33):
            #    print(f'{player["Name"]:<16} {creature["Name"]:<22} {creature["Level"]}')
        print(f'{player["Name"]:<16}: $:{money // 1000:>5}k Boost:{boosts:>3}')
        # print(f'{player["Name"]:<16}: $:{money // 1000:>6}k Boost:{boosts:>3} XP:{player["exp"] // 1000:>5}k')
        # print(f'{player["Name"]:<16}: 25+:{creatures_25:>3}')


def generate_omegas():
    with open("../json/creature_dict.json") as f:
        data = json.load(f)
    stats = list()
    for creature in data.values():
        if find_rarity(creature["id"]) == "Omega":
            count = len(list(filter(lambda x: x >= 26, creature["Levels"])))
            stats.append([creature['Name'], count])
    for item in sorted(stats, key=lambda x: x[1], reverse=True):
        print(f"{item[0]:<22} {item[1]}")


def generate_table():
    with open(JSON_DIR + "players.json") as f:
        players = json.load(f)
    lines = []
    for player in players.values():
        player_name = player["Name"]
        for creature in player["Creatures"]:
            id = creature["id"]
            rarity = find_rarity(id)
            name = creature["Name"]
            level = creature["Level"]
            boosts = '\t'.join([str(x) for x in creature["Boosts"]])
            lines.append(f"{player_name}\t{rarity}\t{name}\t{level}\t{boosts}\n")
    with open(JSON_DIR + "players.csv", "w") as f:
        f.writelines(lines)


generate_stats()
