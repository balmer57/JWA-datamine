import sys
import re
import os
import subprocess
import urllib.request

if len(sys.argv) != 2:
    # print("Usage: python Parse_APK.py JWA_#_#_##.apk")
    file_path = r"D:\Dino\APK\JWA_3_7_29.apk"
else:
    file_path = sys.argv[1]

from utilities import BASE_DIR
SCRIPT_DIR = BASE_DIR + "JWA_scripts/"
KDIFF3_PATH = r"C:\Program Files\KDiff3\kdiff3.exe"

dir_name = os.path.dirname(file_path)
file_name = os.path.basename(file_path)
version = re.findall("\\d+[\\d_]+", file_name.split(".")[0])[-1]

print("Setting version...")
with open(SCRIPT_DIR + "utilities.py") as f:
    data = f.readlines()
    for line_index in range(len(data)):
        if re.match('VERSION = "\\d+[\\d_]+"', data[line_index]):
            data[line_index] = re.sub("\\d+[\\d_]+", version, data[line_index])
with open(SCRIPT_DIR + "utilities.py", "w") as f:
    f.writelines(data)

print("Unpacking...")
os.chdir(BASE_DIR)
subprocess.run([os.path.join(dir_name, "apktool_no_pause.bat"), file_path])
os.rename(file_name.split(".")[0], version)

urllib.request.urlretrieve("https://cdn-gr-prod.ludia.net/jw2018/Localization/Localization_JW_2_Global_RUSSIAN.json", BASE_DIR + "Localization_JW_2_Global_RUSSIAN.json")
urllib.request.urlretrieve("https://cdn-gr-prod.ludia.net/jw2018/Localization/Localization_JW_2_Global_ENGLISH.json", BASE_DIR + "Localization_JW_2_Global_ENGLISH.json")

os.chdir(SCRIPT_DIR)
print("Creating map...")
os.system("python generate_map.py")
print("Parsing OnlineOptionCache...")
os.system("python analize_encryption.py")


def show_diff(dir1, dir2):
    subprocess.Popen([KDIFF3_PATH, dir1, dir2], start_new_session=True)


os.chdir(BASE_DIR)
print("Running kdiff3...")
folders = list(filter(lambda x: re.match("\\d+[\\d_]+", x), next(os.walk('.'))[1]))
folders.sort()
prev_folder = folders[-2] if folders[-1] == version else folders[-1]
prev_assets = BASE_DIR + f"{prev_folder}/assets/Database/Assets/"
new_assets = BASE_DIR + f"{version}/assets/Database/Assets/"
show_diff(prev_assets + "Data1/", new_assets + "Data1/")
show_diff(prev_assets + "Data/", new_assets + "Data/")

os.chdir(SCRIPT_DIR)
print("Creating creature dex...")
os.system("python Creaturedex.py")
print("Fixing localization...")
os.system("python Localization.py")
print("Processing last capture...")
os.system("python SplitConversation.py")

from compare import compare
print("Comparing...")
compare(prev_assets + "Data1/", new_assets + "Data1/")

input("Press Enter...")
