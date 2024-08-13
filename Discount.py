from PIL import Image, ImageDraw, ImageFont
from utilities import *
import os
import urllib.request

IMG_DIR = BASE_DIR + "Img/"
CUSTOM_BACK = "FeatureNews/FN_Generic_ReleaseNotes2.jpg"

with open(JSON_DIR + "events.json") as f:
    events_data = json.load(f)

found = False
discount_event = None
for event in events_data["future"]["other"]:
    if event["n"] == "CreatureCostReductionEvent":
        found = True
        discount_event = event
if not found:
    print("Discount event not found!")


def find_img(guid):
    fname = None
    if guid in guid_map.keys():
        entry = guid_map[guid]
        fname = DATA_DIR + "/../../" + entry
    elif os.path.exists(DATA_DIR + "/../Data1/" + guid):
        fname = DATA_DIR + "/../Data1/" + guid
    if fname:
        with open(fname) as f:
            creature = json.load(f)
            img_guid = creature["i"]["guid"]
            return asset_map[img_guid]["Path"]
    else:
        return ""


def draw_text(img, coords, txt, size, anchor="mt"):
    drawing_context = ImageDraw.Draw(img)
    fnt = ImageFont.truetype("segoeuil.ttf", size=size)
    drawing_context.text(coords, txt, font=fnt, fill=(0, 0, 0, 255), stroke_width=2, anchor=anchor)
    drawing_context.text(coords, txt, font=fnt, fill=(255, 255, 255, 255), stroke_width=1, anchor=anchor)


### Image dimensions ###
IMAGE_WIDTH = 600
IMAGE_HEIGHT = 900
IMAGE_SIZE = (IMAGE_WIDTH, IMAGE_HEIGHT)
IMAGE2_SIZE = (IMAGE_WIDTH*4//5, IMAGE_HEIGHT*4//5)
HEADER_AREA = 60
CREATURE_WIDTH = 90
CREATURE_HEIGHT = CREATURE_WIDTH * 250 // 207
STAGE_NAME_OFFSET = 260
CREATURES_PER_ROW = 4

if found:
    # Prepare data
    event_name = discount_event["p"]
    start_date = discount_event["s"].split()[0]
    end_date = discount_event["e"].split()[0]
    pool = discount_event["d"]["cfl"]

    creature_pool = Image.new("RGBA", IMAGE_SIZE)

    if CUSTOM_BACK:
        back_file_name = BASE_DIR + "Img/" + CUSTOM_BACK.split("/")[-1]
        if not os.path.exists(back_file_name):
            urllib.request.urlretrieve("https://cdn-gr-prod.ludia.net/jw2018/" + CUSTOM_BACK, back_file_name)
        background = Image.open(back_file_name)
        if background.width > background.height:
            background = background.transpose(Image.Transpose.ROTATE_90).resize(IMAGE_SIZE)
        else:
            background = background.resize(IMAGE_SIZE)
        creature_pool.paste(background, (0, 0))

    # Header
    draw_text(creature_pool, (IMAGE_WIDTH // 2, 55), event_name, 16)
    draw_text(creature_pool, (IMAGE_WIDTH // 2, 15), "{0} - {1}".format(start_date, end_date), 36)

    # Pool
    drawing_context = ImageDraw.Draw(creature_pool)
    # Drawing format
    x_offset = (IMAGE_WIDTH - 100) // CREATURES_PER_ROW
    y_offset = ((IMAGE_HEIGHT - HEADER_AREA - 50) // ((len(pool) + CREATURES_PER_ROW - 1) // CREATURES_PER_ROW))

    # Creatures
    for creature_index in range(len(pool)):
        creature = pool[creature_index]
        creature_file_name = find_img(creature.split()[0]).split("/")[-1]
        creature_img_path = BASE_DIR + "Img/" + creature_file_name
        x_coord = 50 + (CREATURE_WIDTH // 4) + x_offset * (creature_index % CREATURES_PER_ROW)
        y_coord = HEADER_AREA + 50 + y_offset * (creature_index // CREATURES_PER_ROW)
        if os.path.exists(creature_img_path):
            creature_img = Image.open(creature_img_path).resize((CREATURE_WIDTH, CREATURE_HEIGHT))
            creature_pool.alpha_composite(creature_img, (x_coord, y_coord))
        else:
            draw_text(creature_pool, (x_coord, y_coord), creature, 16)

    creature_pool.show()
    f_name = event_name.replace("/", "_")
    creature_pool.save(BASE_DIR + "plots/" + f_name + "_creatures.png")
