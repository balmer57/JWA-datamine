import re

from PIL import Image, ImageDraw, ImageFont
from utilities import *
import os
import urllib.request

IMG_DIR = BASE_DIR + "Img/"

with open(JSON_DIR + "events.json") as f:
    events_data = json.load(f)

found = False
creature_list = None
for event in events_data["future"]["other"]:
    if event["n"] == "BrawlEvent":
        found = True
        creature_list = event
if not found:
    for event in events_data["ongoing"]["other"]:
        if event["n"] == "BrawlEvent":
            found = True
            creature_list = event
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


BACK_IMG = "NewsCenter/NC2_Brawl_Upcoming.jpg"
### Image dimensions ###
IMAGE_WIDTH = 1200
IMAGE_HEIGHT = 700
IMAGE_SIZE = (IMAGE_WIDTH, IMAGE_HEIGHT)
HEADER_AREA = 100
CREATURE_WIDTH = 110
CREATURE_HEIGHT = CREATURE_WIDTH * 250 // 207
CREATURES_PER_ROW = 6

if found:
    # Prepare data
    start_date = creature_list["s"].split()[0]
    end_date = creature_list["e"].split()[0]
    steps_data = creature_list["d"]["tcrdd"]["crl"]
    items = dict()

    # Canvas
    collage = Image.new("RGBA", IMAGE_SIZE)

    # Background
    icon_file_name = BASE_DIR + "Img/" + BACK_IMG.split("/")[-1]
    if not os.path.exists(icon_file_name):
        urllib.request.urlretrieve("https://cdn-gr-prod.ludia.net/jw2018/" + BACK_IMG, icon_file_name)
    calendar_icon = Image.open(icon_file_name).resize(IMAGE_SIZE)
    collage.paste(calendar_icon, (0, 0))

    # Remove comment
    if creature_list["p"].startswith("["):
        creature_list["p"] = re.sub(r"^\[[^]]+] *", "", creature_list["p"])
    creature_list["p"] = re.sub(r"[|*]", "", creature_list["p"])
    # Header
    draw_text(collage, (IMAGE_WIDTH // 2, 15), "{0}".format(creature_list["p"], start_date, end_date), 36)
    draw_text(collage, (IMAGE_WIDTH // 2, 55), "{1} - {2}".format(creature_list["p"], start_date, end_date), 36)

    # Steps
    drawing_context = ImageDraw.Draw(collage)
    creatures = list()
    for step_index in range(len(steps_data)):
        step = steps_data[step_index]
        for creature_guid in step["cli"]:
            img = find_img(creature_guid.split()[0])
            creatures.append(img)

    # Drawing formatting
    row_count = (len(creatures) + CREATURES_PER_ROW - 1) // CREATURES_PER_ROW
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
        creature_img_path = BASE_DIR + "Img/" + creature
        if os.path.exists(creature_img_path):
            creature_img = Image.open(creature_img_path).resize((CREATURE_WIDTH, CREATURE_HEIGHT))
            collage.alpha_composite(creature_img, (x_coord, y_coord))
        else:
            draw_text(collage, (x_coord, y_coord), creature, 16)

    collage.show()
    collage.save(BASE_DIR + "plots/" + creature_list["p"] + ".png")
