import json
import os
from utilities import *


effects = dict()
abilities = dict()
creatures = dict()
raids = dict()
sanctuary_base = dict()


def get_guid_by_filename(fname):
    for guid in guid_map:
        parts = guid_map[guid].rsplit("/", maxsplit=2)
        if len(parts) >= 2:
            if fname == parts[-2] + "/" + parts[-1]:
                return guid
    return "Unknown"


def ability_container(ability_json):
    ability = dict()
    if ability_json["ai"]["guid"]:
        if ability_json["$type"].startswith("AbIt"):
            ability["Split"] = "None"
            ability["Ability"] = abilities[ability_json["ai"]["guid"]]
        if ability_json["$type"].startswith("ReAbIt"):
            ability["Split"] = "Revenge"
            ability["AbilityNormal"] = abilities[ability_json["ai"]["guid"]]
            ability["AbilityRevenge"] = abilities[ability_json["rai"]["guid"]]
        if ability_json["$type"].startswith("ThAbIt"):
            ability["Split"] = "Threshold"
            if ability_json["hltc"] == "lower":
                ability["AbilityLow"] = abilities[ability_json["otai"]["guid"]] if ability_json["otai"]["guid"] else None
                ability["AbilityHigh"] = abilities[ability_json["ai"]["guid"]]
            else:
                ability["AbilityLow"] = abilities[ability_json["ai"]["guid"]]
                ability["AbilityHigh"] = abilities[ability_json["otai"]["guid"]] if ability_json["otai"]["guid"] else None
            ability["Threshold"] = ability_json["hltv"] / 100.
    return ability


def attributes_by_guid(guid):
    attr_file = DATA_DIR + "../../" + guid_map[guid]
    attr_file2 = DATA_DIR + "../../" + guid_map[guid].replace("/Data/", "/Data2/")
    if os.path.exists(attr_file2):
        attr_file = attr_file2
    with open(attr_file) as g:
        attr_json = json.load(g)
        return attribute_container(attr_json)


def attribute_container(attr_json):
    attr = dict()
    attr_map = {"hp": "HP", "miap": "Attack", "s": "Speed"}
    attr_map2 = {"def": "Armor", "chc": "Critical chance", "chm": "Critical multiplier"}
    res_map = {"rs": "Stun", "rsp": "Antiswap", "rt": "Taunt", "rr": "Rend", "rd": "Distract", "rdot": "DoT", "rv": "Vulnerability", "rdec": "Decelerate", "rcrit": "Crit", "rarm": "Armor", "raff": "Affliction"}
    for attr_key in attr_map.keys():
        attr[attr_map[attr_key]] = attr_json[attr_key] if attr_key in attr_json.keys() else 0
    for attr_key in attr_map2.keys():
        attr[attr_map2[attr_key]] = attr_json[attr_key]/10000000 if attr_key in attr_json.keys() else 0.0
    attr["Resistances"] = dict()
    for attr_key in res_map.keys():
        attr["Resistances"][res_map[attr_key]] = attr_json[attr_key]/10000000 if attr_key in attr_json.keys() else 0.0
    return attr


def process_effect_files(cur_dir, files):
    for file in files:
        with open(cur_dir + "/" + file) as f:
            effect_json = json.load(f)
            effect_type = effect_json["$type"]
            if effect_type.startswith("Be"):
                effect = dict()
                effect["Target"] = effect_json["tr"] if "tr" in effect_json.keys() else effect_json["at"]
                effect["TargetCount"] = effect_json["tc"] if "tc" in effect_json.keys() else 4 if effect["Target"] == "All" else 1
                if effect["TargetCount"] == 4:
                    effect["Target"] = "All"
                if effect["TargetCount"] > 1 and effect["Target"] != "All":
                    print("Strange target count in file {0}".format(file))
                effect["Team"] = effect_json["tg"] if "tg" in effect_json.keys() else "Self"
                if "None" == effect["Target"]:
                    if 4 == effect_json["tc"]:
                        effect["Target"] = "All"
                if effect_type.startswith("BeDa"):
                    if effect_type.startswith("BeDaHp"):
                        effect["Type"] = "Rend"
                        effect["Value"] = effect_json["dp"]/10000000.
                    elif effect_type.startswith("BeDaMe"):
                        effect["Type"] = "Devour"
                        effect["Value"] = effect_json["dm"]/10000000.
                        effect["Heal"] = effect_json["mp"] / 10000000.
                        effect["Turns"] = effect_json["md"]
                    else:
                        effect["Type"] = "Damage"
                        effect["Value"] = effect_json["dm"]/10000000.
                    effect["ArmorBypass"] = effect_json["sb"]
                    effect["Precise"] = effect_json["db"]
                elif effect_type.startswith("BeEf"):
                    if effect_type.startswith("BeEfIn"):
                        if effect_type.startswith("BeEfInScDa"):
                            effect["Type"] = "Nullify"
                            effect["Stat"] = "All"
                        elif effect_type.startswith("BeEfInNuDa"):
                            effect["Type"] = "Nullify"
                            effect["Stat"] = effect_json["ne"]
                        elif effect_type.startswith("BeEfInDeShDa"):
                            effect["Type"] = "Nullify"
                            effect["Stat"] = "Shields"
                        elif effect_type.startswith("BeEfInClDa"):
                            effect["Type"] = "Cleanse"
                            effect["Stat"] = effect_json["ce"] if "ce" in effect_json.keys() else "All"
                        elif effect_type.startswith("BeEfInReDeDaDa"):
                            effect["Type"] = "Cleanse"
                            effect["Stat"] = "DebuffAttack"
                        elif effect_type.startswith("BeEfInReHaFoSwDa"):
                            effect["Type"] = "ForceSwap"
                        else:
                            print("Not parsed type: {0} in file {1}".format(effect_type, file))
                    elif effect_type.startswith("BeEfDu"):
                        effect["Turns"] = effect_json["d"]
                        effect["Attacks"] = effect_json["eac"] if "eac" in effect_json.keys() else 0
                        if effect_type.startswith("BeEfDuSwPrDa"):
                            effect["Type"] = "NoSwap"
                        elif effect_type.startswith("BeEfDuVuDa"):
                            effect["Type"] = "Vulnerability"
                            effect["Value"] = effect_json["vuln"] / 10000000.
                        elif effect_type.startswith("BeEfDuShDa"):
                            effect["Type"] = "Shield"
                            effect["Value"] = effect_json["slvl"] / 10000000.
                        elif effect_type.startswith("BeEfDuStDa"):
                            effect["Type"] = "Stun"
                            effect["Chance"] = effect_json["ps"] / 10000000.
                        elif effect_type.startswith("BeEfDuDoDa"):
                            effect["Type"] = "DoT"
                            effect["Value"] = effect_json["ppt"] / 10000000.
                        elif effect_type.startswith("BeEfDuReBuDeDa"):
                            effect["Type"] = "Affliction"
                            effect["Value"] = effect_json["p"] / 10000000.
                        elif effect_type.startswith("BeEfDuDeImDa"):
                            effect["Type"] = "DebuffImmune"
                        elif effect_type.startswith("BeEfDuStImDa"):
                            effect["Type"] = "StunImmune"
                        elif effect_type.startswith("BeEfDuSwPrImDa"):
                            effect["Type"] = "SwapLockImmune"
                        elif effect_type.startswith("BeEfDuVuImDa"):
                            effect["Type"] = "VulnerabilityImmune"
                        elif effect_type.startswith("BeEfDuSpReImDa"):
                            effect["Type"] = "DecelerationImmune"
                        elif effect_type.startswith("BeEfDuDaReImDa"):
                            effect["Type"] = "DistractionImmune"
                        elif effect_type.startswith("BeEfDuDoImDa"):
                            effect["Type"] = "DoTImmune"
                        elif effect_type.startswith("BeEfDuLoDa"):
                            effect["Type"] = "NoSwap"
                        elif effect_type.startswith("BeEfDuTaDa"):
                            effect["Type"] = "Taunt"
                        elif effect_type.startswith("BeEfDuDodDa"):
                            effect["Type"] = "Dodge"
                            effect["Value"] = effect_json["pdr"] / 10000000.
                            effect["Chance"] = effect_json["p"] / 10000000.
                        elif effect_type.startswith("BeEfDuInDa"):
                            effect["Type"] = "Cloak"
                            effect["Value"] = effect_json["pdr"] / 10000000.
                            effect["Chance"] = effect_json["p"] / 10000000.
                            effect["DamageBuff"] = effect_json["mn"] / 10000000.
                        elif effect_type.startswith("BeEfDuBuDeDa"):
                            if effect_json["p"] > 0:
                                effect["Type"] = "Buff"
                                effect["Value"] = effect_json["p"] / 10000000.
                            else:
                                effect["Type"] = "Debuff"
                                effect["Value"] = -effect_json["p"] / 10000000.
                            effect["Stat"] = effect_json["aa"]
                            # effect["Cumulative"] = effect_json["c"]
                        elif effect_type.startswith("BeEfDuCoAtDa"):
                            effect["Type"] = "None"
                        elif effect_type.startswith("BeEfDuOnOpEsDa"):
                            effect["Type"] = "None"
                        else:
                            print("Not parsed type: {0} in file {1}".format(effect_type, file))
                    else:
                        print("Not parsed type: {0} in file {1}".format(effect_type, file))
                elif effect_type.startswith("BeHe"):
                    if effect_type.startswith("BeHePeDa"):
                        effect["Type"] = "Heal"
                        effect["Source"] = effect_json["pb"] if "pb" in effect_json.keys() else None
                        effect["Value"] = effect_json["p"] / 10000000.
                        effect["Rally"] = effect_json["ttb"] if "ttb" in effect_json.keys() else False
                else:
                    print("Not parsed type: {0} in file {1}".format(effect_type, file))

                folder = cur_dir.rsplit("/", maxsplit=1)[-1].rsplit("\\", maxsplit=1)[-1]
                guid = get_guid_by_filename(folder + "/" + file)
                effect["guid"] = guid
                effects[guid] = effect


# Effects
for cur_dir, dirs, files in os.walk(DATA_DIR + "/AbilityStaticData"):
    process_effect_files(cur_dir, files)
for cur_dir, dirs, files in os.walk(DATA_DIR + "../Data2/AbilityStaticData"):
    process_effect_files(cur_dir, files)


def process_abilities_files(cur_dir, files):
    for file in files:
        with open(cur_dir + "/" + file) as f:
            ability_json = json.load(f)
            ability_type = ability_json["$type"]
            if 'n' not in ability_json.keys():
                continue
            ability = dict()
            ability["Name"] = ability_json["n"]
            if ability["Name"] in localization.keys():
                ability["LocalizationName"] = localization[ability["Name"]]
            ability["Description"] = ability_json["d"]
            if ability_type.startswith("AbStDa"):
                ability["Type"] = "Active"
                ability["Priority"] = ability_json["pri"]
                ability["Cooldown"] = ability_json["c"]
                ability["Delay"] = ability_json["cod"]
                ability["effects"] = list()
                if not ability_json["bl"]:
                    print("Unknown ability in file {0}".format(file))
                else:
                    fixed_target = None
                    fixed_target_team = None
                    fixed_target_count = None
                    for i in range(len(ability_json["bl"])):
                        if ability_json["bl"][i] is not None:
                            guid = ability_json["bl"][i]["b"]["guid"]
                            if guid in effects.keys():
                                effect = dict(effects[guid])
                                if "t" in ability_json["bl"][i].keys():
                                    if ability_json["bl"][i]["t"] == "s":
                                        fixed_target = effect["Target"]
                                        fixed_target_team = effect["Team"]
                                        fixed_target_count = effect["TargetCount"]
                                    if (ability_json["bl"][i]["t"] == "u") and fixed_target:
                                        if (effect["Target"] != fixed_target) and (effect["Team"] == fixed_target_team):
                                            effect["LegacyTarget"] = effect["Target"]
                                            effect["Target"] = fixed_target
                                            effect["LegacyCount"] = effect["TargetCount"]
                                            effect["TargetCount"] = fixed_target_count
                                    effect["TargetOverride"] = ability_json["bl"][i]["t"]
                                ability["effects"].append(effect)
                            elif guid:
                                print("Unknown effect {0} in file {1}".format(guid, file))
            elif ability_type.startswith("PaStDa"):
                ability["Type"] = "Passive"
                guid = ability_json["b"]["guid"]
                ability["effects"] = [effects[guid]]
            else:
                continue

            folder = cur_dir.rsplit("/", maxsplit=1)[-1].rsplit("\\", maxsplit=1)[-1]
            guid = get_guid_by_filename(folder + "/" + file)
            ability["guid"] = guid
            abilities[guid] = ability


# Abilities
for cur_dir, dirs, files in os.walk(DATA_DIR + "/AbilityStaticData"):
    process_abilities_files(cur_dir, files)
for cur_dir, dirs, files in os.walk(DATA_DIR + "../Data2/AbilityStaticData"):
    process_abilities_files(cur_dir, files)


def process_creature_files(cur_dir, files):
    for file in files:
        with open(cur_dir + "/" + file) as f:
            creature_json = json.load(f)
            creature_type = creature_json["$type"]
            if creature_type.startswith("CrStDa"):
                creature = dict()
                creature["Name"] = creature_json["lkn"]
                if creature["Name"] in localization.keys():
                    creature["LocalizationName"] = localization[creature["Name"]]
                if len(creature_json["rl"]) == 1:
                    attr_guid = creature_json["rl"][0]["att"]["guid"]
                    if attr_guid in guid_map.keys():
                        creature["Stats"] = attributes_by_guid(attr_guid)
                    creature["Abilities"] = list()
                    creature["Type"] = "Creature"
                    for i in range(len(creature_json["rl"][0]["al"])):
                        if creature_json["rl"][0]["al"][i] is not None:
                            creature["Abilities"].append(ability_container(creature_json["rl"][0]["al"][i]))
                    if ("sia" in creature_json["rl"][0].keys()) and creature_json["rl"][0]["sia"]:
                        creature["SwapIn"] = ability_container(creature_json["rl"][0]["sia"])
                    if ("ac" in creature_json["rl"][0].keys()) and creature_json["rl"][0]["ac"]:
                        creature["Counter"] = ability_container(creature_json["rl"][0]["ac"])
                    if ("aooe" in creature_json["rl"][0].keys()) and creature_json["rl"][0]["aooe"]:
                        creature["SwapOut"] = ability_container(creature_json["rl"][0]["aooe"])
                elif len(creature_json["rl"]) > 1:
                    creature["Type"] = "Boss"
                    creature["Rounds"] = list()
                    for i in range(len(creature_json["rl"])):
                        raid_round = dict()
                        attr_guid = creature_json["rl"][i]["att"]["guid"]
                        if attr_guid in guid_map.keys():
                            raid_round["Stats"] = attributes_by_guid(attr_guid)
                        raid_round["Abilities"] = list()
                        for j in range(len(creature_json["rl"][i]["al"])):
                            if creature_json["rl"][i]["al"][j] is not None:
                                raid_round["Abilities"].append(ability_container(creature_json["rl"][i]["al"][j]))
                        if ("ac" in creature_json["rl"][i].keys()) and creature_json["rl"][i]["ac"]:
                            raid_round["Counter"] = ability_container(creature_json["rl"][i]["ac"])
                        creature["Rounds"].append(raid_round)
                folder = cur_dir.rsplit("/", maxsplit=1)[-1].rsplit("\\", maxsplit=1)[-1]
                guid = get_guid_by_filename(folder + "/" + file)
                creature["guid"] = guid
                creatures[guid] = creature
                localization_name = localization[creature["Name"]] if creature["Name"] in localization.keys() else creature["Name"]
                sanctuary_base[guid] = (localization_name, creature_json["ad"])


# Creatures
for cur_dir, dirs, files in os.walk(DATA_DIR + "/CreaturesStaticData"):
    process_creature_files(cur_dir, files)
for cur_dir, dirs, files in os.walk(DATA_DIR + "../Data2/CreaturesStaticData"):
    process_creature_files(cur_dir, files)


def process_creature_files(cur_dir, files):
    for file in files:
        with open(cur_dir + "/" + file) as f:
            raid_json = json.load(f)
            raid_type = raid_json["$type"]
            if raid_type.startswith("Rddt"):
                raid = dict()
                raid["Name"] = raid_json["rn"]
                raid["Creatures"] = list()
                for i in range(len(raid_json["rdaipy"])):
                    creature_json = raid_json["rdaipy"][i]["rdct"]
                    creature = dict()
                    creature["Creature"] = creatures[creature_json["pvecrsd"]["guid"]]
                    creature["Level"] = creature_json["crlvl"]
                    creature["AttackBoost"] = creature_json["aepat"]
                    creature["HPBoost"] = creature_json["aepht"]
                    creature["SpeedBoost"] = creature_json["aepst"]
                    raid["Creatures"].append(creature)
                folder = cur_dir.rsplit("/", maxsplit=1)[-1].rsplit("\\", maxsplit=1)[-1]
                guid = get_guid_by_filename(folder + "/" + file)
                raid["guid"] = guid
                raids[guid] = raid


# Raids
for cur_dir, dirs, files in os.walk(DATA_DIR + "/Raid"):
    process_creature_files(cur_dir, files)
for cur_dir, dirs, files in os.walk(DATA_DIR + "../Data2/Raid"):
    process_creature_files(cur_dir, files)


with open(JSON_DIR + "Effectdex.json", "w") as f:
    json.dump(effects, f, indent=2)
with open(JSON_DIR + "Abilitydex.json", "w") as f:
    json.dump(abilities, f, indent=2)
with open(JSON_DIR + "Creaturedex.json", "w") as f:
    json.dump(creatures, f, indent=2)
with open(JSON_DIR + "Raiddex.json", "w") as f:
    json.dump(raids, f, indent=2)
with open(JSON_DIR + "SanctuaryBasePoints.json", "w") as f:
    json.dump(sanctuary_base, f, indent=2)
with open(JSON_DIR + "SanctuaryBasePoints.txt", "w") as f:
    for creature in sanctuary_base.values():
        f.write("{0}\t{1}\n".format(*creature))


for key in abilities.keys():
    enemy = 0
    ally = 0
    s = 0
    s_team = None
    s_target = None
    ally_target = None
    enemy_target = None
    total = 0
    if "effects" not in abilities[key].keys():
        print(abilities[key])
        continue
    for effect in abilities[key]["effects"]:
        if "TargetOverride" in effect.keys():
            name = guid_map[key].split("/")[-1] + " (" + key + ")"
            if effect["TargetOverride"] == "s":
                s += 1
                if s > 1:
                    if (s_team == effect["Team"]) and not ((effect["Target"] == "All") and (s_target == "All")):
                        print("s > 1: " + name)
                s_team = effect["Team"]
                s_target = effect["Target"]
            if effect["Team"] == "Enemy":
                enemy += 1
                if not enemy_target:
                    if (effect["TargetOverride"] == "u") and (total == 0):
                        print("u to None: " + name)
                if (effect["Target"] != "All") and (enemy > 1):
                    if (effect["TargetOverride"] != "u") and (s > 0):
                        print("enemy > 1, not u: " + name)
                if enemy > 1:
                    if (effect["TargetOverride"] == "s") and not ((effect["Target"] == "All") and (enemy_target == "All")):
                        print("enemy > 1, s: " + name)
                if effect["TargetOverride"] != "u":
                    enemy_target = effect["Target"]
            elif effect["Team"] == "Ally":
                ally += 1
                if not ally_target:
                    if (effect["TargetOverride"] == "u") and (total == 0):
                        print("u to None: " + name)
                if (effect["Target"] != "All") and (ally > 1):
                    if (effect["TargetOverride"] != "u") and (s > 0):
                        print("ally > 1, not u: " + name)
                if enemy > 1:
                    if (effect["TargetOverride"] == "s") and not ((effect["Target"] == "All") and (ally_target == "All")):
                        print("ally > 1, s: " + name)
                if effect["TargetOverride"] != "u":
                    ally_target = effect["Target"]
            total += 1

