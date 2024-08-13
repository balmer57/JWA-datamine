from PIL import Image
import glob
import transparency_fix
import moviepy.editor as mp


def create_gifs():
    WIDTH = 200
    HEIGHT = 200
    OFFSET_X = 0
    OFFSET_Y = 24
    COLS = 5
    ROWS = 5

    path = "D:/Dino/Img/Texture2D/"
    for file_name in glob.glob(path + "img_Emoticons_*"):
        print(file_name)
        im = Image.open(file_name)

        imgs = [im.crop((OFFSET_X + x*WIDTH, OFFSET_Y + y*HEIGHT, OFFSET_X + (x + 1)*WIDTH, OFFSET_Y + (y + 1)*HEIGHT)).resize((512, 512)) for x in range(COLS) for y in range(ROWS)]

        export_name = file_name.split("/")[-1].split("\\")[-1].split('.')[0][14:]
        transparency_fix.save_transparent_gif(imgs[:5], durations=150, save_file='D:/Dino/gif/gif/{}.gif'.format(export_name))
        for img_index in range(len(imgs)):
            img = imgs[img_index]
            img.save('D:/Dino/plots/gifs/{}_{}.png'.format(file_name.split("/")[-1].split("\\")[-1].rsplit('.', maxsplit=1)[0], img_index))


def convert_gifs():
    path = "D:/Dino/gif/"
    for file_name in glob.glob(path + "gif/*.gif"):
        print(file_name)
        export_name = path + "webm/" + file_name.split("/")[-1].split("\\")[-1].split('.')[0] + ".webm"
        clip = mp.VideoFileClip(file_name)
        clip.write_videofile(export_name, codec="libvpx-vp9")


create_gifs()
# convert_gifs()
