import os

from utilities import *
import json

dir_1 = r'D:\Dino\com.ludia.jw2\files'
dir_2 = r'D:\Dino\com.ludia.jw2\files1'

full_set = set()

for _, _, files in os.walk(dir_2):
    for file in files:
        if os.path.exists(dir_1 + '\\' + file):
            with open(dir_1 + '\\' + file) as f:
                json1 = json.load(f)
            with open(dir_2 + '\\' + file) as f:
                json2 = json.load(f)
            list1 = json1["MapInfo"]["TopScores"].keys()
            list2 = json2["MapInfo"]["TopScores"].keys()
            full_set = full_set.union(set(list1).difference(set(list2)))
players = sorted(list(full_set))

players = [get_player_name(x) for x in players]
print(players)
