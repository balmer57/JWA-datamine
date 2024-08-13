from datetime import datetime, timezone, timedelta
import json
import os
from utilities import *
from unpcap import *
import glob


def load_from_conv():
    sent = list()
    received = list()
    with open(BASE_DIR + "out/conv.txt") as f:
        strings = f.readlines()
        for line in strings:
            if line.startswith("sent"):
                sent += json.loads(line[8:], object_pairs_hook=guid_hook)
            elif line.startswith("received"):
                received += json.loads(line[12:], object_pairs_hook=guid_hook)
    return sent + received


def load_from_pcap(file_name=None):
    if file_name is None:
        files = list(filter(os.path.isfile, glob.glob(BASE_DIR + "*.pcap")))
        files.sort(key=os.path.getctime)
        fname = files[-1]
    else:
        fname = BASE_DIR + file_name
    print(f"Processing {fname}...")
    strings, strings_decoded = extract_pcap(fname)
    # strings = [x[0] for x in strings]
    return json.loads(json.dumps(strings), object_pairs_hook=guid_hook)


if __name__ == "__main__":
    messages = load_from_pcap()
else:
    messages = load_from_pcap()
print(len(messages))

command_names = dict()
command_names["c.ea"] = "GetCredentials"
command_names["c.fcs"] = "PlayerList1"
command_names["c.fhm"] = "Chat"
command_names["c.gs"] = "KeepAlive"
command_names["c.gt"] = "TimeRequest"
command_names["c.gtk"] = "GameUpdateToken"
command_names["c.ia"] = "SubscriptionIsActive"
command_names["c.lg"] = "PhoneFingerprint"
command_names["c.lv"] = "LoginVisitor"
command_names["c.mg"] = "InGameMessagesGet"
command_names["c.pr"] = "OnlineOptionsRead"
command_names["c.rp"] = "ResourceGetProductList"
command_names["c.vg"] = "GPlayAchievements"
command_names["j.ca2ca"] = "Achievement2"
command_names["j.ca2gal"] = "AchievementStats2"
command_names["j.cad"] = "CdnAssetDownloader"
command_names["j.cagal"] = "AchievementStats"
command_names["j.cbpcr"] = "PassRewards"
command_names["j.cbplss"] = "PassSomething"
command_names["j.cbps"] = "EventsSomething"
command_names["j.ccgcp"] = "Campaign"
command_names["j.cdare"] = "AddReadEvent"
command_names["j.cdge"] = "GetDazzleEvent"
command_names["j.cdlrc"] = "DailyLoginC"
command_names["j.cgad"] = "GetAuthoredData"
command_names["j.cgcp"] = "Scent2"
command_names["j.cgdc"] = "DroneCompleted"
command_names["j.cgdhs"] = "CreatureDex"
command_names["j.cgdls"] = "DailyLoginS"
command_names["j.cgdrdc"] = "Spawn"
command_names["j.cgds"] = "SpawnLocationInfo"
command_names["j.cgftue"] = "TutorialStatus"
command_names["j.cggap"] = "Scent"
command_names["j.cggdl"] = "GlobalCap"
command_names["j.cgglt"] = "DroneGetSpawnLocationLockTime"
command_names["j.cggsd"] = "GetSupplyDrop"
command_names["j.cglbc"] = "LobbyDataC"
command_names["j.cglbl"] = "LobbyData"
command_names["j.cgmv2s"] = "Missions"
command_names["j.cgrdf"] = "RadarDinoFocussed"
command_names["j.cgts"] = "Isla"
command_names["j.cgsdcs"] = "CollectSupplyDrop"
command_names["j.cgt"] = "GetTutorials"
command_names["j.cguap"] = "CreatureScentSomething"
command_names["j.cguls"] = "UnlockDate"
command_names["j.clce"] = "CreatureEvolve"
command_names["j.clcf"] = "Fuse"
command_names["j.clcgl"] = "GetCreatureList"
command_names["j.clcmf"] = "FuseMulti"
command_names["j.cldcl"] = "EmotesSomething"
command_names["j.clgcl"] = "Emotes"
command_names["j.clgdl"] = "GetDeckList"
command_names["j.clgdvl"] = "GetDiscovered"
command_names["j.clged"] = "EmotesList"
command_names["j.clgml"] = "Mail"
command_names["j.clgps"] = "GetPlayerStatus"
command_names["j.clmac"] = "ActionChoice"
command_names["j.clmj"] = "Me"
command_names["j.clmpr"] = "PVPLastPlayer"
command_names["j.cluc"] = "RadarDinoFocussed"
command_names["j.cludl"] = "Team"
command_names["j.cmbe"] = "BattleEmote"
command_names["j.cmc"] = "PVPMatchCreation"
command_names["j.cmcts"] = "TrackerActive"
command_names["j.ccts"] = "TrackerCreatures"
command_names["j.cmgil"] = "BattleIncubatorList"
command_names["j.cmgt"] = "EventTimedList"
command_names["j.cmip"] = "MatchInProgress"
command_names["j.cmodi"] = "PVPDailyIncubator"
command_names["j.cmui"] = "PVPNewIncubator"
command_names["j.cmv2ar"] = "MissionsProgress"
command_names["j.cns"] = "NewSessionRequest"
command_names["j.crg"] = "GetResources"
command_names["j.csb"] = "StartBootstrap"
command_names["j.csfclg"] = "CollectDNAChat"
command_names["j.csfdg"] = "DonateDNAChat"
command_names["j.csfgpi"] = "PlayerInfo"
command_names["j.csfslul"] = "Language"
command_names["j.csgllog"] = "PlayerList2"
command_names["j.csgps"] = "SanctuaryCreatures"
command_names["j.csgsi"] = "GetStoreItemList"
command_names["j.cspi"] = "MarketIncubator"
command_names["j.csts"] = "SetTutorialState"
command_names["j.csv"] = "GetServerVersion"
command_names["j.rdm"] = "(Ping)"
command_names["j.rdma"] = "BattleTurn"
command_names["j.sgrfs"] = "Mentee"
command_names["j.sgwbs"] = "WelcomeBack"
command_names["x.ef"] = "EventsData"


command_dict = dict()
undecoded_messages = list()

for msg in messages:
    if msg["c"]:
        command = msg["p"]["c"]
        if command in command_names.keys():
            command = command_names[command]
        else:
            undecoded_messages.append(msg["p"])
        if command in command_dict.keys():
            command_dict[command].append(msg)
        else:
            command_dict[command] = [msg]


with open(JSON_DIR + "messages.json", "w") as f:
    json.dump(undecoded_messages, f, indent=2)

for key in command_dict.keys():
    with open(BASE_DIR + "decoded_streams/" + key + ".json", "w") as f:
        json.dump(command_dict[key], f, indent=2)


if "EventsData" in command_dict.keys():
    ongoing = {"long": list(), "shop": list(), "battle": list(), "ESD": list(), "News": list(), "tournament": list(), "other": list()}
    future = json.loads(json.dumps(ongoing))
    past = json.loads(json.dumps(ongoing))
    all_events = {"past": past, "ongoing": ongoing, "future": future}
    events = command_dict["EventsData"]
    UTC_tz = timezone(timedelta(0), name='UTC')
    my_tz = timezone(timedelta(hours=3), name='MSK')
    now = datetime.now().astimezone(tz=my_tz)
    for message in events:
        event_list = message['p']['p']['e']
        if isinstance(event_list, list):
            for event in event_list:
                if 's' in event.keys():
                    start = datetime.fromtimestamp(event['s']/1000).astimezone(tz=my_tz)
                    end = datetime.fromtimestamp(event['e']/1000).astimezone(tz=my_tz)
                    event['s'] = start.strftime('%d.%m.%Y %H:%M:%S')
                    event['e'] = end.strftime('%d.%m.%Y %H:%M:%S')
                    duration = (end - start).total_seconds()
                    if start <= now <= end:
                        time_key = "ongoing"
                    elif now < start:
                        time_key = "future"
                    else:
                        time_key = "past"
                    if (event["n"] == "TournamentEvent") or (event["n"] == "Championship Event"):
                        all_events[time_key]["tournament"].append(event)
                    elif duration > 86400 * 60:
                        all_events[time_key]["long"].append(event)
                    elif (event["n"] == "SpecialOfferEventV2") or (event["n"].startswith("SO_")) or (event["n"].startswith("VIP_")):
                        all_events[time_key]["shop"].append(event)
                    elif event["n"].startswith("PVE_"):
                        all_events[time_key]["battle"].append(event)
                    elif event["n"].startswith("ESD_"):
                        all_events[time_key]["ESD"].append(event)
                    elif event["n"] == "NCGenericEvent":
                        all_events[time_key]["News"].append(event)
                    else:
                        all_events[time_key]["other"].append(event)

    for l in ongoing.keys():
        ongoing[l].sort(key=lambda x: x["as"])
    for l in future.keys():
        future[l].sort(key=lambda x: x["as"])
    with open(JSON_DIR + "events.json", 'w') as f:
        json.dump(all_events, f, indent=2)

if "AchievementStats2" in command_dict.keys():
    incompleted = list()
    achievement_messages = command_dict["AchievementStats2"]
    for message in achievement_messages:
        if "acm" in message["p"]["p"]:
            for achievement in message["p"]["p"]["acm"].values():
                if achievement["ste"] != "cpt":
                    ach_data = dict()
                    if "guid" in achievement.keys():
                        name = achievement["guid"]
                        if name.endswith(".json"):
                            name = name[:-5]
                        if name.startswith("Ach"):
                            name = name[4:]
                        ach_data["name"] = name
                        progress = json.loads(json.dumps(achievement["prg"]))
                        if "_StateObjectClass" in progress.keys():
                            progress.pop("_StateObjectClass")
                        if progress:
                            ach_data["progress"] = progress
                        incompleted.append(ach_data)
    with open(JSON_DIR + "IncompletedAchievements.json", 'w') as f:
        json.dump(incompleted, f, indent=2)
