from utilities import *

creature_dict = dict()
id_table = dict()

for cur_dir, dirs, files in os.walk(DATA_DIR + "/Resource/Dna"):
    for file in files:
        with open(cur_dir + "/" + file) as f:
            dna_json = json.load(f)
            if dna_json["$type"].startswith("CrDNARe"):
                if dna_json["l"]:
                    guid = dna_json["cr"]["guid"]
                    name = find_name(guid)
                    id = dna_json["TypeId"]
                    creature_dict[guid] = {"id": id, "guid": guid, "name": name, "level": 0, "dna": 0}
                    id_table[id] = guid

with open(BASE_DIR + "/decoded_streams/GetResources.json") as f:
    messages = json.load(f)
    for message in messages:
        if message["p"]["c"] == "j.crg":
            if "res" in message["p"]["p"].keys():
                data = message["p"]["p"]["res"]
                for item in data:
                    id = item["t"]
                    if id in id_table.keys():
                        creature_dict[id_table[id]]["dna"] = item["a"]

with open(BASE_DIR + "/decoded_streams/GetCreatureList.json") as f:
    messages = json.load(f)
    for message in messages:
        if message["p"]["c"] == "j.clcgl":
            if "cl" in message["p"]["p"].keys():
                data = message["p"]["p"]["cl"]
                for item in data:
                    guid = item["cid"].split()[0]
                    if guid in creature_dict.keys():
                        creature_dict[guid]["level"] = item["level"]

creature_list = list()
for creature in creature_dict.values():
    creature_list.append([creature["name"], creature["level"], creature["dna"]])
for creature in sorted(creature_list):
    print("{}\t{}\t{}".format(*creature))
