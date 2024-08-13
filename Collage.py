from PIL import Image, ImageDraw, ImageFont
from utilities import *
import os
import urllib.request
import datetime

IMG_DIR = BASE_DIR + "Img/"
BACK_IMG = "NewsCenter/WeeklyCalendar_generic_NC.jpg"
# BACK_IMG = "NewsCenter/NC2_WeeklyCalendar_SwapClash.jpg"
EVENT_NAME = "SwapClash"

with open(JSON_DIR + "events.json") as f:
    events_data = json.load(f)


def draw_text(img, coords, txt, size):
    drawing_context = ImageDraw.Draw(img)
    fnt = ImageFont.truetype("segoeuil.ttf", size=size)
    drawing_context.text(coords, txt, font=fnt, fill=(0, 0, 0, 255), stroke_width=2, anchor="mt")
    drawing_context.text(coords, txt, font=fnt, fill=(255, 255, 255, 255), stroke_width=1, anchor="mt")


def tries_word(i):
    if not isinstance(i, int):
        i = 0
    i = i % 20
    if i == 1:
        return "попытка"
    elif 2 <= i <= 4:
        return "попытки"
    else:
        return "попыток"


### Image dimensions ###
IMAGE_WIDTH = 1400
IMAGE_HEIGHT = 730
IMAGE_SIZE = (IMAGE_WIDTH, IMAGE_HEIGHT)
HEADER_AREA = 110
RECT_OFFSET = 20
COLUMN_WIDTH = (IMAGE_WIDTH - 2 * RECT_OFFSET) // 7
CREATURE_WIDTH = 90
CREATURE_HEIGHT = CREATURE_WIDTH * 250 // 207
INC_WIDTH = 50
INC_HEIGHT = INC_WIDTH * 620 // 458
HEADER_IMAGE_WIDTH = 75
HEADER_IMAGE_HEIGHT = 90
INC_PER_LINE = 3


def method_1(calendar):
    # Prepare data
    calendar_name = calendar["p"].replace(" ", "_").replace("|", "")
    start_date = calendar["s"].split()[0]
    end_date = calendar["e"].split()[0]
    calendar_data = calendar["d"]["nc"][1]["ncwc"]
    days = ["cdw", "cdth", "cdf", "cdsa", "cdsu", "cdm", "cdtu"]
    day_names = ["Ср", "Чт", "Пт", "Сб", "Вс", "Пн", "Вт"]

    # Background
    icon_file_name = BASE_DIR + "Img/" + calendar["d"]["bico"].split("/")[-1]
    if not os.path.exists(icon_file_name):
        urllib.request.urlretrieve("https://cdn-gr-prod.ludia.net/jw2018/" + calendar["d"]["bico"], icon_file_name)
    calendar_icon = Image.open(icon_file_name).resize(IMAGE_SIZE)

    collage = Image.new("RGBA", IMAGE_SIZE)
    collage.paste(calendar_icon, (0, 0))

    # Rectangle
    newImg = Image.new("RGBA", IMAGE_SIZE)
    drawing_context = ImageDraw.Draw(newImg)
    drawing_context.rectangle([RECT_OFFSET, HEADER_AREA + RECT_OFFSET, IMAGE_WIDTH - RECT_OFFSET, IMAGE_HEIGHT - RECT_OFFSET], fill="#80808060", outline="#ffffffff")
    collage.alpha_composite(newImg)

    # Header
    draw_text(collage, (IMAGE_WIDTH // 2, 15), "{0} - {1}".format(start_date, end_date), 36)

    # Days
    drawing_context = ImageDraw.Draw(collage)
    merge = 1
    creatures = []
    for day_index in range(7):
        # Get creatures
        day = days[day_index]
        prev_creatures = creatures
        creatures = calendar_data[day]["cdsdcl"]["rdn"]
        incubators = [x["ip"] for x in calendar_data[day]["cdseta"]["ser"]]
        treasure = calendar_data[day]["cdtci"]["ncip"]
        if treasure:
            incubators.append(treasure)
        next_creatures = calendar_data[days[day_index + 1]]["cdsdcl"]["rdn"] if day_index < 6 else []
        cpr = 1 + len(creatures) // 3

        # Day
        draw_text(collage, (RECT_OFFSET + day_index * COLUMN_WIDTH + COLUMN_WIDTH // 2, HEADER_AREA + RECT_OFFSET + 15), day_names[day_index], 36)

        # Lines
        if creatures != prev_creatures:
            drawing_context.line((RECT_OFFSET + day_index * COLUMN_WIDTH, HEADER_AREA + RECT_OFFSET, RECT_OFFSET + day_index * COLUMN_WIDTH, IMAGE_HEIGHT - RECT_OFFSET))

        # Creatures
        if creatures != next_creatures:
            creature_index = 0
            start_day_index = day_index - merge + 1
            for creature in creatures:
                creature_file_name = BASE_DIR + "Img/Img_" + creature + ".png"
                if not os.path.exists(creature_file_name):
                    creature_file_name = BASE_DIR + "Img/" + creature + "_Img.png"
                delta = (COLUMN_WIDTH * merge - CREATURE_WIDTH * cpr) // cpr
                x_coord = RECT_OFFSET + (start_day_index * COLUMN_WIDTH) + (delta // 2) + (creature_index % cpr) * (CREATURE_WIDTH + delta)
                # x_coord = shift + RECT_OFFSET + day_index * COLUMN_WIDTH + ((COLUMN_WIDTH - CREATURE_WIDTH) // 2 if cpr == 1 else ((creature_index % cpr) * (CREATURE_WIDTH + 5) + 5))
                y_coord = HEADER_AREA + RECT_OFFSET + 85 + (CREATURE_HEIGHT + 5) * (creature_index // cpr)
                if os.path.exists(creature_file_name):
                    creature_img = Image.open(creature_file_name).resize((CREATURE_WIDTH, CREATURE_HEIGHT))
                    collage.alpha_composite(creature_img, (x_coord, y_coord))
                else:
                    draw_text(collage, (x_coord, y_coord), creature, 16)
                creature_index += 1

            # Print tries
            q_data = calendar_data[days[day_index]]["cdsdb"]["tv"]
            q_list = []
            for q in q_data:
                if q.startswith("IDS"):
                    q_list.append(q[4:])
                else:
                    q_list.append(q)
            quantity = " + ".join(q_list)
            draw_text(collage,
                      ((merge * COLUMN_WIDTH // 2) + RECT_OFFSET + start_day_index * COLUMN_WIDTH, HEADER_AREA + RECT_OFFSET + 55),
                      quantity + " " + tries_word(int(q_list[-1])), 24)

            # Reset shift
            merge = 1
        else:
            merge += 1

        # Incubators
        inc_lines = (len(incubators) - 1) // INC_PER_LINE
        for i in range(len(incubators)):
            inc = incubators[i]
            inc_filename = BASE_DIR + "Img/" + inc.split("/")[-1]
            if not os.path.exists(inc_filename):
                urllib.request.urlretrieve("https://cdn-gr-prod.ludia.net/jw2018/" + inc, inc_filename)
            if os.path.exists(inc_filename):
                inc_img = Image.open(inc_filename)
                if inc_img.height * 2 < inc_img.width:
                    inc_img = inc_img.crop([inc_img.width // 4, 0, 3 * inc_img.width // 4, inc_img.height])
                inc_img = inc_img.resize((INC_WIDTH, inc_img.height * INC_WIDTH // inc_img.width))
                x_coord = RECT_OFFSET + day_index * COLUMN_WIDTH + (INC_WIDTH + 5) * (i % INC_PER_LINE) + 5
                y_coord = IMAGE_HEIGHT - RECT_OFFSET - (inc_img.height + INC_HEIGHT) // 2 - 15 - (INC_HEIGHT + 10) * (i // INC_PER_LINE)
                if inc_img.mode != 'RGBA':
                    inc_img = inc_img.convert('RGBA')
                collage.alpha_composite(inc_img, (x_coord, y_coord))

    collage.show()
    collage.save(BASE_DIR + "plots/" + calendar_name + ".png")


def method_2(ESD, battles, TH, AM, HP):
    # Prepare data
    start_date = ESD[0]["s"].split()[0]
    end_date = ESD[-1]["e"].split()[0]
    calendar_name = start_date.replace(".", "_")  # + "-" + end_date.replace(".", "_")

    # Background
    icon_file_name = BASE_DIR + "Img/" + BACK_IMG.split("/")[-1]
    if not os.path.exists(icon_file_name):
        urllib.request.urlretrieve("https://cdn-gr-prod.ludia.net/jw2018/" + BACK_IMG, icon_file_name)
    calendar_icon = Image.open(icon_file_name).resize(IMAGE_SIZE)

    collage = Image.new("RGBA", IMAGE_SIZE)
    collage.paste(calendar_icon, (0, 0))

    # Rectangle
    newImg = Image.new("RGBA", IMAGE_SIZE)
    drawing_context = ImageDraw.Draw(newImg)
    drawing_context.rectangle([RECT_OFFSET, HEADER_AREA + RECT_OFFSET, IMAGE_WIDTH - RECT_OFFSET, IMAGE_HEIGHT - RECT_OFFSET], fill="#80808080", outline="#ffffffff")
    collage.alpha_composite(newImg)

    # Header
    draw_text(collage, (180, 25), "{0} - {1}".format(start_date, end_date), 30)
    draw_text(collage, (180, 75), EVENT_NAME, 30)

    # HP
    if HP:
        creature = HP["d"]["nc"][2]["clg"]["rdn"][0]
        HP_creature_name = BASE_DIR + "Img/Img_" + creature + ".png"
        if not os.path.exists(HP_creature_name):
            HP_creature_name = BASE_DIR + "Img/" + creature + "_Img.png"
        creature_img = Image.open(HP_creature_name).resize((HEADER_IMAGE_WIDTH, HEADER_IMAGE_HEIGHT))
        collage.alpha_composite(creature_img, (380, 10))
        draw_text(collage, (380 + 38, HEADER_IMAGE_HEIGHT + 20), "Hybrid pursuit".format(start_date, end_date), 15)

    # AM
    defence_guid = AM["d"]["btrl"][-1].split()[0]
    def_list = get_json_from_guid(defence_guid)
    rew_list = [x["r"]["guid"] for x in def_list["gar"]]
    dna_list = [get_json_from_guid(x)["cr"]["guid"] for x in rew_list]
    defence = [get_json_from_guid(x)["devName"] for x in dna_list]

    explore_guid = AM["d"]["gtrl"][-1].split()[0]
    def_list = get_json_from_guid(explore_guid)
    rew_list = [x["r"]["guid"] for x in def_list["gar"]]
    dna_list = [get_json_from_guid(x)["cr"]["guid"] for x in rew_list]
    explore = [get_json_from_guid(x)["devName"] for x in dna_list]

    for i in range(len(defence)):
        creature_file_name = BASE_DIR + "Img/Img_" + defence[i] + ".png"
        if not os.path.exists(creature_file_name):
            creature_file_name = BASE_DIR + "Img/" + defence[i] + "_Img.png"
        creature_img = Image.open(creature_file_name).resize((HEADER_IMAGE_WIDTH, HEADER_IMAGE_HEIGHT))
        collage.alpha_composite(creature_img, (510 + (HEADER_IMAGE_WIDTH + 5) * i, 10))
    draw_text(collage, (510 + ((HEADER_IMAGE_WIDTH + 5) * 5) // 2, HEADER_IMAGE_HEIGHT + 20),
              "Defence alliance mission".format(start_date, end_date), 15)

    for i in range(len(explore)):
        creature_file_name = BASE_DIR + "Img/Img_" + explore[i] + ".png"
        if not os.path.exists(creature_file_name):
            creature_file_name = BASE_DIR + "Img/" + explore[i] + "_Img.png"
        creature_img = Image.open(creature_file_name).resize((HEADER_IMAGE_WIDTH, HEADER_IMAGE_HEIGHT))
        collage.alpha_composite(creature_img, (960 + (HEADER_IMAGE_WIDTH + 5) * i, 10))
    draw_text(collage, (960 + ((HEADER_IMAGE_WIDTH + 5) * 5) // 2, HEADER_IMAGE_HEIGHT + 20),
              "Exploration alliance mission".format(start_date, end_date), 15)

    # Days
    slots = list()
    slot_length = list()
    creature_slots = list()
    quantities = list()
    for day_index in range(7):
        slots.append(list())
        slot_length.append(list())
        creature_slots.append(list())
        quantities.append(list())
        day_names = ["Ср", "Чт", "Пт", "Сб", "Вс", "Пн", "Вт"]
        draw_text(collage, (RECT_OFFSET + day_index * COLUMN_WIDTH + COLUMN_WIDTH // 2, HEADER_AREA + RECT_OFFSET + 15),
                  day_names[day_index], 36)

    # Prepare creatures
    for esd_event in ESD:
        creatures_guid = find_guid_by_name("RB_" + esd_event["n"])
        if creatures_guid:
            creatures_json = get_json_from_guid(creatures_guid)
            creatures_guids = [x["dino"]["guid"].split()[0] for x in creatures_json["dinow"]]
            ESD_start_day = (esd_event["as"] - ESD[0]["as"]) // 86400000
            ESD_length = (esd_event["ae"] - esd_event["as"]) // 86400000
            if len(creature_slots[i]) % 2 == 1:
                creature_slots[i].append("")
            for i in range(ESD_start_day, ESD_start_day + ESD_length):
                creature_slots[i].extend([get_json_from_guid(guid)["dn"] for guid in creatures_guids])
        else:
            print("Error! {0} not found!".format("RB_" + esd_event["n"]))

    # Creatures
    drawing_context = ImageDraw.Draw(collage)
    for esd_event in ESD:
        creatures_guid = find_guid_by_name("RB_" + esd_event["n"])
        if not creatures_guid:
            print("Error! RB_" + esd_event["n"] + " not found!")
            continue
        creatures_json = get_json_from_guid(creatures_guid)
        creatures_guids = [x["dino"]["guid"].split()[0] for x in creatures_json["dinow"]]
        creatures = [get_json_from_guid(guid)["dn"] for guid in creatures_guids]

        ESD_start_day = (esd_event["as"] - ESD[0]["as"]) // 86400000
        ESD_length = (esd_event["ae"] - esd_event["as"]) // 86400000
        cpr = 2 if len(creature_slots[ESD_start_day]) > 3 else 1
        shift = (ESD_length - 1) * COLUMN_WIDTH // 2

        # Lines
        drawing_context.line((RECT_OFFSET + ESD_start_day * COLUMN_WIDTH, HEADER_AREA + RECT_OFFSET,
                              RECT_OFFSET + ESD_start_day * COLUMN_WIDTH, IMAGE_HEIGHT - RECT_OFFSET))

        # Paste creature pictures
        creature_index = creature_slots[ESD_start_day].index(creatures[0])
        for creature in creatures:
            creature_file_name = BASE_DIR + "Img/Img_" + creature + ".png"
            if not os.path.exists(creature_file_name):
                creature_file_name = BASE_DIR + "Img/" + creature + "_Img.png"
            x_coord = shift + RECT_OFFSET + ESD_start_day * COLUMN_WIDTH + (
                (COLUMN_WIDTH - CREATURE_WIDTH) // 2 if cpr == 1 else ((creature_index % cpr) * (CREATURE_WIDTH + 5) + 5))
            y_coord = HEADER_AREA + RECT_OFFSET + 85 + (CREATURE_HEIGHT + 5) * (creature_index // cpr)
            if os.path.exists(creature_file_name):
                creature_img = Image.open(creature_file_name).resize((CREATURE_WIDTH, CREATURE_HEIGHT))
                collage.alpha_composite(creature_img, (x_coord, y_coord))
            else:
                draw_text(collage, (x_coord, y_coord), creature, 16)
            creature_index += 1

        # Prepare tries
        guid = find_guid_by_name("DS_" + esd_event["n"])
        if guid:
            tries = get_json_from_guid(guid)
            quantity = tries["hlc"]
        else:
            quantity = "?"
        quantities[ESD_start_day].append([shift, quantity])

    # Print tries
    for q_index in range(len(quantities)):
        q = quantities[q_index]
        if not q:
            continue
        shift = q[0][0]
        text = " + ".join([str(x) for x in [y[1] for y in q]])
        draw_text(collage,
                  (shift + RECT_OFFSET + q_index * COLUMN_WIDTH + COLUMN_WIDTH // 2, HEADER_AREA + RECT_OFFSET + 55),
                  text + " " + tries_word(q[-1][1]), 24)

    # Battles
    for battle in battles:
        pcc = get_json_from_guid(battle["d"]["poic"].split()[0])
        if pcc:
            pcf = get_json_from_guid(pcc["fl"][1]["guid"].split()[0])
            pve = get_json_from_guid(pcf["pve"]["guid"].split()[0])
            incubator_json = get_json_from_guid(pve["pvecst"][-1]["pvesr"][0]["guid"].split()[0])
            battle_len = len(pve["pvecst"])
            if incubator_json:
                if "imgn" in incubator_json.keys():
                    incubator = incubator_json["imgn"]
                elif incubator_json["cltbda"]["TypeName"] == "BaDa":
                    incubator = "NewsCenter/Icons_PVE_Badge.png"
                elif incubator_json["cltbda"]["TypeName"] == "EmDa":
                    incubator = "NewsCenter/Icons_PVE_Emote.png"
                elif incubator_json["cltbda"]["TypeName"] == "TtDa":
                    incubator = "NewsCenter/Img_Title_Reward.png"
                else:
                    incubator = ""

            day_index = (battle["as"] - ESD[0]["as"]) // 86400000
            if incubator:
                slots[day_index].append(incubator)
                slot_length[day_index].append(battle_len)
            else:
                pass
        else:
            print("guid {0} unknown".format(battle["d"]["poic"].split()[0]))

    for event in TH:
        TH_start_day = (event["as"] - ESD[0]["as"]) // 86400000
        TH_length = (event["ae"] - event["as"]) // 86400000
        if 0 < event["ae"] - event["as"] < 86400000:
            TH_length = 1
        for i in range(TH_start_day, TH_start_day + TH_length):
            if "NewsCenter/NC_Body_TreasureChaseGeneric.jpg" not in slots[i]:
                slots[i].append("NewsCenter/NC_Body_TreasureChaseGeneric.jpg")
                slot_length[i].append(0)

    for day_index in range(7):
        # Incubators
        incubators = slots[day_index]
        lengths = slot_length[day_index]
        top_line = min(len(incubators), max((len(incubators) + 1) // 2, 2))
        bottom_line = len(incubators) - top_line
        for i in range(len(incubators)):
            inc = incubators[i]
            # Load img
            inc_filename = BASE_DIR + "Img/" + inc.split("/")[-1]
            if not os.path.exists(inc_filename):
                urllib.request.urlretrieve("https://cdn-gr-prod.ludia.net/jw2018/" + inc, inc_filename)
            if os.path.exists(inc_filename) and os.path.isfile(inc_filename):
                # Resize img
                inc_img = Image.open(inc_filename)
                if inc_img.height * 2 < inc_img.width:
                    inc_img = inc_img.crop([inc_img.width // 4, 0, 3 * inc_img.width // 4, inc_img.height])
                inc_img = inc_img.resize((INC_WIDTH, inc_img.height * INC_WIDTH // inc_img.width))
                # Coords
                line_length = bottom_line if (i >= top_line) else top_line
                space = (COLUMN_WIDTH - INC_WIDTH * line_length) // (line_length + 2)
                x_coord = RECT_OFFSET + day_index * COLUMN_WIDTH + 3 * space // 2 + (INC_WIDTH + space) * (i % line_length)
                if bottom_line > 0:
                    line_index = 1 if i >= top_line else 0
                    y_coord = IMAGE_HEIGHT - RECT_OFFSET - (inc_img.height + INC_HEIGHT) // 2 - 15 - (INC_HEIGHT + 10) * (1 - line_index)
                else:
                    y_coord = IMAGE_HEIGHT - RECT_OFFSET - inc_img.height // 2 - INC_HEIGHT - 20
                # Paste img
                if inc_img.mode != 'RGBA':
                    inc_img = inc_img.convert('RGBA')
                collage.alpha_composite(inc_img, (x_coord, y_coord))
                if lengths[i] > 0:
                    draw_text(collage, (x_coord + INC_WIDTH // 2, y_coord + INC_HEIGHT - 10), str(lengths[i]), 12)

    collage.show()
    collage.save(BASE_DIR + "plots/" + calendar_name + ".png")


found = False
for event in events_data["future"]["News"]:
    if (event["n"] == "NCGenericEvent") and ("Weekly Cal" in event["p"]):
        found = True
        method_1(event)
found = False
if not found:
    start_date = 1678287600 + ((datetime.datetime.now().timestamp() - 1678287600) // (86400*7) + 1) * (86400*7)
    # start_date -= (86400*7)
    start_date *= 1000
    end_date = start_date + 86400*7*1000
    week_end_date = start_date + 86400*4*1000
    TH = []
    AM = None
    HP = None
    events_data_all = dict()
    for key in events_data["ongoing"].keys():
        events_data_all[key] = events_data["ongoing"][key] + events_data["future"][key]
    for event in events_data["ongoing"]["other"]:
        if event["n"] == "AllianceMissionEvent":
            AM = event
    for event in events_data_all["other"]:
        if event["n"].startswith("TH_") or event["n"].startswith("TreasureHunt_"):
            if (event["as"] >= start_date) and (event["as"] < end_date):
                TH.append(event)
        if event["n"] == "AllianceMissionEvent":
            if (event["as"] >= start_date) and (event["as"] < week_end_date):
                AM = event
    for event in events_data_all["News"]:
        if event["p"].startswith("FUSE"):
            if (event["as"] >= start_date) and (event["as"] < end_date):
                HP = event
                break
    ESD = [x for x in events_data_all["ESD"] if (x["as"] >= start_date) and (x["as"] < end_date)]
    battles = [x for x in events_data_all["battle"] if (x["as"] >= start_date) and (x["as"] < end_date)]
    TH = [x for x in TH if x["as"] >= start_date]
    method_2(ESD, battles, TH, AM, HP)
