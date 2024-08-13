from utilities import *
from PIL import Image, ImageDraw, ImageFont

with open(JSON_DIR + "pcap_out.json") as f:
    strings = json.load(f)
    strings_decoded = json.loads(json.dumps(strings), object_pairs_hook=guid_hook)

guilds_map = dict()
with open(JSON_DIR + "guilds.json") as f:
    guilds = json.load(f)
    for guild in guilds.values():
        for member in guild["members"]:
            guilds_map[int(member["id"])] = {"id": member["id"], "name": member["name"], "guild": guild["name"]}

additional_players = {3300000000001: "Unknown"}

for player in additional_players:
    guilds_map[int(player)] = {"id": str(player), "name": additional_players[player], "guild": "Alliance"}


def draw_text(img, coords, txt, size, anchor="mm", font_name="segoeuil.ttf"):
    drawing_context = ImageDraw.Draw(img)
    fnt = ImageFont.truetype(font_name, size=size)
    drawing_context.text(coords, txt, font=fnt, fill=(0, 0, 0, 255), stroke_width=2, anchor=anchor)
    drawing_context.text(coords, txt, font=fnt, fill=(255, 255, 255, 255), stroke_width=1, anchor=anchor)


tour = alliance_items[0]
tour.sort(key=lambda x: guilds_map[int(x["aid"])]["name"].lower() if int(x["aid"]) in guilds_map.keys() else str(x["aid"]))
tour.sort(key=lambda x: x["asv"], reverse=True)


### Settings ###
BACKGROUND_IMG = "img_2024-02.png"
TOUR_NAME = "February 2024 (1/4)"
TOUR_ID = 445

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
draw_text(collage, (IMAGE_WIDTH // 6 + 20, 50), f"{TOUR_NAME}", 36, font_name="palabi.ttf")
# draw_text(collage, (IMAGE_WIDTH // 2, 25), "Alliance", 36)
# draw_text(collage, (IMAGE_WIDTH // 2, 65), "Hall of Fame", 36)

# Alliance top
while tour[PLAYERS_DISPLAYED - 1]["asv"] == tour[PLAYERS_DISPLAYED]["asv"]:
    PLAYERS_DISPLAYED += 1
h_per_player = (IMAGE_HEIGHT - HEADER_AREA - 20) / PLAYERS_DISPLAYED
last_score = 0
last_place = 0
real_place = 0
for player in tour[:PLAYERS_DISPLAYED]:
    name = guilds_map[int(player["aid"])]["name"] if int(player["aid"]) in guilds_map.keys() else player["aid"]
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
top_not_empty = False
with open("D:/Dino/com.ludia.jw2/files/Leaderboard_{}_ScoresCache.3300000000001.json".format(TOUR_ID)) as f:
    tour_top = json.load(f)["MapInfo"]["TopScores"]
    y = IMAGE_HEIGHT // 2 + 50
    alliance_player_list = [str(x["aid"]) for x in tour]
    for player in tour_top.keys():
        if player in alliance_player_list:
            name = guilds_map[int(player)]["name"] if int(player) in guilds_map.keys() else player
            score = tour_top[player]["Score"]
            place = tour_top[player]["Rank"]
            draw_text(collage, (IMAGE_WIDTH - 400, y), f"{place}", 32)
            draw_text(collage, (IMAGE_WIDTH - 240, y), f"{name}", 32)
            draw_text(collage, (IMAGE_WIDTH - 60, y), f"{score}", 32)
            y += 50
            top_not_empty = True
# if top_not_empty:
#     draw_text(collage, ((5 * IMAGE_WIDTH) // 6, IMAGE_HEIGHT // 2 - 20), "World Top-500", 36)

collage.show()
collage.save(BASE_DIR + "plots/HoF_{}.png".format(TOUR_ID))
