from PIL import Image, ImageDraw, ImageFont
from utilities import *
import os
import urllib.request

CUSTOM_BACK = "TTE/Banner_TTE_SummerSports.jpg"

with open(JSON_DIR + "events.json") as f:
    events_data = json.load(f)

found = False
track = None
for event in events_data["future"]["other"]:
    if event["n"] == "TourTrackEvent":
        found = True
        track = event
if not found:
    for event in events_data["ongoing"]["other"]:
        if event["n"] == "TourTrackEvent":
            found = True
            track = event
if not found:
    print("Track event not found!")


def find_img(guid):
    fname = None
    if guid in guid_map.keys():
        entry = guid_map[guid]
        fname = DATA_DIR + "/../../" + entry
    elif os.path.exists(DATA_DIR + "/../Data2/" + guid):
        fname = DATA_DIR + "/../Data2/" + guid
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
IMAGE_HEIGHT = 1500
IMAGE_SIZE = (IMAGE_WIDTH, IMAGE_HEIGHT)
IMAGE2_SIZE = (IMAGE_WIDTH*4//5, IMAGE_HEIGHT*4//5)
HEADER_AREA = 50
CREATURE_WIDTH = 60
CREATURE_HEIGHT = CREATURE_WIDTH * 250 // 207
CREATURE_WIDTH_POOL = 90
CREATURE_HEIGHT_POOL = CREATURE_WIDTH_POOL * 250 // 207
REWARD_WIDTH = 60
REWARD_HEIGHT = REWARD_WIDTH * 250 // 207
REWARD_OFFSET = 10
LEVEL_TEXT_OFFSET = 90
STAGE_NAME_OFFSET = 270
CREATURES_PER_ROW = 4

if found:
    # Prepare data
    track_name = track["d"]["title"]
    start_date = track["s"].split()[0]
    end_date = track["e"].split()[0]
    battle_data = track["d"]["battle_data"]
    pool = track["d"]["creature_pool"]["crl"][0]["cli"]

    collage = Image.new("RGBA", IMAGE_SIZE)
    creature_pool = Image.new("RGBA", IMAGE_SIZE)

    if CUSTOM_BACK:
        back_file_name = BASE_DIR + "Img/" + CUSTOM_BACK.split("/")[-1]
        if not os.path.exists(back_file_name):
            try:
                urllib.request.urlretrieve("https://cdn-gr-prod.ludia.net/jw2018/" + CUSTOM_BACK, back_file_name)
            except:
                pass
        if not os.path.exists(back_file_name):
            try:
                urllib.request.urlretrieve("https://cdn-gr-test.ludia.net/jw2018/" + CUSTOM_BACK, back_file_name)
            except:
                pass
        background = Image.open(back_file_name)
        if background.height < background.width:
            background = background.transpose(Image.Transpose.ROTATE_90).resize(IMAGE_SIZE)
        else:
            background = background.resize(IMAGE_SIZE)
        collage.paste(background, (0, 0))
        creature_pool.paste(background, (0, 0))

    # Header
    draw_text(collage, (IMAGE_WIDTH // 2, 15), "{0} - {1}".format(start_date, end_date), 36)
    draw_text(creature_pool, (IMAGE_WIDTH // 2, 15), "{0} - {1}".format(start_date, end_date), 36)

    # Stages
    if len(battle_data) > 10:
        CREATURE_WIDTH = 60
        CREATURE_HEIGHT = CREATURE_WIDTH * 250 // 207
    drawing_context = ImageDraw.Draw(collage)
    for stage_index in range(len(battle_data)):
        stage = battle_data[stage_index]

        # Drawing format
        x_offset = (IMAGE_WIDTH - STAGE_NAME_OFFSET - 3 * CREATURE_WIDTH) // 3
        y_offset = ((IMAGE_HEIGHT - HEADER_AREA) // len(battle_data))
        y_coord = IMAGE_HEIGHT - y_offset * (stage_index + 1) - 5

        # Stage
        if "leveloffset" in stage["scaling"].keys():
            level = 20 + stage["scaling"]["leveloffset"]
            level_str = str(level) + "*"
        elif "levelset" in stage["scaling"].keys():
            level_str = str(stage["scaling"]["levelset"])
        else:
            level_str = "?"
        boosts = [stage["scaling"][x] for x in ["hpaep", "atkaep", "spdaep"]]
        draw_text(collage, (LEVEL_TEXT_OFFSET, y_coord + 20), "Stage {0}".format(stage_index + 1), 20, anchor="lt")
        draw_text(collage, (LEVEL_TEXT_OFFSET, y_coord + 50), "Level {0} ({1}, {2}, {3})".format(level_str, *boosts), 20, anchor="lt")

        # Get reward
        reward_list_guid = stage["reward"][0]["reward"].split(":")[0]
        reward_list = get_json_from_guid(reward_list_guid)
        if reward_list and "rl" in reward_list.keys():
            quantity = reward_list["rl"][0]["q"]["v"]
            reward_guid = reward_list["rl"][0]["r"]["guid"]
            reward = get_json_from_guid(reward_guid)
            if reward["$type"].split(",")[0] == "RewDnDa":
                creature_dna = get_json_from_guid(reward["cr"]["guid"])
                creature_guid = creature_dna["cr"]["guid"]
                creature_img_path = find_img(creature_guid)
                img_path = BASE_DIR + "Img/" + creature_img_path.rsplit("/")[-1]
                creature_img = Image.open(img_path).resize((REWARD_WIDTH, REWARD_HEIGHT))
                collage.alpha_composite(creature_img, (REWARD_OFFSET, y_coord))
                draw_text(collage, (REWARD_OFFSET + REWARD_WIDTH // 2, y_coord + REWARD_HEIGHT + 5), f"{quantity}", 20)
        else:
            draw_text(collage, (REWARD_OFFSET + REWARD_WIDTH // 2, y_coord + 20), "?", 32)
        # Get creatures
        creatures = stage["battle"]["creature"]["cli"]

        # Creatures
        for creature_index in range(len(creatures)):
            creature = creatures[creature_index]
            creature_file_name = find_img(creature.split()[0]).split("/")[-1]
            creature_img_path = BASE_DIR + "Img/" + creature_file_name
            x_coord = STAGE_NAME_OFFSET + x_offset * creature_index + CREATURE_WIDTH * creature_index
            if creature_file_name and os.path.exists(creature_img_path):
                creature_img = Image.open(creature_img_path).resize((CREATURE_WIDTH, CREATURE_HEIGHT))
                collage.alpha_composite(creature_img, (x_coord, y_coord))
            else:
                draw_text(collage, (x_coord, y_coord + CREATURE_HEIGHT // 2), creature, 16, anchor="lm")
            creature_index += 1

    # Pool
    drawing_context = ImageDraw.Draw(creature_pool)
    if len(pool) > 24:
        CREATURES_PER_ROW = 5
    # Drawing format
    x_offset = (IMAGE_WIDTH - CREATURES_PER_ROW * CREATURE_WIDTH_POOL) // (CREATURES_PER_ROW + 1)
    y_offset = ((IMAGE_HEIGHT - HEADER_AREA - 40) // ((len(pool) + CREATURES_PER_ROW - 1) // CREATURES_PER_ROW))

    # Creatures
    for creature_index in range(len(pool)):
        creature = pool[creature_index]
        creature_file_name = find_img(creature.split()[0]).split("/")[-1]
        creature_img_path = BASE_DIR + "Img/" + creature_file_name
        x_coord = x_offset + (x_offset + CREATURE_WIDTH_POOL) * (creature_index % CREATURES_PER_ROW)
        y_coord = HEADER_AREA + 30 + y_offset * (creature_index // CREATURES_PER_ROW)
        if os.path.exists(creature_img_path):
            creature_img = Image.open(creature_img_path).resize((CREATURE_WIDTH_POOL, CREATURE_HEIGHT_POOL))
            creature_pool.alpha_composite(creature_img, (x_coord, y_coord))
        else:
            draw_text(creature_pool, (x_coord, y_coord), creature, 16)

    collage.show()
    collage.save(BASE_DIR + "plots/" + track_name + ".png")
    # creature_pool.show()
    creature_pool.save(BASE_DIR + "plots/" + track_name + "_pool.png")
