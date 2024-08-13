import json
from utilities import *
import base64
from MyParser import *
import os
import zlib
from pathlib import Path
import time


def equal(a, b):
    if a == b:
        return True
    if isinstance(a, list):
        if isinstance(b, list):
            if len(a) != len(b):
                return False
            else:
                result = True
                for a_item, b_item in zip(a, b):
                    if not equal(a_item, b_item):
                        result = False
                        break
                return result
        else:
            return False
    elif isinstance(a, dict):
        if isinstance(b, dict):
            result = True
            for key in a.keys():
                if key in b.keys():
                    if not equal(a[key], b[key]):
                        result = False
                        break
                else:
                    if a[key]:
                        result = False
                        break
            for key in b.keys():
                if key not in a.keys():
                    if b[key]:
                        result = False
                        break
            return result
        else:
            return False
    else:
        return False


def file_decryptor(filename):
    fd = os.open(filename, os.O_RDONLY)
    status = os.fstat(fd)
    file = filename.rsplit("/", maxsplit=1)[-1]
    if status.st_size > 0:
        print(filename.rsplit("/", maxsplit=1)[-1])
        with open(filename, 'rb') as f:
            data = parse_payload(f.read())
            if 'data' not in data[0]["data"].keys():
                for key in data[0]["data"].keys():
                    if (key != '$type') and (key in guid_map.keys()):
                        key_data64 = data[0]["data"][key][0]
                        key_data = base64.b64decode(key_data64)
                        try:
                            data_decompressed = zlib.decompress(key_data, wbits=-zlib.MAX_WBITS)
                            path = DATA_DIR + "/../../" + guid_map[key]
                            path0 = DATA_DIR + "/../../" + guid_map[key].replace("/Data/", "/Data0/")
                            path1 = DATA_DIR + "/../../" + guid_map[key].replace("/Data/", "/Data1/")
                            path2 = DATA_DIR + "/../../" + guid_map[key].replace("/Data/", "/Data2/")
                            Path(os.path.dirname(path0)).mkdir(parents=True, exist_ok=True)
                            Path(os.path.dirname(path1)).mkdir(parents=True, exist_ok=True)
                            Path(os.path.dirname(path2)).mkdir(parents=True, exist_ok=True)
                            with open(path) as input_stream:
                                with open(path0, "w") as output_stream:
                                    json0 = json.load(input_stream, object_pairs_hook=guid_hook)
                                    json.dump(json0, output_stream, indent=2)
                            with open(path1, "w") as output_stream:
                                json1 = json.loads(data_decompressed, object_pairs_hook=guid_hook)
                                json.dump(json1, output_stream, indent=2)
                            with open(path2, "w") as output_stream:
                                json2 = json.loads(data_decompressed)
                                json.dump(json2, output_stream, indent=2)
                            # if not equal(json0, json1):
                            #     print(guid_map[key])
                        except:
                            print("Exception: File {0}, key {1}".format(file, key))
                            pass
                    elif key != '$type':
                        key_data64 = data[0]["data"][key][0]
                        key_data = base64.b64decode(key_data64)
                        try:
                            data_decompressed = zlib.decompress(key_data, wbits=-zlib.MAX_WBITS)
                            path1 = DATA_DIR + "/../Data1/" + key
                            path2 = DATA_DIR + "/../Data2/" + key
                            with open(path1, "w") as output_stream:
                                json.dump(json.loads(data_decompressed, object_pairs_hook=guid_hook), output_stream, indent=2)
                            with open(path2, "w") as output_stream:
                                json.dump(json.loads(data_decompressed), output_stream, indent=2)
                        except:
                            print("Exception: File {0}, key {1}".format(file, key))
                            pass

            else:
                data64 = data[0]["data"]["data"][0]
                data = base64.b64decode(data64)
                try:
                    data_decompressed = zlib.decompress(data, wbits=-zlib.MAX_WBITS)
                    if file in local_map.keys():
                        path = DATA_DIR + local_map[file]
                        path0 = DATA_DIR.replace("/Data/", "/Data0/") + local_map[file]
                        path1 = DATA_DIR.replace("/Data/", "/Data1/") + local_map[file]
                        path2 = DATA_DIR.replace("/Data/", "/Data2/") + local_map[file]
                        Path(os.path.dirname(path0)).mkdir(parents=True, exist_ok=True)
                        Path(os.path.dirname(path1)).mkdir(parents=True, exist_ok=True)
                        Path(os.path.dirname(path2)).mkdir(parents=True, exist_ok=True)
                        with open(path) as input_stream:
                            with open(path0, "w") as output_stream:
                                json0 = json.load(input_stream, object_pairs_hook=guid_hook)
                                json.dump(json0, output_stream, indent=2)
                        with open(path1, "w") as output_stream:
                            json1 = json.loads(data_decompressed, object_pairs_hook=guid_hook)
                            json.dump(json1, output_stream, indent=2)
                        with open(path2, "w") as output_stream:
                            json2 = json.loads(data_decompressed)
                            json.dump(json2, output_stream, indent=2)
                        # if not equal(json0, json1):
                        #     print(local_map[file])
                    else:
                        path1 = DATA_DIR + "/../Data1/" + file
                        with open(path1, "w") as output_stream:
                            json.dump(json.loads(data_decompressed, object_pairs_hook=guid_hook), output_stream,
                                      indent=2)
                except:
                    print("Exception: File {0}".format(file))
                    pass


def sequence_6():
    for cur_dir, dirs, files in os.walk(CACHE_DIR):
        for file in files:
            file_decryptor(cur_dir + "/" + file)


def sequence_8():
    path1 = DATA_DIR.replace("/Data/", "/Data1/")
    _, _, files = next(os.walk(path1))
    for file in files:
        file_name = file
        with open(path1 + file) as f:
            try:
                content = json.load(f)
                type = content["$type"].split(',')[0]
                if "devName" in content.keys():
                    file_name = content["devName"]
                elif "bgn" in content.keys():
                    file_name = content["bgn"]
                elif "rtbn" in content.keys():
                    file_name = content["rtbn"]
                elif "plt" in content.keys():
                    file_name = content["plt"]
                file_name = file_name.strip()
            except:
                continue
        if type in types_map.keys():
            if os.path.exists(path1 + types_map[type] + file_name):
                i = 1
                while os.path.exists(path1 + types_map[type] + file_name + "_" + str(i)):
                    i += 1
                file_name += "_" + str(i)
            os.rename(path1 + file, path1 + types_map[type] + file_name)


local_map = {
    "adcf": "Ads/AdsConfigurationData.json",
    "aepc": "AepConfiguration/AepConfigurationData.json",
    "aftuecfg": "FTUE/CallToActionReturnLabConfiguration.json",
    "bcfg": "BattleConfiguration/BattleConfiguration.json",
    "bpc": "BattlePass/BattlePassConfig.json",
    "bpxpd": "BattlePass/BattlePassXpData.json",
    "cco": "Country/CountryCode.json",
    "cmlcfg": "LevelIncrease/CreatureMaxLevelConfig.json",
#    "cmpgn": "",
    "cpcf": "Geolocation/Sanctuary/CaringPreferenceData/CaringPreferenceConfig.json",
    "crbocf": "CreatureBookmark/CreatureBookmarkConfig.json",
    "crdmcfg": "Geolocation/Sanctuary/CaringDiminishingValues/CaringDiminishingValuesConfig.json",
    "ctc": "CreatureTracker/CreatureTrackerConfig.json",
    "ctst": "Geolocation/Radar/Settings/ContinentSettings.json",
    "dcfg": "Geolocation/Battery/DroneConfigurationManager.json",
    "dlogbgld": "DailyLogin/BigGifts/BigGiftListData.json",
    "dloggcd": "DailyLogin/DailyLoginGridConfigData.json",
    "drviupcf": "Subscription/DroneVIPUpsellConfig.json",
    "frprtr": "Social/ReferralFriend/FriendshipProgressTracker.json",
    "frtrsuda": "Subscription/FreeTrialSubscriptionConfig.json",
    "gac": "GeolocArenaData/GeolocArenasConfiguration.json",
#    "glscd": "../Scripts/Alliance/GuildListSortingConfig.json",
    "gsc": "GameSettings/GameSettingsConfiguration.json",
    "hycrecfg": "HybridCreation/HybridCreationConfig.json",
    "iaec": "InAppEvent/InAppEventConfiguration.json",
    "invs": "Inventory/InventorySlots.json",
    "locda": "Localization/LocalizationData.json",
    "mfc": "MultiFusion/MultiFusionConfig.json",
    "mocfm": "Geolocation/MapObject/MapObjectConfigManager.json",
    "mv2scfg": "MissionV2/MissionV2SegmentConfig.json",
    "pec": "Experience/PlayerExperienceCurveDB.json",
    "pftuerdd": "PostFTUERequiredDinos/RequiredDinos.json",
    "rac": "Raid/RaidArenasConfiguration.json",
    "rdmcfg": "ReliableDirectMessage/ReliableDirectMessageConfiguration.json",
    "recy": "Recycling/RecyclingDataConfig.json",
    "refrcf": "Social/ReferralFriend/ReferredFriendConfig.json",
    "repada": "WelcomeBack/ReturnerPass/DefaultReturnerPass.json",
    "rlcd": "Raid/RaidLobbyChat/RaidLobbyChatData.json",
    "rmc": "Raid/Matchmaking/RaidMatchmakingConfig.json",
    "rst": "Geolocation/Radar/Settings/RadarSettings.json",
    "sdc": "Store/Config/DefaultStoreConfig.json",
    "sgcf": "Social/Gifting/Config/SocialGiftingConfig.json",
    "slc": "Geolocation/Sanctuary/Config/SanctuaryLevelConfig.json",
    "spu": "Global/SpeedUpResource/DefaultSpeedUpConfig.json",
    "stc": "Geolocation/Sanctuary/Config/SanctuaryConfig.json",
    "surl": "Social/MasterSocialUrls.json",
    "tc": "Tour/TourConfig.json",
    "trc": "Tournament/TournamentData/TournamentRulesConfiguration.json",
    "trcfg": "Tracking/TrackingConfig.json",
    "unco": "UnlockableSettings/UnlockableConfig.json",
    "vcfg": "Vote/VoteConfiguration.json",
    "wmc": "WeeklyMissionData/Configuration/WeeklyMissionConfigurationData.json",
    "wttd": "WinTierTableData/WinTierTableData.json"
}

types_map = {
    "RewLi": "Reward/RewardList/",
    "CaDa": "Campaign/",
    # "LoSeCo": "",
    "ParTyDa": "Geolocation/PartnerType/",
    "ByPlLe": "Reward/",
    #"GiLiSoCoDa": "",
    #"BrArCo": "",
    "InIm": "Inventory/Items/",
    "PveChDa": "PVEChallenge/",
    #"CoCfg": "",
    "RewInV2Da": "Reward/",
    #"AbIcCoCf": "",
    "RewPhe": "Reward/Pheromones/",
    #"GlCfg": "",
    "MiV2Da": "MissionV2/Missions/",
    "PbL": "Tournament/Rewards/PrizeBrackets/",
    "StItDa": "Store/",
    #"RcsCfg": "",
    "MoCfg": "Geolocation/MapObject/Config/",
    "RaTyBu": "Geolocation/Radar/RadarType/",
    "Tpd": "Tournament/TournamentData/",
    "RewLiWe": "Reward/",
    "RaBu": "Geolocation/Radar/RadarBucket/",
    # "LbDa": "", ?
    "TeGeStDa": "Tournament/Matchmaking/TeamGeneratorStaticData/",
    "MoPvE": "Geolocation/MapObject/Feature/",
    "Peda": "Geolocation/Radar/Scents/",
    "PhReDa": "Resource/Scents/",
    "MoFDsf": "Geolocation/MapObject/Feature/DinoSpawners/",
    "CrStDa": "CreaturesStaticData/",
    "CrAtDa": "CreaturesAttributesData/"
}

# start_time = time.perf_counter()
sequence_6()
# end_time = time.perf_counter()

sequence_8()
