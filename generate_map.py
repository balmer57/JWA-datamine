import os
import json
from utilities import *


def parse_all(base_dir):
    keys_storage = []
    key_set = set()

    # Parse databases
    with open(DATA_DIR + "DataDatabase.json") as f:
        data = json.load(f)
        for key in data["Data"].keys():
            if len(key) > 10:
                if key not in guid_map.keys():
                    guid_map[key] = dict()
                guid_map[key]["owner"] = data["Data"][key]

    with open(DATA_DIR + "AssetsDatabase.json") as f:
        data = json.load(f)
        for key in data["Assets"].keys():
            if len(key) > 10:
                if key not in guid_map.keys():
                    guid_map[key] = dict()
                guid_map[key]["owner"] = data["Assets"][key]["Path"]

    # Parse folders
    for (current_dir, dirs, filenames) in os.walk(base_dir):
        keys_by_dir = set()
        if current_dir != base_dir:
            for f_name in filenames:
                global current_file_name
                current_file_name = current_dir[len(base_dir):] + "/" + f_name
                try:
                    with open(current_dir + "/" + f_name) as f:
                        data = json.load(f, object_pairs_hook=guid_hook)
                        keys_by_dir.update(data.keys())
                        if "guid" in data.keys():
                            if data["guid"] != "":
                                process_guid(data, main=True)
                except:
                    print("Exception {0}".format(current_file_name))
            keys_storage.append(list(keys_by_dir))
            key_set.update(keys_by_dir)

    return keys_storage, key_set


def subst_all(base_dir, target_dir):
    # Parse folders
    for (current_dir, dirs, filenames) in os.walk(base_dir):
        if current_dir != base_dir:
            for f_name in filenames:
                global current_file_name
                current_file_name = current_dir[len(base_dir) + 1:] + "/" + f_name
                try:
                    with open(current_dir + "/" + f_name) as f:
                        data = json.load(f, object_pairs_hook=subst_guid_hook)
                        target_file_name = f_name.rsplit('.', maxsplit=1)[0] + "__" + current_dir.split("/")[-1].split("\\")[-1] + "." + f_name.rsplit('.', maxsplit=1)[1]
                        with open(target_dir + "/" + target_file_name, "w") as g:
                            json.dump(data, g, indent=2)
                except:
                    pass


def load_term_dict(f_name):
    terms = dict()
    with open(f_name) as f:
        lines = f.readlines()
        for line in lines:
            term, descr = line.split(maxsplit=1)
            terms[term.strip()] = descr.strip()
    return terms


def guid_hook(pairs):
    pair_dict = dict(pairs)
    if "guid" in pair_dict.keys():
        if pair_dict["guid"] != "":
            process_guid(pair_dict)
    return pair_dict


def subst_guid_hook(pairs):
    for i in range(len(pairs)):
        if pairs[i][0] in term_dict.keys():
            pairs[i] = (term_dict[pairs[i][0]], pairs[i][1])
    pair_dict = dict(pairs)
    if "guid" in pair_dict.keys():
        if (pair_dict["guid"] != "") and pair_dict["guid"] and ("owner" in guid_map[pair_dict["guid"]].keys()):
            pair_dict["guid"] = guid_map[pair_dict["guid"]]["owner"].split("/")[-1]
    return pair_dict


def process_guid(data, main=False):
    if main:
        if data["guid"] in guid_map.keys():
            if "owner" in guid_map[data["guid"]].keys():
                print("Owner change: from {0} to {1}".format(guid_map[data["guid"]]["owner"], current_file_name))
        else:
            guid_map[data["guid"]] = dict()

        guid_map[data["guid"]]["owner"] = current_file_name
    else:
        if data["guid"] not in guid_map.keys():
            guid_map[data["guid"]] = dict()
        if "references" not in guid_map[data["guid"]].keys():
            guid_map[data["guid"]]["references"] = list()
        guid_map[data["guid"]]["references"].append(current_file_name)

    if "TypeName" in data.keys():
        if "type" in guid_map[data["guid"]].keys():
            if guid_map[data["guid"]]["type"] != data["TypeName"]:
                print("Type conflict: {0} {1}".format(guid_map[data["guid"]]["type"], data["TypeName"]))
    guid_map[data["guid"]]["type"] = data["TypeName"]


current_file_name = ""
guid_map = dict()
keys, key_set = parse_all(DATA_DIR)
keys = set([str(x) for x in keys])
keys.remove("[]")
with open(JSON_DIR + "keys_list.txt", "w") as g:
    g.write("\n".join(list(keys)))

term_dict = load_term_dict(JSON_DIR + "terms.txt")

with open(JSON_DIR + "guid_map.json", "w") as g:
    json.dump(guid_map, g)
with open(JSON_DIR + "guid_map_indent.json", "w") as g:
    json.dump(guid_map, g, indent=2)

subst_all(DATA_DIR, BASE_DIR + "assets")


with open(DATA_DIR + "DataDatabase.json") as f:
    guid_map = json.load(f)["Data"]

creature_names = dict()
for key in guid_map.keys():
    entry = guid_map[key]
    fname = DATA_DIR + entry.split("/", maxsplit=2)[-1]
    if 'CreaturesStatic' in fname:
        with open(fname) as f:
            creature = json.load(f)
            if "lkn" in creature.keys():
                name = creature["lkn"]
                creature_names[key] = localization[name] if name in localization.keys() else name
with open(JSON_DIR + "creature_names.json", "w") as f:
    json.dump(creature_names, f)
