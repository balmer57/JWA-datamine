from utilities import *
import glob

moves = dict()
for file in list(filter(os.path.isfile, glob.glob(DATA_DIR + "CreaturesStaticData/*"))):
    with open(file) as f:
        data = json.load(f)
        rounds = data["rl"]
        creature_name = localization[data["lkn"]] if data["lkn"] in localization.keys() else data["lkn"]
        for moveset in rounds:
            for move in moveset["al"]:# + [moveset["sia"]] + [moveset["ac"]]:
                if isinstance(move, dict):
                    move_guid = move["ai"]["guid"]
                    move_duration = move["at"]
                    move_name = find_name(move_guid)
                    if 1501 > move_duration > 0:
                    # if move_duration > 6999:
                        if move_guid in moves.keys():
                            moves[move_guid]["creatures"].append({"name": creature_name, "time": move_duration})
                        else:
                            moves[move_guid] = {"name": move_name, "creatures": [{"name": creature_name, "time": move_duration}]}

for move in moves.keys():
    moves[move]["creatures"] = sorted(moves[move]["creatures"], key=lambda x: x["time"], reverse=False)
moves_list = sorted(moves.values(), key=lambda x: x["creatures"][0]["time"], reverse=False)
for move in moves_list:
    print(move["name"])
    for instance in move["creatures"]:
        print("  {:20} {}".format(instance["name"], instance["time"]))
