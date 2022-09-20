"""
mapping_classes.txt
guava => fruit
cantaloupe => fruit
watermelon => fruit
peache => fruit
pomegranate => fruit
tomatoe => fruit
"""

import os

INPUT = "labels"
OUTPATH = "labels_new"
CLASS_FILE = "classes.txt"
MAPPING_CLASS_FILE = "mapping_classes.txt"
NEW_CLASS_FILE = "classes_new.txt"

if not os.path.exists(OUTPATH):
    os.mkdir(OUTPATH)

# read classes.txt
with open(MAPPING_CLASS_FILE, "r") as mf:
    mclass = mf.readlines()
with open(CLASS_FILE, "r") as idf:
    idclass = idf.readlines()

# create mapping class name
mapping_dict = {}
new_cls_list = []
for cls in mclass:
    old_cls, new_cls = [i.strip() for i in cls.split("=>")]
    mapping_dict[old_cls] = new_cls
    if new_cls not in new_cls_list:
        new_cls_list.append(new_cls)
print(mapping_dict)

# create new classes.txt
with open(NEW_CLASS_FILE, "w") as ncf:
    for cls in new_cls_list:
        ncf.write("%s\n" % cls)

# create new mapping dict
mapping_id = {}
for i, cls in enumerate(idclass):
    cls = cls.strip()
    mapping_id[str(i)] = cls
print(mapping_id)

# processing
for fname in os.listdir(INPUT):
    fpath = os.path.join(INPUT, fname)
    with open(fpath, "r") as lf:
        lines = lf.readlines()

    new_fpath = os.path.join(OUTPATH, fname)
    with open(new_fpath, "w") as nlf:
        for line in lines:
            line = line.strip()
            cls_id, center_x, center_y, width, height = line.split(" ")
            new_cls_name = mapping_dict[mapping_id[cls_id]]
            new_cls_id = new_cls_list.index(new_cls_name)
            print(new_cls_id, center_x, center_y, width, height)
            nlf.write("%s %s %s %s %s \n" % (new_cls_id, center_x, center_y, width, height))
