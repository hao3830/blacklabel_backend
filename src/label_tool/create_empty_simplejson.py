import os
import re
from pathlib import Path
import json

import cv2
import magic


def get_img_shape(img_path):
    width = 0
    height = 0
    file_magic = magic.from_file(img_path)
    regex_result = re.findall("(\d+)x(\d+)", file_magic)
    if len(regex_result) > 1:
        width, height = regex_result[1]
    else:
        width, height = regex_result[0]

    return int(width), int(height)


def create_simplejson(img_path, json_label_path):
    file_name = img_path.split("/")[-1]
    file_size = os.path.getsize(img_path)
    width, height = get_img_shape(img_path)

    json_file = open(json_label_path, "w")
    label_list = []

    label_dict = {"file_name": file_name}
    label_dict["image_width"] = width
    label_dict["image_height"] = height
    label_dict["file_size"] = file_size
    label_dict["bboxes"] = label_list
    label_dict["manual_label"] = 0
    label_dict["set_type"] = ""
    json.dump(label_dict, json_file)

    json_file.close()


def create_simplejson_db(img_folder, json_folder):
    for fname in os.listdir(img_folder):
        img_path = os.path.join(img_folder, fname)
        fname_woext = ".".join(fname.split(".")[:-1])
        json_label_path = os.path.join(json_folder, "%s.json" % fname_woext)
        create_simplejson(img_path, json_label_path)


if __name__ == "__main__":
    img_folder = "image"
    json_folder = "simplejson"
    create_simplejson_db(img_folder, json_folder)
