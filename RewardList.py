import re

from PIL import Image, ImageDraw, ImageFont
from utilities import *
import os
import urllib.request

IMG_DIR = BASE_DIR + "Img/"

with open(JSON_DIR + "events.json") as f:
    events_data = json.load(f)

found = False
reward_list = None
for event in events_data["future"]["other"]:
    if event["n"] == "LoginCalendarEvent":
        found = True
        reward_list = event
if not found:
    for event in events_data["ongoing"]["other"]:
        if event["n"] == "LoginCalendarEvent":
            found = True
            reward_list = event
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


### Image dimensions ###
IMAGE_WIDTH = 1200
IMAGE_HEIGHT = 700
IMAGE_SIZE = (IMAGE_WIDTH, IMAGE_HEIGHT)
HEADER_AREA = 100
CREATURE_WIDTH = 80
CREATURE_HEIGHT = CREATURE_WIDTH * 250 // 207
CREATURES_PER_ROW = 8

if found:
    # Prepare data
    start_date = reward_list["s"].split()[0]
    end_date = reward_list["e"].split()[0]
    steps_data = reward_list["d"]["cslo"]["sl"]
    items = dict()

    # Canvas
    collage = Image.new("RGBA", IMAGE_SIZE)

    # Background
    icon_file_name = BASE_DIR + "Img/" + reward_list["d"]["bip"].split("/")[-1]
    if not os.path.exists(icon_file_name):
        urllib.request.urlretrieve("https://cdn-gr-prod.ludia.net/jw2018/" + reward_list["d"]["bip"], icon_file_name)
    calendar_icon = Image.open(icon_file_name).resize(IMAGE_SIZE)
    collage.paste(calendar_icon, (0, 0))

    # Remove comment
    if reward_list["p"].startswith("["):
        reward_list["p"] = re.sub(r"^\[[^]]+] *", "", reward_list["p"])
    # Header
    draw_text(collage, (IMAGE_WIDTH // 2, 15), "{0}".format(reward_list["p"], start_date, end_date), 36)
    draw_text(collage, (IMAGE_WIDTH // 2, 55), "{1} - {2}".format(reward_list["p"], start_date, end_date), 36)

    # Steps
    drawing_context = ImageDraw.Draw(collage)
    for step_index in range(len(steps_data)):
        step = steps_data[step_index]
        rd = step["cro"]["rd"]
        if "rtd" in rd.keys():
            rew = rd["rtd"].split(":")[0]
        else:
            rew = rd["rd"].split(":")[0]
        amount = rd["a"] if "a" in rd.keys() else 1
        if rew in items.keys():
            items[rew] += amount
        else:
            items[rew] = amount
    creatures = list()
    other_imgs = list()
    other = list()
    tokens = ""
    for item_guid in items:
        reward = get_json_from_guid(item_guid)
        if not reward:
            other.append("Unknown reward")
            continue
        if reward["$type"].split(",")[0] == "CrDNARe":
            creature_guid = reward["cr"]["guid"]
            img = find_img(creature_guid)
            creatures.append([img, items[item_guid]])
        elif reward["$type"].split(",")[0] == "PhReDa":
            pod_guid = reward["pod"]["guid"]
            pod = get_json_from_guid(pod_guid)
            img_link = pod["pdcin"]
            checkimg(img_link)
            img = img_link.split("/")[-1]
            creatures.append([img, reward["devName"]])
            # other_imgs.append([img, reward["devName"]])
            # other.append(reward["devName"])
        elif reward["$type"].split(",")[0] == "CuReDa":
            sprite_guid = reward["Sprite"]["guid"]
            img = asset_map[sprite_guid]["Path"].split("/")[-1]
            other_imgs.append([img, items[item_guid]])
        elif reward["$type"].split(",")[0] == "RewInV2Da":
            img = reward["imgn"]
            checkimg(img)
            other_imgs.append([img.split("/")[-1], items[item_guid]])
        else:
            print(reward["$type"])
    if "" != tokens:
        other_imgs.append(["Icon_Currency_Token_Generic.png", tokens])

    # Drawing formatting
    row_count = (len(creatures) + CREATURES_PER_ROW - 1) // CREATURES_PER_ROW
    row_count += (len(other_imgs) + CREATURES_PER_ROW - 1) // CREATURES_PER_ROW
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

        draw_text(collage, (x_coord + CREATURE_WIDTH // 2, y_coord + CREATURE_HEIGHT + 5), "{0}".format(creature[1]), 18)

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

        draw_text(collage, (x_coord + CREATURE_WIDTH // 2, y_coord + CREATURE_HEIGHT + 5), "{0}".format(img[1]), 18)

    # All other
    for other_index in range(len(other)):
        imgs_in_row = len(other_imgs) + 2
        x_offset = (IMAGE_WIDTH - imgs_in_row * CREATURE_WIDTH) // imgs_in_row
        x_coord = x_offset // 2 + int((x_offset + CREATURE_WIDTH) * (imgs_in_row - 1.5))
        y_coord = HEADER_AREA + y_offset * (row_count - 1) + other_index * 20

        draw_text(collage, (x_coord + CREATURE_WIDTH // 2, y_coord), other[other_index], 18)

    collage.show()
    collage.save(BASE_DIR + "plots/" + reward_list["p"] + ".png")
