import os
import json
import glob

BASE_DIR = "D:/Dino/flows/"
OUT_FILE = "D:/Dino/json/player_guilds.json"
# players = dict()

with open(OUT_FILE) as f:
    players = json.load(f)

files = list(filter(os.path.isfile, glob.glob(BASE_DIR + "*")))
files.sort(key=lambda x: os.path.getmtime(x))
for file in files:
    if "cachedAccountGamerIds" in file:
        try:
            with open(file) as f:
                data = json.load(f)
                for player in data["data"]["collectionData"]:
                    player_id = int(player["collectionWebResourceId"])
                    player_name = player["validatedGamerId"]
                    players[player_id] = dict()
                    players[player_id]["id"] = player_id
                    players[player_id]["name"] = player_name.split("#")[0]
                    players[player_id]["tag"] = player_name.split("#")[1]
                    players[player_id]["guild"] = ""
        except:
            pass
for file in files:
    if "guildProfile" in file:
        try:
            with open(file) as f:
                data = json.load(f)
                for player_id in data["data"]["membersAccountIds"]:
                    if player_id in players.keys():
                        players[player_id]["guild"] = data["data"]["guildAlias"]
        except:
            pass

with open(OUT_FILE, "w") as g:
    json.dump(players, g, indent=2)
