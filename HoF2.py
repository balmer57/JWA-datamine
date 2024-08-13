import json

from utilities import *
from PIL import Image, ImageDraw, ImageFont
from unpcap import *


def draw_text(img, coords, txt, size, anchor="mm", font_name="segoeui.ttf", color=(255, 255, 255, 255)):
    coords_scaled = (coords[0]*SCALE, coords[1]*SCALE)
    drawing_context = ImageDraw.Draw(img)
    fnt = ImageFont.truetype(font_name, size=size*SCALE)
    drawing_context.text(coords_scaled, txt, font=fnt, fill=(0, 0, 0, 255), stroke_width=2, anchor=anchor)
    drawing_context.text(coords_scaled, txt, font=fnt, fill=color, stroke_width=1, anchor=anchor)


def extract_tours(file1, file2, index1, index2):
    _, _ = extract_pcap(BASE_DIR + file1)
    if index2 is not None:
        _, _ = extract_pcap(BASE_DIR + file2)
        indices = [index1, index2]
    else:
        indices = [index1]
    tour = list()
    index = 0
    for alliance in [alliance_items[i] for i in indices]:
        for entry in alliance:
            entry["alliance"] = index
            tour.append(entry)
        index += 1
    tour.sort(key=lambda x: get_player_name(x["aid"]))
    tour.sort(key=lambda x: x["asv"], reverse=True)
    with open("temp_save.json", "w") as f:
        json.dump(tour, f)


# extract_tours("PCAPdroid_01_июл._19_10_42.pcap", "PCAPdroid_01_июл._19_18_33.pcap", 0, 2)
with open("temp_save.json") as f:
    tour = json.load(f)
tour = list(filter(lambda x: x["asv"] > 1000, tour))
ids = [x["aid"] for x in tour]
for item in range(len(tour)):
    tour[item]["occur"] = ids.count(tour[item]["aid"])

### Settings ###
BACKGROUND_IMG = "1687795364_bogatyr_club_p_fon_dlya_prezentatsii_paleontologiya_insta.jpg"
TOUR_NAME = "June 2024"
TOURS_ID = [482, 483, 484, 485]

### Image dimensions ###
SCALE = 2
IMAGE_WIDTH = 1200
IMAGE_HEIGHT = 700
IMAGE_SIZE = (IMAGE_WIDTH*SCALE, IMAGE_HEIGHT*SCALE)
HEADER_AREA = 100
PLAYERS_DISPLAYED = 10
HIGHLIGHTED = 3
BD_COLOR = (255, 210, 210, 255)
BB_COLOR = (210, 255, 210, 255)

# Background
background = Image.open(BASE_DIR + "Img/" + BACKGROUND_IMG).resize(IMAGE_SIZE)

collage = Image.new("RGBA", IMAGE_SIZE)
collage.paste(background, (0, 0))

# Header
draw_text(collage, (IMAGE_WIDTH // 5, 50), f"{TOUR_NAME}", 36, font_name="palabi.ttf")
draw_text(collage, (IMAGE_WIDTH * 7 // 10, 25), "Alliances", 36)
draw_text(collage, (IMAGE_WIDTH * 7 // 10, 65), "Hall of Fame", 36)

tours_top = list()
for TOUR_ID in TOURS_ID:
    with open(CACHE_DIR + "../../files/Leaderboard_{}_ScoresCache.3300000000001.json".format(TOUR_ID)) as f:
        tours_top.append(json.load(f)["MapInfo"]["TopScores"])

tour_top = dict()
for top in tours_top:
    for id in top.keys():
        if (id not in tour_top.keys()) or (tour_top[id]["Rank"] > top[id]["Rank"]):
            tour_top[id] = top[id]

# Top-10
while tour[PLAYERS_DISPLAYED - 1]["asv"] == tour[PLAYERS_DISPLAYED]["asv"]:
    PLAYERS_DISPLAYED += 1
h_per_player = (IMAGE_HEIGHT - HEADER_AREA - 20) / PLAYERS_DISPLAYED
last_score = 0
last_place = 0
real_place = 0
for player in tour[:PLAYERS_DISPLAYED]:
    name = get_player_name(player["aid"])
    if player["occur"] > 1:
        name += "*"
    score = player["asv"]
    if score == last_score:
        place = last_place
    else:
        place = real_place + 1
        last_place = place
    y = HEADER_AREA + (real_place * h_per_player) + h_per_player // 3
    text_size = 32 if place <= HIGHLIGHTED else 24
    if player["alliance"] == 0:
        color = BD_COLOR
    else:
        color = BB_COLOR
    draw_text(collage, (50, y), f"{place}", text_size, color=color)
    draw_text(collage, (210, y), f"{name}", text_size, color=color)
    draw_text(collage, (390, y), f"{score}", text_size, color=color)
    if str(player["aid"]) in tour_top.keys():
        draw_text(collage, (27, y - 3), str(tour_top[str(player["aid"])]["Rank"]), text_size // 2, color=(210, 210, 255, 255))
    last_score = score
    real_place += 1

# Other
PLAYERS_PER_COLUMN = (len(tour) - PLAYERS_DISPLAYED + 2) // 3
h_per_player = (IMAGE_HEIGHT - HEADER_AREA - 20) / PLAYERS_PER_COLUMN
# column_x = IMAGE_WIDTH * 4 // 9
column_x = IMAGE_WIDTH * 3 // 8
row_index = 0
for player in tour[PLAYERS_DISPLAYED:]:
    name = get_player_name(player["aid"])
    if player["occur"] > 1:
        name += "*"
    score = player["asv"]
    if score == last_score:
        place = last_place
    else:
        place = real_place + 1
        last_place = place
    y = HEADER_AREA + (row_index * h_per_player) + h_per_player // 3
    text_size = 16
    if player["alliance"] == 0:
        color = BD_COLOR
    else:
        color = BB_COLOR
    draw_text(collage, (column_x + 50, y), f"{place}", text_size, color=color)
    draw_text(collage, (column_x + 130, y), f"{name}", text_size - 1, color=color)
    draw_text(collage, (column_x + 220, y), f"{score}", text_size, color=color)
    if str(player["aid"]) in tour_top.keys():
        draw_text(collage, (column_x + 26, y - 2), str(tour_top[str(player["aid"])]["Rank"]), text_size * 2 // 3, color=(210, 210, 255, 255))
    last_score = score
    real_place += 1
    row_index += 1
    if row_index == PLAYERS_PER_COLUMN:
        row_index = 0
        column_x += IMAGE_WIDTH * 1 // 5


collage.show()
collage.save(BASE_DIR + "plots/HoF2_{}.png".format(TOUR_ID))
