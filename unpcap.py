from pcapkit import extract
from MyParser import MyParser
import json
from utilities import *


def compare_by_s(x):
    if 's' in x.keys():
        return x['s']
    elif 'p' in x.keys():
        if 's' in x['p'].keys():
            return x['p']['s']
        elif 'p' in x['p'].keys():
            if 's' in x['p']['p'].keys():
                return x['p']['p']['s']
            elif 'id' in x['p']['p'].keys():
                return x['p']['p']['id'] - 10000
    return -10001


def extract_pcap(file):
    print("Extracting...")
    extraction = extract(fin=file, store=False, nofile=True, tcp=True, strict=True)

    strings = list()
    plain_strings = list()
    rereassembly = dict()
    # indices = dict()

    print("Reassembling...")
    for datagram in extraction.reassembly.tcp:
        if datagram.packet is not None:
            address_key = str(datagram.id["dst"][0]) + ":" + str(datagram.id["dst"][1]) + "-" + str(datagram.id["src"][0]) + ":" + str(datagram.id["src"][1])
            data = datagram.payload
            if address_key in rereassembly.keys():
                rereassembly[address_key] += data
                # indices[address_key] += list(datagram.index)
            else:
                rereassembly[address_key] = data
                # indices[address_key] = list(datagram.index)

    print("Parsing...")
    # strings_2 = list()
    for key in rereassembly.keys():
        data = rereassembly[key]
        if (data[0:1] == b'\x80') or (data[0:1] == b'\x88'):
            parser = MyParser()
            decoded_data = parser.decode(data)

            result = [x[0] for x in decoded_data if x]
            for x in result:
                if isinstance(x, dict):
                    x["connection_key"] = key
            if result:
                strings.append(result)
                # strings_2.append([indices[key], result])
        if data[0:1] == b'{':
            try:
                plain_json = json.loads(data)
                plain_strings.append(plain_json)
            except:
                pass

    print("Exporting...")
    flat_strings = [item for sublist in strings for item in sublist]
    # flat_strings.sort(key=compare_by_s)
    strings = flat_strings
    strings_decoded = json.loads(json.dumps(strings), object_pairs_hook=guid_hook)

    with open(JSON_DIR + "pcap_out.json", "w") as f:
        json.dump(strings, f, indent=2)

    with open(JSON_DIR + "pcap_out_decoded.json", "w") as f:
        json.dump(strings_decoded, f, indent=2)

    with open(JSON_DIR + "pcap_out_plain.json", "w") as f:
        json.dump(plain_strings, f, indent=2)

    return strings, strings_decoded
