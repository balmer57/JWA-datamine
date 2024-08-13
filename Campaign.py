import os
import json
from utilities import *

rewards = dict()

for cur_dir, dirs, files in os.walk(DATA_DIR + "Campaign/Campaign2.0"):
    for file in files:
        try:
            with open(os.path.join(cur_dir, file)) as f:
                data = json.load(f)
                if "cmrwds" in data.keys():
                    print("--- " + cur_dir + "/" + file + " ---")
                    # Rewards
                    for reward in data["cmrwds"]:
                        qty = reward["rewIt"]["q"]["v"]
                        guid = reward["rewIt"]["r"]["guid"]
                        if guid in rewards.keys():
                            rewards[guid] += qty
                        else:
                            rewards[guid] = qty
                    # Creatures
                    battle_guid = data["cdpvebd"]["guid"]
                    battle_data = get_json_from_guid(battle_guid)
                    for creature_link in battle_data["pvecrt"]:
                        creature_guid = creature_link["pvecrsd"]["guid"]
                        creature = get_json_from_guid(creature_guid)
                        creature_name = localization[creature["lkn"]]
                        print(creature_name)
        except:
            pass


for key, value in sorted(rewards.items(), key=lambda x: x[1], reverse=True):
    name = key
    rarity = ""
    if key in guid_map.keys():
        name = guid_map[key].rsplit("/", maxsplit=1)[-1][:-5]
        rew_json = get_json_from_guid(key)
        if "cr" in rew_json.keys():
            creature_DNA_guid = rew_json["cr"]["guid"]
            creature_DNA_data = get_json_from_guid(creature_DNA_guid)

            creature_data = get_json_from_guid(creature_DNA_data["cr"]["guid"])
            creature_lkn = creature_data["lkn"]

            name = localization[creature_lkn]
            if creature_lkn.startswith("IDS_"):
                loc_key = "IDS_LOWCASE_" + creature_lkn[4:]
                if loc_key in localization.keys():
                    name = localization[loc_key]
            rarity = creature_data['r']['guid']
            rp = guid_map[rarity]
            if rp:
                rarity = os.path.split(rp)[1][1:-5]

    print(f"{rarity}\t{name}\t{value}")
