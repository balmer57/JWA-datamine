from utilities import *

with open(JSON_DIR + "players.json") as f:
    data = json.load(f)

data = list(data.values())


def print_creatures(alliance):
    for player in alliance:
        name = player["Name"]
        for creature in player["Creatures"]:
            c_name = creature["Name"]
            level = str(creature["Level"])
            boosts = [str(x) for x in creature["Boosts"]]
            rarity = find_rarity(creature["id"])
            print(f'{name}\t{c_name}\t{rarity}\t{level}\t{boosts[0]}\t{boosts[1]}\t{boosts[2]}')


print_creatures(data)
