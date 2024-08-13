import json
from utilities import *
from PIL import Image, ImageDraw, ImageFont
import urllib.request

with open(r"D:\Dino\json\guid_map_indent.json") as f:
    data = json.load(f)

abilities = []
for guid in data.keys():
    if "references" in data[guid].keys():
        if ("PVEBattle\\AbilityRestrictions/Restriction_Ability_Stun.json" in data[guid]["references"]) or ("PVEBattle\\AbilityRestrictions/Restriction_Ability_Swap_In_Stun.json" in data[guid]["references"]):
            abilities.append(data[guid]["owner"])

creatures = []
creature_paths = []
for guid in data.keys():
    if "references" in data[guid].keys():
        if ("PVEBattle\\AbilityRestrictions/Restriction_Ability_Stun.json" in data[guid]["references"]) or ("PVEBattle\\AbilityRestrictions/Restriction_Ability_Swap_In_Stun.json" in data[guid]["references"]):
            for entry in data[guid]["references"]:
                if entry.startswith("CreaturesStaticData"):
                    creature_name = entry.rsplit("/", maxsplit=1)[-1].rsplit(".", maxsplit=1)[0]
                    if not creature_name.startswith("A_") and not (creature_name[0].isupper() and creature_name[1].isupper()):
                        if not creature_name in creatures:
                            creature_paths.append(entry)
                            creatures.append(creature_name)

creature_guids = []
for guid in data.keys():
    if "owner" in data[guid]:
        if data[guid]["owner"].replace("Assets/Data/", "") in creature_paths:
            creature_guids.append(guid)

creature_guids = list(filter(lambda x: find_rarity(x) in ["Rare", "Epic", "Legendary", "Omega"], creature_guids))


def draw_text(img, coords, txt, size, anchor="mt"):
    drawing_context = ImageDraw.Draw(img)
    fnt = ImageFont.truetype("segoeuil.ttf", size=size)
    drawing_context.text(coords, txt, font=fnt, fill=(0, 0, 0, 255), stroke_width=2, anchor=anchor)
    drawing_context.text(coords, txt, font=fnt, fill=(255, 255, 255, 255), stroke_width=1, anchor=anchor)


CUSTOM_BACK = "NewsCenter/NC2_Champ_Tyrannometrodon.jpg"

### Image dimensions ###
IMAGE_WIDTH = 1500
IMAGE_HEIGHT = 600
IMAGE_SIZE = (IMAGE_WIDTH, IMAGE_HEIGHT)
CREATURE_WIDTH = 90
CREATURE_HEIGHT = CREATURE_WIDTH * 250 // 207
CREATURES_PER_ROW = 10

creature_pool = Image.new("RGBA", IMAGE_SIZE)

if CUSTOM_BACK:
    back_file_name = BASE_DIR + "Img/" + CUSTOM_BACK.split("/")[-1]
    if not os.path.exists(back_file_name):
        urllib.request.urlretrieve("https://cdn-gr-prod.ludia.net/jw2018/" + CUSTOM_BACK, back_file_name)
    background = Image.open(back_file_name)
    if (background.height < background.width) ^ (IMAGE_HEIGHT < IMAGE_WIDTH):
        background = background.transpose(Image.Transpose.ROTATE_90).resize(IMAGE_SIZE)
    else:
        background = background.resize(IMAGE_SIZE)
    creature_pool.paste(background, (0, 0))

    # Pool
    drawing_context = ImageDraw.Draw(creature_pool)
    # Drawing format
    x_offset = IMAGE_WIDTH // CREATURES_PER_ROW
    y_offset = ((IMAGE_HEIGHT - 50) // ((len(creature_guids) + CREATURES_PER_ROW - 1) // CREATURES_PER_ROW))

    # Creatures
    for creature_index in range(len(creature_guids)):
        creature = creature_guids[creature_index]
        creature_file_name = find_img(creature.split()[0]).split("/")[-1]
        creature_img_path = BASE_DIR + "Img/" + creature_file_name
        x_coord = 10 + (CREATURE_WIDTH // 4) + x_offset * (creature_index % CREATURES_PER_ROW)
        y_coord = 40 + y_offset * (creature_index // CREATURES_PER_ROW)
        if os.path.exists(creature_img_path):
            creature_img = Image.open(creature_img_path).resize((CREATURE_WIDTH, CREATURE_HEIGHT))
            creature_pool.alpha_composite(creature_img, (x_coord, y_coord))
        else:
            draw_text(creature_pool, (x_coord, y_coord), creature, 16)

    creature_pool.show()
    creature_pool.save(BASE_DIR + "plots/tournament_creatures.png")
