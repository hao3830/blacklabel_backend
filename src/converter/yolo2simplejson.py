import os
from pathlib import Path
import json
import re

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


def yolo2simplejson(img_path, cls_list, yolo_label_path, json_label_path):
    img_filename = img_path.split("/")[-1]
    width, height = get_img_shape(img_path)
    with open(yolo_label_path, "r") as yolo_file:
        yolo_label = yolo_file.readlines()

    json_file = open(json_label_path, "w")
    label_list = []
    for line in yolo_label:
        line = line.strip()
        cls_id, scale_cx, scale_cy, scale_w, scale_h = [float(i) for i in line.split(" ")]
        bbox_cx = scale_cx * width
        bbox_cy = scale_cy * height
        bbox_width = scale_w * width
        bbox_height = scale_h * height

        x1 = int(bbox_cx - (bbox_width / 2))
        y1 = int(bbox_cy - (bbox_height / 2))
        x2 = int(bbox_cx + (bbox_width / 2))
        y2 = int(bbox_cy + (bbox_height / 2))

        bbox_dict = {}
        bbox_dict["class_name"] = cls_list[int(cls_id)]
        bbox_dict["x1"] = x1
        bbox_dict["y1"] = y1
        bbox_dict["x2"] = x2
        bbox_dict["y2"] = y2

        label_list.append(bbox_dict)

    file_size = os.path.getsize(img_path)

    label_dict = {"file_name": img_filename}
    label_dict["image_width"] = width
    label_dict["image_height"] = height
    label_dict["bboxes"] = label_list
    label_dict["file_size"] = file_size
    label_dict["manual_label"] = 0
    label_dict["set_type"] = ""

    json.dump(label_dict, json_file)

    json_file.close()


def yolo2simplejson_db(img_folder, yolo_folder, json_folder):
    yolo_folder = Path(yolo_folder)

    # load class list
    cls_list_path = os.path.join(yolo_folder, "classes.txt")
    with open(cls_list_path, "r") as cls_file:
        cls_list = cls_file.readlines()
    cls_list = [cls.strip() for cls in cls_list]
    print(cls_list)

    for fname in os.listdir(img_folder):
        img_path = os.path.join(img_folder, fname)
        fname_woext = ".".join(fname.split(".")[:-1])
        yolo_label_path = list(yolo_folder.glob("%s.*" % fname_woext))[0]
        json_label_path = os.path.join(json_folder, "%s.json" % fname_woext)
        yolo2simplejson(img_path, cls_list, yolo_label_path, json_label_path)

    return cls_list


if __name__ == "__main__":
    #    cls_list = ["pineapple"]
    #    img_path = "000002_fake_B_png.rf.73c0fff550877063cedcc73d1971467b.jpg"
    #    yolo_label_path = "000002_fake_B_png.rf.73c0fff550877063cedcc73d1971467b.txt"
    #    json_label_path = "000002_fake_B_png.rf.73c0fff550877063cedcc73d1971467b.json"
    #    yolo2simplejson(img_path, cls_list, yolo_label_path, json_label_path)

    img_folder = "images"
    yolo_folder = "yolo"
    json_folder = "json"
    yolo2simplejson_db(img_folder, yolo_folder, json_folder)
