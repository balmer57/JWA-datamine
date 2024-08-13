from utilities import *

with open(JSON_DIR + "pcap_out.json") as f:
    strings = json.load(f)
    strings_decoded = json.loads(json.dumps(strings), object_pairs_hook=guid_hook)

for message in strings:
    if 'p' in message['p'].keys():
        if 'mk' in message['p']['p'].keys():
            if message['p']['p']['mk'] == "j.sbspo":
                sancts = message['p']['p']['msg']['sancl']
                sancts.sort(key=lambda x: x["slv"], reverse=True)
                for sanc in sancts:
                    print("Sanctuary: {} points ({}, {})".format(sanc["slv"], sanc["slt"][:8], sanc["sln"][:8]))
                    enc_num = 0
                    for enc in sanc["sel"]:
                        enc_num += 1
                        for creature in enc["edl"]:
                            UTC_tz = timezone(timedelta(0), name='UTC')
                            my_tz = timezone(timedelta(hours=3), name='MSK')
                            time = datetime.fromtimestamp(creature["cat"]).astimezone(tz=my_tz)
                            print("  {}  {}  {}".format(enc_num, time.strftime('%d.%m %H:%M:%S'), find_name(creature["cid"])))
