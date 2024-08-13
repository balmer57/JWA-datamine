import glob
from PIL import Image, ImageDraw, ImageFont
from utilities import *
import numpy as np

zones = ["Everywhere", "Generic1", "Generic2", "Generic3", "Generic4", "Park", "ShortRange"]
zones_special = ["SpecialTerrains/" + x for x in ["Airport", "Arts", "ATM", "Bank", "Boating", "Fishing", "Gas_station", "Hospital", "Restaurant", "Restroom", "School", "Transit"]]
zones_daily = ["Daily auto-migration/" + x for x in ["1Monday", "2Tuesday", "3Wednesday", "4Thursday", "5Friday", "6Saturday", "7Sunday"]]

### Image dimensions ###
IMAGE_WIDTH = 960
IMAGE_HEIGHT = 1536
IMAGE_SIZE = (IMAGE_WIDTH, IMAGE_HEIGHT)
HEADER_AREA = 100
CREATURE_WIDTH = 90
CREATURE_HEIGHT = CREATURE_WIDTH * 250 // 207
CREATURES_PER_ROW = 6
ICON_SPACING = 5
ICON_WIDTH = (CREATURE_WIDTH - 3 * ICON_SPACING) // 4
ICON_HEIGHT = ICON_WIDTH


def draw_text(img, coords, txt, size, anchor="mt"):
    drawing_context = ImageDraw.Draw(img)
    fnt = ImageFont.truetype("segoeuil.ttf", size=size)
    drawing_context.text(coords, txt, font=fnt, fill=(0, 0, 0, 255), stroke_width=2, anchor=anchor)
    drawing_context.text(coords, txt, font=fnt, fill=(255, 255, 255, 255), stroke_width=1, anchor=anchor)


def repaint_img(img, value, color_channel):
    data = np.array(img)
    red, green, blue, alpha = data.T

    if value == 0:
        areas = (red == 0) & (blue == 0) & (green == 0)
        data[..., :][areas.T] = (0, 0, 0, 0)
    else:
        areas = (red == 0) & (blue == 0) & (green == 0)
        data[..., -1][areas.T] = [(x / 300) * (45 + value) for x in data[..., -1][areas.T]]
        data[..., :-1][areas.T] = [255 * x for x in color_channel]

    return Image.fromarray(data)


path = DATA2_DIR + "Geolocation/Radar/RadarBucket/"

color_scheme = [(1, 0.75, 0), (1, 0, 0), (1, 0.75, 0), (0, 0, 0.5)]


def draw_zones():
    for zone in zones:
        # Collect data
        dinos = []
        max_value = 0
        for file in glob.glob(path + zone + "*"):
            with open(file) as f:
                data = json.load(f)
                for dino in data["dinow"]:
                    guid = dino["dino"]["guid"]
                    activity = [dino[x] for x in ["dawnWeight", "dayWeight", "duskWeight", "nightWeight"]]
                    if max(activity) > max_value:
                        max_value = max(activity)
                    dinos.append([guid, activity])
        # Draw
        if len(dinos) > 30:
            CREATURES_PER_ROW = 6
            CREATURE_WIDTH = 90
            TEXT_AREA_HEIGHT = 55
        elif len(dinos) <= 12:
            CREATURES_PER_ROW = 3
            CREATURE_WIDTH = 160
            TEXT_AREA_HEIGHT = 75
        elif len(dinos) <= 24:
            CREATURES_PER_ROW = 4
            CREATURE_WIDTH = 120
            TEXT_AREA_HEIGHT = 65
        else:
            CREATURES_PER_ROW = 5
            CREATURE_WIDTH = 100
            TEXT_AREA_HEIGHT = 60
        CREATURE_HEIGHT = CREATURE_WIDTH * 250 // 207
        ICON_WIDTH = (CREATURE_WIDTH - 3 * ICON_SPACING) // 4
        ICON_HEIGHT = ICON_WIDTH

        collage = Image.open(IMG_DIR + "JurassicWorldAlive_Wallpaper_47_AndroidPhone-960x1536.jpg").resize(IMAGE_SIZE).convert('RGBA')
        draw_text(collage, (IMAGE_WIDTH // 2, 20), zone, 36)
        x_space = (IMAGE_WIDTH - CREATURES_PER_ROW * CREATURE_WIDTH) // CREATURES_PER_ROW
        row_count = ((len(dinos) - 1) // CREATURES_PER_ROW) + 1
        y_space = (IMAGE_HEIGHT - HEADER_AREA - row_count * (CREATURE_HEIGHT + TEXT_AREA_HEIGHT)) // (row_count - 1) + TEXT_AREA_HEIGHT
        for dino_index in range(len(dinos)):
            # Prepare dino picture
            dino = dinos[dino_index]
            creature_name = find_name(dino[0])
            creature_img_path = find_img(dino[0])
            img_path = IMG_DIR + creature_img_path.rsplit("/")[-1]
            creature_img = Image.open(img_path).resize((CREATURE_WIDTH, CREATURE_HEIGHT))
            x_coord = x_space // 2 + (dino_index % CREATURES_PER_ROW) * (CREATURE_WIDTH + x_space)
            y_coord = HEADER_AREA + (dino_index // CREATURES_PER_ROW) * (CREATURE_HEIGHT + y_space)
            # Rectangle
            newImg = Image.new("RGBA", IMAGE_SIZE)
            drawing_context = ImageDraw.Draw(newImg)
            drawing_context.rectangle(
                [x_coord - 30, y_coord - 15, x_coord + CREATURE_WIDTH + 30, y_coord + CREATURE_HEIGHT + TEXT_AREA_HEIGHT],
                fill="#B0B0B0A0", outline="#ffffffff")
            collage.alpha_composite(newImg)
            # Dino
            collage.alpha_composite(creature_img, (x_coord, y_coord))
            draw_text(collage, (x_coord + CREATURE_WIDTH // 2, y_coord + CREATURE_HEIGHT + 15), creature_name, 12)

            for icon_index in range(4):
                icon = Image.open(IMG_DIR + ["sunrise", "day", "sunset", "night"][icon_index] + ".png").resize((ICON_WIDTH, ICON_HEIGHT))
                value = int(dino[1][icon_index] / max_value * 255)
                icon = repaint_img(icon, value, color_scheme[icon_index])
                collage.alpha_composite(icon, (x_coord + icon_index * (ICON_WIDTH + ICON_SPACING), y_coord + CREATURE_HEIGHT + 35))
        collage.save(BASE_DIR + "plots/zones/" + zone + ".png")


def draw_daily_zones():
    CREATURES_PER_ROW = 2
    CREATURE_WIDTH = 90
    TEXT_AREA_HEIGHT = 55
    CREATURE_HEIGHT = CREATURE_WIDTH * 250 // 207
    ICON_WIDTH = (CREATURE_WIDTH - 3 * ICON_SPACING) // 4
    ICON_HEIGHT = ICON_WIDTH
    ZONE_NAME_WIDTH = 200

    collage = Image.open(IMG_DIR + "JurassicWorldAlive_Wallpaper_47_AndroidPhone-960x1536.jpg").resize(IMAGE_SIZE).convert('RGBA')
    draw_text(collage, (IMAGE_WIDTH // 2, 20), "Daily", 36)
    row_count = len(zones_daily)
    max_value = 0
    for zone_index in range(row_count):
        # Collect data
        zone_file = zones_daily[zone_index]
        dinos = []
        for file in glob.glob(path + zone_file + "*"):
            with open(file) as f:
                data = json.load(f)
                if data["dinow"] is not None:
                    for dino in data["dinow"]:
                        guid = dino["dino"]["guid"]
                        activity = [dino[x] for x in ["dawnWeight", "dayWeight", "duskWeight", "nightWeight"]]
                        if max(activity) > max_value:
                            max_value = max(activity)
                        dinos.append([guid, activity])
        zone_name = zone_file.split("/")[-1][1:]
        # Draw
        x_space = (IMAGE_WIDTH - ZONE_NAME_WIDTH - CREATURES_PER_ROW * CREATURE_WIDTH) // CREATURES_PER_ROW
        y_space = (IMAGE_HEIGHT - HEADER_AREA - row_count * (CREATURE_HEIGHT + TEXT_AREA_HEIGHT)) // (row_count - 1) + TEXT_AREA_HEIGHT
        y_coord = HEADER_AREA + zone_index * (CREATURE_HEIGHT + y_space)
        draw_text(collage, (50, y_coord + (CREATURE_WIDTH + TEXT_AREA_HEIGHT) // 2), zone_name, 36, anchor="lm")
        for dino_index in range(len(dinos)):
            # Prepare dino picture
            dino = dinos[dino_index]
            creature_name = find_name(dino[0])
            creature_img_path = find_img(dino[0])
            img_path = IMG_DIR + creature_img_path.rsplit("/")[-1]
            creature_img = Image.open(img_path).resize((CREATURE_WIDTH, CREATURE_HEIGHT))
            x_coord = ZONE_NAME_WIDTH + x_space // 2 + dino_index * (CREATURE_WIDTH + x_space)

            # Rectangle
            newImg = Image.new("RGBA", IMAGE_SIZE)
            drawing_context = ImageDraw.Draw(newImg)
            drawing_context.rectangle(
                [x_coord - 30, y_coord - 15, x_coord + CREATURE_WIDTH + 30, y_coord + CREATURE_HEIGHT + TEXT_AREA_HEIGHT],
                fill="#B0B0B0A0", outline="#ffffffff")
            collage.alpha_composite(newImg)
            # Dino
            collage.alpha_composite(creature_img, (x_coord, y_coord))
            draw_text(collage, (x_coord + CREATURE_WIDTH // 2, y_coord + CREATURE_HEIGHT + 15), creature_name, 12)

            for icon_index in range(4):
                icon = Image.open(IMG_DIR + ["sunrise", "day", "sunset", "night"][icon_index] + ".png").resize((ICON_WIDTH, ICON_HEIGHT))
                value = int(dino[1][icon_index] / max_value * 255)
                icon = repaint_img(icon, value, color_scheme[icon_index])
                collage.alpha_composite(icon, (x_coord + icon_index * (ICON_WIDTH + ICON_SPACING), y_coord + CREATURE_HEIGHT + 35))
    collage.save(BASE_DIR + "plots/zones/Daily.png")


def draw_special_zones():
    CREATURES_PER_ROW = 6
    CREATURE_WIDTH = 60
    TEXT_AREA_HEIGHT = 35
    CREATURE_HEIGHT = CREATURE_WIDTH * 250 // 207
    ICON_WIDTH = (CREATURE_WIDTH - 3 * ICON_SPACING) // 4
    ICON_HEIGHT = ICON_WIDTH
    ZONE_NAME_WIDTH = 130

    collage = Image.open(IMG_DIR + "JurassicWorldAlive_Wallpaper_47_AndroidPhone-960x1536.jpg").resize(IMAGE_SIZE).convert('RGBA')
    draw_text(collage, (IMAGE_WIDTH // 2, 20), "Special", 36)
    row_count = len(zones_special)
    max_value = 0
    for zone_index in range(row_count):
        # Collect data
        zone_file = zones_special[zone_index]
        dinos = []
        for file in glob.glob(path + zone_file + "*"):
            with open(file) as f:
                data = json.load(f)
                for dino in data["dinow"]:
                    guid = dino["dino"]["guid"]
                    activity = [dino[x] for x in ["dawnWeight", "dayWeight", "duskWeight", "nightWeight"]]
                    if max(activity) > max_value:
                        max_value = max(activity)
                    dinos.append([guid, activity])
        zone_name = zone_file.split("/")[-1]
        # Draw
        x_space = (IMAGE_WIDTH - ZONE_NAME_WIDTH - CREATURES_PER_ROW * CREATURE_WIDTH) // CREATURES_PER_ROW
        y_space = (IMAGE_HEIGHT - HEADER_AREA - row_count * (CREATURE_HEIGHT + TEXT_AREA_HEIGHT)) // (row_count - 1) + TEXT_AREA_HEIGHT
        y_coord = HEADER_AREA + zone_index * (CREATURE_HEIGHT + y_space)
        draw_text(collage, (20, y_coord + (CREATURE_WIDTH + TEXT_AREA_HEIGHT) // 2), zone_name, 24, anchor="lm")
        for dino_index in range(len(dinos)):
            # Prepare dino picture
            dino = dinos[dino_index]
            creature_name = find_name(dino[0])
            creature_img_path = find_img(dino[0])
            img_path = IMG_DIR + creature_img_path.rsplit("/")[-1]
            creature_img = Image.open(img_path).resize((CREATURE_WIDTH, CREATURE_HEIGHT))
            x_coord = ZONE_NAME_WIDTH + x_space // 2 + dino_index * (CREATURE_WIDTH + x_space)

            # Rectangle
            newImg = Image.new("RGBA", IMAGE_SIZE)
            drawing_context = ImageDraw.Draw(newImg)
            drawing_context.rectangle(
                [x_coord - 30, y_coord - 10, x_coord + CREATURE_WIDTH + 30, y_coord + CREATURE_HEIGHT + TEXT_AREA_HEIGHT],
                fill="#B0B0B0A0", outline="#ffffffff")
            collage.alpha_composite(newImg)
            # Dino
            collage.alpha_composite(creature_img, (x_coord, y_coord))
            draw_text(collage, (x_coord + CREATURE_WIDTH // 2, y_coord + CREATURE_HEIGHT + 5), creature_name, 10)

            for icon_index in range(4):
                icon = Image.open(IMG_DIR + ["sunrise", "day", "sunset", "night"][icon_index] + ".png").resize((ICON_WIDTH, ICON_HEIGHT))
                value = int(dino[1][icon_index] / max_value * 255)
                icon = repaint_img(icon, value, color_scheme[icon_index])
                collage.alpha_composite(icon, (x_coord + icon_index * (ICON_WIDTH + ICON_SPACING), y_coord + CREATURE_HEIGHT + 20))
    collage.save(BASE_DIR + "plots/zones/Special.png")

draw_zones()
draw_daily_zones()
# draw_special_zones()
