import json
from datetime import datetime, timezone, timedelta
import os

VERSION = "3_7_29"
BASE_DIR = "D:/Dino/"
JSON_DIR = BASE_DIR + "json/"
DATA_DIR = f"D:/Dino/{VERSION}/assets/Database/Assets/Data/"
DATA2_DIR = f"D:/Dino/{VERSION}/assets/Database/Assets/Data2/"
DATA1_DIR = f"D:/Dino/{VERSION}/assets/Database/Assets/Data1/"
CACHE_DIR = "D:/Dino/com.ludia.jw2/cache/OnlineOptionCache/"
LOCALIZATION_FILE = "D:/Dino/Localization_JW_2_Global_ENGLISH.json"
IMG_DIR = BASE_DIR + "Img/"

with open(DATA_DIR + "DataDatabase.json") as f:
    guid_map = json.load(f)["Data"]
guid_map1 = dict()
if os.path.exists(DATA1_DIR):
    files = [f for f in os.listdir(DATA1_DIR) if os.path.isfile(os.path.join(DATA1_DIR, f))]
    for file in files:
        if file not in guid_map.keys():
            guid_map1[file] = "Assets/Data1/" + file
guid_map2 = dict()
if os.path.exists(DATA2_DIR):
    files = [f for f in os.listdir(DATA2_DIR) if os.path.isfile(os.path.join(DATA2_DIR, f))]
    for file in files:
        if file not in guid_map.keys():
            guid_map2[file] = "Assets/Data2/" + file
with open(DATA_DIR + "AssetsDatabase.json") as f:
    asset_map = json.load(f)["Assets"]
with open(LOCALIZATION_FILE, encoding="utf-8") as f:
    localization = json.load(f)
with open(JSON_DIR + "player_guilds.json") as f:
    guilds_map = json.load(f)
additional_players_Alliance = {3300000000001: "Unknown"}
for player in additional_players_Alliance:
    guilds_map[str(player)] = {"id": int(player), "name": additional_players_Alliance[player], "guild": "Alliance"}

sanc_items = list()
alliance_items = list()
player_items = list()
my_tz = timezone(timedelta(hours=3), name='MSK')


def get_player_name(id):
    if str(id) in guilds_map.keys():
        return guilds_map[str(id)]["name"]
    else:
        return str(id)


def get_json_from_guid(guid):
    if not guid:
        return {}
    guid = guid.split()[0]
    if guid in guid_map.keys():
        entry = guid_map[guid]
    else:
        entry = guid
    fname = DATA_DIR + "/" + entry.split("/", maxsplit=2)[-1]
    f2name = DATA2_DIR + "/" + entry.split("/", maxsplit=2)[-1]
    f1name = DATA1_DIR + "/" + entry.split("/", maxsplit=2)[-1]
    if os.path.exists(f2name):
        try:
            with open(f2name) as f:
                return json.load(f)
        except:
            pass
    elif os.path.exists(fname):
        try:
            with open(fname) as f:
                return json.load(f)
        except:
            pass
    elif os.path.exists(f1name):
        try:
            with open(f1name) as f:
                return json.load(f)
        except:
            pass
    return {}


def find_guid_by_name(name):
    for guid in guid_map.keys():
        if (guid_map[guid].split("/")[-1] == name) or (guid_map[guid].split("/")[-1] == name + ".json"):
            return guid
    for guid in guid_map2.keys():
        guid_json = get_json_from_guid(guid)
        if "bgn" in guid_json.keys():
            if guid_json["bgn"] == name:
                return guid
    return ""


def find_img(guid):
    if guid in guid_map.keys():
        entry = guid_map[guid]
        fname = DATA_DIR + "/../../" + entry
        with open(fname) as f:
            creature = json.load(f)
            img_guid = creature["i"]["guid"]
            return asset_map[img_guid]["Path"].split("/")[-1]
    return ""


def find_name(guid):
    if guid in guid_map.keys():
        entry = guid_map[guid]
        fname = DATA_DIR + "/" + entry.split("/", maxsplit=2)[-1]
        with open(fname) as f:
            creature = json.load(f)
            if "lkn" in creature.keys():
                name = creature["lkn"]
                return localization[name] if name in localization.keys() else ""
            else:
                if "n" in creature.keys():
                    name = creature["n"]
                    return localization[name] if name in localization.keys() else ""
                else:
                    return guid


def find_rarity(guid):
    if guid in guid_map.keys():
        entry = guid_map[guid]
        fname = DATA_DIR + "/" + entry.split("/", maxsplit=2)[-1]
        with open(fname) as f:
            creature = json.load(f)
            rarity = creature['r']['guid']
            rp = guid_map[rarity]
            if rp:
                return os.path.split(rp)[1][1:-5]


def guid_hook(pairs):
    pair_dict = dict(pairs)
    # Player Info
    if ("c" in pair_dict.keys()) and (pair_dict["c"] == "j.csfgpi"):
        if "spl" in pair_dict["p"].keys():
            for spl in pair_dict["p"]["spl"]:
                player_items.append(spl)
    # Main
    for (key, val) in pair_dict.items():
        if key in guid_map.keys():
            short_val = guid_map[key].rsplit("/", maxsplit=1)[-1]
            if isinstance(val, str):
                pair_dict[key] = pair_dict[key] + " (" + short_val + ")"
            elif isinstance(val, list):
                pair_dict[key] = ["(" + short_val + ")"] + pair_dict[key]
            elif isinstance(val, dict):
                pair_dict[key]["guid"] = short_val
            elif isinstance(val, int):
                pair_dict[key] = str(pair_dict[key]) + "(int) (" + short_val + ")"
        if isinstance(val, str):
            if val in guid_map.keys():
                short_val = guid_map[val].rsplit("/", maxsplit=1)[-1]
                pair_dict[key] = val + " (" + short_val + ")"
            elif (":" in val) and (val.split(":")[0] in guid_map.keys()):
                short_val = guid_map[val.split(":")[0]].rsplit("/", maxsplit=1)[-1]
                pair_dict[key] = val + " (" + short_val + ")"
        elif isinstance(val, list):
            for item_index in range(len(val)):
                item = val[item_index]
                if isinstance(item, str):
                    if item in guid_map.keys():
                        short_val = guid_map[item].rsplit("/", maxsplit=1)[-1]
                        pair_dict[key][item_index] = item + " (" + short_val + ")"

    # Sanctuary
    for (key, val) in pair_dict.items():
        if key == "edl":
            for item in val:
                sanc_items.append(item)
        elif key == "phase_end":
            if (isinstance(val, int)) and (val > 0):
                try:
                    dt = datetime.fromtimestamp(val / 1000).astimezone(tz=my_tz)
                    pair_dict[key] = dt.strftime('%d.%m.%Y %H:%M:%S')
                except:
                    print("Error val: {0}".format(val))
    # Alliance
    if ("mk" in pair_dict.keys()) and (pair_dict["mk"] == "j.sauap"):
        if "en" in pair_dict["msg"]["cl"].keys():
            alliance_items.append(pair_dict["msg"]["cl"]["en"])
    return pair_dict


