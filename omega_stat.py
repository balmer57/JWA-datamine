from utilities import *
import os

for _, _, files in os.walk(DATA_DIR + "CreaturesStaticData"):
    for file in files:
        with open(DATA_DIR + "CreaturesStaticData/" + file) as f:
            data = json.load(f)
            if data["r"]["guid"] == "d9f9bbc76fb7d4e4489fb81286fb35a6":
                name = data["dn"]
                stats_base = get_json_from_guid(data["rl"][0]["att"]["guid"])
                omega_config = get_json_from_guid(data["capd"]["guid"])
                if omega_config:
                    stats_cap = get_json_from_guid(omega_config["cap"]["guid"])
                    stats_diff = get_json_from_guid(omega_config["app"]["guid"])
                    print(f"\n\n{name}\tHP\tAttack\tSpeed\tDef\tCrit chance\tCrit damage")
                    lines = [stats_base, stats_cap, stats_diff]
                    line_names = ["Base", "Max", "Diff"]
                    for line, line_name in zip(lines, line_names):
                        s = line_name
                        for stat in ["hp", "ap", "sp"] if "ap" in line.keys() else ["hp", "miap", "s"]:
                            s += "\t" + str(line[stat])
                        for stat in ["def", "chc", "chm"]:
                            s += "\t" + str(line[stat]/10000000)
                        print(s)
