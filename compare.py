from utilities import *
import difflib


def compare(path_old, path_new):
    with open(JSON_DIR + "compare.txt", "w") as g:
        for dirpath, dirnames, filenames in os.walk(path_new):
            dirpath_old = dirpath.replace(path_new, path_old)
            dirpath_relative = dirpath.replace(path_new, "")
            for file in filenames:
                if not os.path.exists(dirpath_old + "/" + file):
                    g.write(f"New:\t {dirpath_relative}/{file}\n")
                else:
                    with open(dirpath + "/" + file) as f:
                        text_new = f.readlines()
                    with open(dirpath_old + "/" + file) as f:
                        text_old = f.readlines()
                    s = difflib.SequenceMatcher(a=text_old, b=text_new)
                    r = s.ratio()
                    if r < 0.95:
                        g.write(f"Diff:\t{dirpath_relative}/{file}\t{r:.3}\n")
                    elif r < 1:
                        block_list = s.get_matching_blocks()
                        if len(block_list) > 3:
                            g.write(f"Blocks:\t{dirpath_relative}/{file}\t{len(block_list)}\n")
