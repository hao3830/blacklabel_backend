import os
import json
import logging

# get logger
logger = logging.getLogger("blacklabel")

# get config
with open("config/api.json") as jfile:
    config = json.load(jfile)

DATASET_FOLDER = config["DATASET_FOLDER"]

# define function
def update_label_obj_detection(ds_id, class_list, image_name, obj_list):
    img_name_woext = ".".join(image_name.split(".")[:-1])

    ds_path = os.path.join(DATASET_FOLDER, ds_id)
    label_path = os.path.join(ds_path, "labels", "%s.json" % img_name_woext)
    with open(label_path) as label_file:
        label_json = json.load(label_file)
    label_list = label_json["bboxes"]

    for obj in obj_list:
        class_name = obj[0]
        bbox = obj[1]
        x1, y1, x2, y2 = bbox
        bbox_dict = {}
        bbox_dict["class_name"] = class_name
        bbox_dict["x1"] = x1
        bbox_dict["y1"] = y1
        bbox_dict["x2"] = x2
        bbox_dict["y2"] = y2

        if bbox_dict not in label_list:
            label_list.append(bbox_dict)

    label_json["manual_label"] = 1
    with open(label_path, "w") as label_file:
        json.dump(label_json, label_file)
