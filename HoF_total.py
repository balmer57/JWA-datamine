from utilities import *
from PIL import Image, ImageDraw, ImageFont

with open(JSON_DIR + "pcap_out.json") as f:
    strings = json.load(f)
    strings_decoded = json.loads(json.dumps(strings), object_pairs_hook=guid_hook)


def draw_text(img, coords, txt, size, anchor="mm", font_name="segoeuil.ttf", color=(255, 255, 255, 255)):
    drawing_context = ImageDraw.Draw(img)
    fnt = ImageFont.truetype(font_name, size=size)
    drawing_context.text(coords, txt, font=fnt, fill=(0, 0, 0, 255), stroke_width=2, anchor=anchor)
    drawing_context.text(coords, txt, font=fnt, fill=color, stroke_width=1, anchor=anchor)


tour = alliance_items[0]
tour.sort(key=lambda x: get_player_name(x["aid"]))
tour.sort(key=lambda x: x["asv"], reverse=True)

### Settings ###
BACKGROUND_IMG = "photo_2024-07-01_19-43-07.jpg"
TOUR_NAME = "June 2024"
TOURS_ID = [482, 483, 484, 485]
TOURS_NAME = ["Rare Advantage", "Rare Skill", "Apex Skill", "Apex Advantage"]

### Image dimensions ###
IMAGE_WIDTH = 1200
IMAGE_HEIGHT = 800
IMAGE_SIZE = (IMAGE_WIDTH, IMAGE_HEIGHT)
HEADER_AREA = 100
PLAYERS_DISPLAYED = 10
HIGHLIGHTED = 3


# Background
background = Image.open(BASE_DIR + "Img/" + BACKGROUND_IMG).resize(IMAGE_SIZE)

collage = Image.new("RGBA", IMAGE_SIZE)
collage.paste(background, (0, 0))

# Header
if len(TOURS_ID) == 4:
    draw_text(collage, (IMAGE_WIDTH // 6 + 20, 50), f"{TOUR_NAME}", 36, font_name="palabi.ttf")
    draw_text(collage, (7 * IMAGE_WIDTH // 10, 80), "Alliance", 80, font_name="palabi.ttf")
    draw_text(collage, (7 * IMAGE_WIDTH // 10, 150), "Hall of Fame", 60, font_name="palabi.ttf")
    NAME_SPACING = 25
    TOURNAMENT_SHIFT = -10
else:
    draw_text(collage, (IMAGE_WIDTH // 6 + 20, 50), f"{TOUR_NAME}", 36, font_name="palabi.ttf")
    draw_text(collage, (11*IMAGE_WIDTH // 20, 100), "Alliance", 60, font_name="palabi.ttf")
    draw_text(collage, (11*IMAGE_WIDTH // 20, 180), "Hall of Fame", 50, font_name="palabi.ttf")
    NAME_SPACING = 25
    TOURNAMENT_SHIFT = 60


# Alliance top
while tour[PLAYERS_DISPLAYED - 1]["asv"] == tour[PLAYERS_DISPLAYED]["asv"]:
    PLAYERS_DISPLAYED += 1
h_per_player = (IMAGE_HEIGHT - HEADER_AREA - 20) / PLAYERS_DISPLAYED
last_score = 0
last_place = 0
real_place = 0
for player in tour[:PLAYERS_DISPLAYED]:
    name = get_player_name(player["aid"])
    score = player["asv"]
    if score == last_score:
        place = last_place
    else:
        place = real_place + 1
        last_place = place
    y = HEADER_AREA + (real_place * h_per_player) + h_per_player // 3
    text_size = 32 if place <= HIGHLIGHTED else 24
    draw_text(collage, (40, y), f"{place}", text_size)
    draw_text(collage, (200, y), f"{name}", text_size)
    draw_text(collage, (380, y), f"{score}", text_size)
    last_score = score
    real_place += 1

# World top
tours_count = len(TOURS_ID)
for i, TOUR_ID in enumerate(TOURS_ID):
    top_not_empty = False
    if i < tours_count // 2:
        X = 500
    else:
        X = IMAGE_WIDTH - 300
    if tours_count == 4:
        row = i % 2 + 1
    elif tours_count == 5:
        row = (i + 1) % 3
    else:
        row = i % 3
    Y = (IMAGE_HEIGHT - TOURNAMENT_SHIFT) * row // 3 + TOURNAMENT_SHIFT
    with open("D:/Dino/com.ludia.jw2/files/Leaderboard_{}_ScoresCache.3300000000001.json".format(TOUR_ID)) as f:
        tour_top = json.load(f)["MapInfo"]["TopScores"]
        y = Y + 45
        alliance_player_list = [str(x["aid"]) for x in tour]
        for player in tour_top.keys():
            if player in alliance_player_list:
                name = get_player_name(player)
                score = tour_top[player]["Score"]
                place = tour_top[player]["Rank"]
                if place > 3:
                    draw_text(collage, (X, y), f"{place}", 20, color=(255, (place * place * 255) // 25000, place // 2, 255))
                else:
                    draw_text(collage, (X, y), f"{place}", 20, color="red")
                draw_text(collage, (X + 140, y), f"{name}", 20)
                draw_text(collage, (X + 260, y), f"{score}", 20)
                y += NAME_SPACING
                top_not_empty = True
    if top_not_empty:
        draw_text(collage, (X + 150, Y), TOURS_NAME[i], 30)

collage.show()
collage.save(BASE_DIR + "plots/HoF_{}_total.png".format(TOURS_ID[-1]))
