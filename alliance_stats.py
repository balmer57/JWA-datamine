from unpcap import *
import json
from utilities import *

# strings, strings_decoded = extract_pcap(BASE_DIR + 'PCAPdroid_06_мар._18_04_50.pcap')

with open(JSON_DIR + "pcap_out.json") as f:
    strings = json.load(f)
    strings_decoded = json.loads(json.dumps(strings), object_pairs_hook=guid_hook)

with open(JSON_DIR + "tournaments.txt", "w") as f:
    for tour in alliance_items:
        tour.sort(key=lambda x: x["aid"])
        for player in tour:
            f.write("{0}\t{1}\n".format(player["aid"], player["asv"]))
        f.write("\n\n")


def getSanctPoints(guid, lvl, atk, hp, spd):
    creature_static = get_json_from_guid(guid)
    rarity = creature_static["r"]["guid"]
    if ("3a79f05ec39301d4083f30d662a439cf" in rarity) or ("4929e83e63dbaff429404bdc0e8f57f2" in rarity) or ("38a4e5df8bc1cab4ca23378186749bea" in rarity):
        return 0
    return int(creature_static["ad"] / 10000. * 0.08 * (1.05**(lvl-26) * (1 + (0.0125 * (atk + hp)) + 0.02 * spd)))


player_dict = dict()
tournament_dict = dict()
creature_dict = dict()
my_tz = timezone(timedelta(hours=3), name='MSK')
for player in player_items:
    id = str(player["id"])
    player_dict[id] = dict()
    if id in guilds_map.keys():
        player_dict[id]["Name"] = guilds_map[id]["name"]
    else:
        player_dict[id]["Name"] = str(id)
    player_dict[id]["Level"] = player["lvl"]
    player_dict[id]["time"] = datetime.fromtimestamp(player["lgt"] / 1000).astimezone(tz=my_tz).strftime('%d.%m.%Y %H:%M:%S')
    player_dict[id]["exp"] = player["exp"]
    player_dict[id]["Creatures"] = list()
    for creature in player["cl"]:
        new_creature = dict()
        new_creature["id"] = creature["cid"].split()[0]
        new_creature["Name"] = find_name(creature["cid"].split()[0])
        new_creature["Level"] = creature["level"] + creature["cpl"]
        new_creature["Boosts"] = list()
        for boost_name in ["aepa", "aeph", "aeps"]:
            new_creature["Boosts"].append(int(creature["caeps"][boost_name]/100) if boost_name in creature["caeps"].keys() else 0)
        new_creature["SancPoints"] = getSanctPoints(new_creature["id"], creature["level"], *new_creature["Boosts"])
        player_dict[id]["Creatures"].append(new_creature)
        if new_creature["id"] not in creature_dict.keys():
            creature_dict[new_creature["id"]] = dict()
            creature_dict[new_creature["id"]]["Name"] = new_creature["Name"]
            creature_dict[new_creature["id"]]["id"] = new_creature["id"]
            creature_dict[new_creature["id"]]["Levels"] = list()
            creature_dict[new_creature["id"]]["AtkBoosts"] = list()
            creature_dict[new_creature["id"]]["HPBoosts"] = list()
            creature_dict[new_creature["id"]]["SpdBoosts"] = list()
            creature_dict[new_creature["id"]]["SancPoints"] = list()
        creature_dict[new_creature["id"]]["Levels"].append(new_creature["Level"])
        creature_dict[new_creature["id"]]["AtkBoosts"].append(new_creature["Boosts"][0])
        creature_dict[new_creature["id"]]["HPBoosts"].append(new_creature["Boosts"][1])
        creature_dict[new_creature["id"]]["SpdBoosts"].append(new_creature["Boosts"][2])
        creature_dict[new_creature["id"]]["SancPoints"].append(new_creature["SancPoints"])

        for team in player["cdl"]:
            tour_name = team["did"] + "__" + team["dsid"]
            if tour_name not in tournament_dict.keys():
                tournament_dict[tour_name] = dict()
                tournament_dict[tour_name]["playerCount"] = 1
                tournament_dict[tour_name]["creatures"] = dict()
            else:
                tournament_dict[tour_name]["playerCount"] += 1
            for creature in team["cl"]:
                if creature:
                    creature_id = creature.split()[0]
                    if creature_id not in tournament_dict[tour_name]["creatures"].keys():
                        tournament_dict[tour_name]["creatures"][creature_id] = dict()
                        tournament_dict[tour_name]["creatures"][creature_id]["id"] = creature_id
                        tournament_dict[tour_name]["creatures"][creature_id]["count"] = 1
                        tournament_dict[tour_name]["creatures"][creature_id]["name"] = find_name(creature_id)
                    else:
                        tournament_dict[tour_name]["creatures"][creature_id]["count"] += 1


for player in player_dict.values():
    player["Creatures"].sort(key=lambda x: x["Level"], reverse=True)

creature_list = list()
for creature in creature_dict.values():
    new_creature = dict()
    new_creature["id"] = creature["id"]
    new_creature["Name"] = creature["Name"]
    new_creature["Count"] = len(creature["Levels"])
    new_creature["AverageLevel"] = sum(creature["Levels"])/len(creature["Levels"])
    new_creature["AverageAtkBoost"] = sum(creature["AtkBoosts"]) / len(creature["AtkBoosts"])
    new_creature["AverageHPBoost"] = sum(creature["HPBoosts"]) / len(creature["HPBoosts"])
    new_creature["AverageSpdBoost"] = sum(creature["SpdBoosts"]) / len(creature["SpdBoosts"])
    creature_list.append(new_creature)

creature_list.sort(key=lambda x: x["AverageLevel"], reverse=True)

for tournament in tournament_dict.values():
    tournament["creatures"] = sorted(tournament["creatures"].values(), key=lambda x: x["count"], reverse=True)

with open(JSON_DIR + "players.json", "w") as f:
    json.dump(player_dict, f, indent=2)
with open(JSON_DIR + "tournament.json", "w") as f:
    json.dump(tournament_dict, f, indent=2)
with open(JSON_DIR + "creature_list.json", "w") as f:
    json.dump(creature_list, f, indent=2)
with open(JSON_DIR + "creature_dict.json", "w") as f:
    json.dump(creature_dict, f, indent=2)

SP = list()
for player_id in player_dict:
    player = player_dict[player_id]
    if player_id in guilds_map.keys():
        guild = guilds_map[player_id]["guild"]
        name = guilds_map[player_id]["name"]
    else:
        name = str(player_id)
        guild = ""
    for creature in player["Creatures"]:
        SP.append([name, guild, creature["Name"], str(creature["SancPoints"])])
with open(JSON_DIR + "sanctuaryTop.txt", "w") as f:
    f.write("\n".join(["\t".join(x) for x in sorted(SP, key=lambda x: int(x[3]), reverse=True)]))

print("Parsed {0} players".format(len(player_dict)))

mission_map = list()
for i in range(10):
    mission_map.append(dict())
for message in strings:
    if "p" in message.keys():
        if "p" in message["p"].keys():
            if "mk" in message["p"]["p"].keys():
                if message["p"]["p"]["mk"] == "j.saugm":
                    mission_map = list()
                    for i in range(10):
                        mission_map.append(dict())
                    tracks = message["p"]["p"]["msg"]["gmtm"]
                    track_shift = 0
                    for track_id in ["CurTrack0", "CurTrack1"]:
                        for stage in tracks[track_id]["tl"]:
                            for mission in stage["ip"]:
                                mission_index = mission["mi"] + track_shift
                                for player in mission["ppm"].keys():
                                    if player in mission_map[mission_index].keys():
                                        mission_map[mission_index][player] += mission["ppm"][player]
                                    else:
                                        mission_map[mission_index][player] = mission["ppm"][player]
                        track_shift += 5

player_set = set([x for y in mission_map for x in y.keys()])
for player in sorted(list(player_set)):
    # name = guilds_map[int(player)]["name"] if int(player) in guilds_map.keys() else player
    player_line = player
    for mission in mission_map:
        player_line += "\t" + str((mission[player] if player in mission.keys() else 0))
    print(player_line)
