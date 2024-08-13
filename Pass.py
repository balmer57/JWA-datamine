import re

from PIL import Image, ImageDraw, ImageFont
from utilities import *
import os
import urllib.request

IMG_DIR = BASE_DIR + "Img/"

with open(JSON_DIR + "events.json") as f:
    events_data = json.load(f)

found = False
battle_pass = None
for event in events_data["future"]["other"]:
    if event["n"] == "BattlePassEvent":
        found = True
        battle_pass = event
if not found:
    for event in events_data["ongoing"]["other"]:
        if event["n"] == "BattlePassEvent":
            found = True
            battle_pass = event
if not found:
    print("Pass event not found!")


def draw_text(img, coords, txt, size, anchor="mt"):
    drawing_context = ImageDraw.Draw(img)
    fnt = ImageFont.truetype("segoeuil.ttf", size=size)
    drawing_context.text(coords, txt, font=fnt, fill=(0, 0, 0, 255), stroke_width=2, anchor=anchor)
    drawing_context.text(coords, txt, font=fnt, fill=(255, 255, 255, 255), stroke_width=1, anchor=anchor)


def checkimg(name):
    icon_file_name = BASE_DIR + "Img/" + name.split("/")[-1]
    if not os.path.exists(icon_file_name):
        urllib.request.urlretrieve("https://cdn-gr-prod.ludia.net/jw2018/" + name, icon_file_name)


def add_reward(items, rew_guid, index):
    rew_json = get_json_from_guid(rew_guid)
    if rew_json:
        if "rl" not in rew_json.keys():
            print("Error")
        else:
            for rew in rew_json["rl"]:
                guid = rew["r"]["guid"].split()[0]
                if guid not in items.keys():
                    items[guid] = [0, 0, 0]
                q = rew["q"]["v"]
                items[guid][index] += q
    else:
        print(f"Unknown reward ({index})")


### Image dimensions ###
IMAGE_WIDTH = 1300
IMAGE_HEIGHT = 800
IMAGE_SIZE = (IMAGE_WIDTH, IMAGE_HEIGHT)
HEADER_AREA = 90
CREATURE_WIDTH = 90
CREATURE_HEIGHT = CREATURE_WIDTH * 250 // 207
CREATURES_PER_ROW = 6

if found:
    # Prepare data
    start_date = battle_pass["s"].split()[0]
    end_date = battle_pass["e"].split()[0]
    steps_data = battle_pass["d"]["steplist"]["steps"]
    items = dict()

    # Canvas
    collage = Image.new("RGBA", IMAGE_SIZE)

    # Background
    icon_file_name = BASE_DIR + "Img/" + battle_pass["d"]["themeimg"].split("/")[-1]
    if not os.path.exists(icon_file_name):
        urllib.request.urlretrieve("https://cdn-gr-test.ludia.net/jw2018/" + battle_pass["d"]["themeimg"], icon_file_name)
    calendar_icon = Image.open(icon_file_name).resize(IMAGE_SIZE)
    collage.paste(calendar_icon, (0, 0))

    # Remove comment
    if battle_pass["p"].startswith("["):
        battle_pass["p"] = re.sub(r"^\[[^]]+] *", "", battle_pass["p"])
    # Header
    draw_text(collage, (IMAGE_WIDTH // 2, 15), "{0}".format(battle_pass["p"], start_date, end_date), 30)
    draw_text(collage, (IMAGE_WIDTH // 2, 50), "{1} - {2}".format(battle_pass["p"], start_date, end_date), 30)

    # Steps
    drawing_context = ImageDraw.Draw(collage)
    for step_index in range(len(steps_data)):
        step = steps_data[step_index]
        rew_0 = step["r"][0]["rewp"]["rd"].split(":")[0]
        rew_1 = step["r"][1]["rewp"]["rd"].split(":")[0]
        add_reward(items, rew_0, 0)
        add_reward(items, rew_1, 1)

    # Grand pass
    grand = battle_pass["d"]["gppp"]["prd"]["rewp"]["rd"].split(":")[0]
    add_reward(items, grand, 2)

    creatures = list()
    other_imgs = list()
    other = list()
    tokens = [""]*3
    boosts = [""]*3
    for item_guid in items:
        reward = get_json_from_guid(item_guid)
        if not reward:
            other.append("Unknown reward")
            continue
        if reward["$type"].split(",")[0] == "RewDnDa":
            creature_dna = get_json_from_guid(reward["cr"]["guid"])
            creature_guid = creature_dna["cr"]["guid"]
            img = find_img(creature_guid)
            creatures.append([img, items[item_guid]])
        elif reward["$type"].split(",")[0] == "RewPhe":
            data = get_json_from_guid(reward["pd"]["guid"])
            pod_guid = data["pod"]["guid"]
            pod = get_json_from_guid(pod_guid)
            img_link = pod["pdcin"]
            checkimg(img_link)
            img = img_link.split("/")[-1]
            other_imgs.append([img, items[item_guid]])
            # other.append(data["devName"])
        elif reward["$type"].split(",")[0] == "RewCoDa":
            data = get_json_from_guid(reward["cltbda"]["guid"])
            other.append(data["devName"])
        elif reward["$type"].split(",")[0] == "RewCuDa":
            data = get_json_from_guid(reward["cur"]["guid"])
            sprite_guid = data["Sprite"]["guid"]
            img = asset_map[sprite_guid]["Path"].split("/")[-1]
            other_imgs.append([img, items[item_guid]])
        elif reward["$type"].split(",")[0] == "ReBaPaXpDa":
            data = get_json_from_guid(reward["xps"]["guid"])
            img_guid = data["i"]["guid"]
            img = asset_map[img_guid]["Path"].split("/")[-1]
            other_imgs.append([img, items[item_guid]])
        elif reward["$type"].split(",")[0] == "ReAEPDa":
            for i in range(3):
                if items[item_guid][i] > 0:
                    boosts[i] += reward["devName"].split("_")[2] + f' ({items[item_guid][i]})'
        elif reward["$type"].split(",")[0] == "ReAepReToDa":
            for i in range(3):
                if items[item_guid][i] > 0:
                    tokens[i] += reward["devName"].split("_")[2]
        else:
            print(reward["$type"])
    if "" != "".join(tokens):
        other_imgs.append(["Icon_Currency_Token_Generic.png", tokens])
    if "" != "".join(boosts):
        other_imgs.append(["Icon_Currency_Stats_Generic.png", boosts])

    # Drawing formatting. +1 for other_imgs
    row_count = (len(creatures) + CREATURES_PER_ROW - 1) // CREATURES_PER_ROW + 1
    y_offset = (IMAGE_HEIGHT - HEADER_AREA) // row_count

    # Draw creatures
    for creature_index in range(len(creatures)):
        creature = creatures[creature_index]

        creatures_in_row = CREATURES_PER_ROW
        if creature_index >= (len(creatures) // CREATURES_PER_ROW) * CREATURES_PER_ROW:
            creatures_in_row = len(creatures) - (len(creatures) // CREATURES_PER_ROW) * CREATURES_PER_ROW
        x_offset = (IMAGE_WIDTH - creatures_in_row * CREATURE_WIDTH) // creatures_in_row
        x_coord = x_offset // 2 + (x_offset + CREATURE_WIDTH) * (creature_index % CREATURES_PER_ROW)
        y_coord = HEADER_AREA + y_offset * (creature_index // CREATURES_PER_ROW)

        # Draw
        creature_img_path = BASE_DIR + "Img/" + creature[0]
        if os.path.exists(creature_img_path):
            creature_img = Image.open(creature_img_path).resize((CREATURE_WIDTH, CREATURE_HEIGHT))
            collage.alpha_composite(creature_img, (x_coord, y_coord))
        else:
            draw_text(collage, (x_coord, y_coord), creature[0], 16)

        if creature[1][0]:
            draw_text(collage, (x_coord + CREATURE_WIDTH // 2, y_coord + CREATURE_HEIGHT + 5), "Free: {0}".format(creature[1][0]), 18)
        if creature[1][1]:
            draw_text(collage, (x_coord + CREATURE_WIDTH // 2, y_coord + CREATURE_HEIGHT + 25), "Premium: {0}".format(creature[1][1]), 18)
        if creature[1][2]:
            draw_text(collage, (x_coord + CREATURE_WIDTH // 2, y_coord + CREATURE_HEIGHT + 45), "Grand: {0}".format(creature[1][2]), 18)

    # Other images
    for img_index in range(len(other_imgs)):
        img = other_imgs[img_index]
        imgs_in_row = len(other_imgs) + 2
        x_offset = (IMAGE_WIDTH - imgs_in_row * CREATURE_WIDTH) // imgs_in_row
        x_coord = x_offset // 2 + (x_offset + CREATURE_WIDTH) * (img_index % CREATURES_PER_ROW)
        y_coord = HEADER_AREA + y_offset * (row_count - 1)
        creature_img_path = BASE_DIR + "Img/" + img[0]

        # Draw
        if os.path.exists(creature_img_path):
            creature_img = Image.open(creature_img_path)
            height = CREATURE_HEIGHT
            if creature_img.height / CREATURE_HEIGHT < creature_img.width / CREATURE_WIDTH:
                height = int(creature_img.height / (creature_img.width / CREATURE_WIDTH))
            creature_img = creature_img.resize((CREATURE_WIDTH, height))
            collage.alpha_composite(creature_img, (x_coord, y_coord))
        else:
            draw_text(collage, (x_coord, y_coord), img, 16)

        if img[1][0]:
            draw_text(collage, (x_coord + CREATURE_WIDTH // 2, y_coord + CREATURE_HEIGHT + 5), "Free: {0}".format(img[1][0]), 18)
        if img[1][1]:
            draw_text(collage, (x_coord + CREATURE_WIDTH // 2, y_coord + CREATURE_HEIGHT + 25), "Premium: {0}".format(img[1][1]), 18)
        if img[1][2]:
            draw_text(collage, (x_coord + CREATURE_WIDTH // 2, y_coord + CREATURE_HEIGHT + 45), "Grand: {0}".format(img[1][2]), 18)

    # All other
    for other_index in range(len(other)):
        imgs_in_row = len(other_imgs) + 2
        x_offset = (IMAGE_WIDTH - imgs_in_row * CREATURE_WIDTH) // imgs_in_row
        x_coord = x_offset // 2 + int((x_offset + CREATURE_WIDTH) * (imgs_in_row - 1.5))
        y_coord = HEADER_AREA + y_offset * (row_count - 1) + other_index * 20

        draw_text(collage, (x_coord + CREATURE_WIDTH // 2, y_coord), other[other_index], 18)

    collage.show()
    collage.save(BASE_DIR + "plots/" + battle_pass["p"] + ".png")
