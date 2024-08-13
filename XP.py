from utilities import *

players = dict()

with open(BASE_DIR + "decoded_streams/PlayerInfo.json") as f:
    data = json.load(f)
    for message in data:
        if "spl" in message['p']['p'].keys():
            for player in message['p']['p']["spl"]:
                players[player["id"]] = player["exp"]
    for id, score in sorted(players.items()):
        print("{0}\t{1}\t{2}".format(id, get_player_name(id), score))
