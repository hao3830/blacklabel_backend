import os
import re
import json

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


def csv2simplejson_db(img_folder_path, csv_label_path, json_folder_path, with_header=True):
    with open(csv_label_path, "r") as csv_file:
        csv_label = csv_file.readlines()

    file_dict = {}
    cls_list = []

    obj_list = csv_label[1:]
    for obj in obj_list:
        obj = obj.strip()
        fname, cls_name, conf, x1, y1, x2, y2 = obj.split(",")
        x1, y1, x2, y2 = [int(i) for i in [x1, y1, x2, y2]]
        if fname not in file_dict:
            file_dict[fname] = [[cls_name, conf, x1, y1, x2, y2]]
        else:
            file_dict[fname].append([cls_name, conf, x1, y1, x2, y2])

    for fname in file_dict.keys():
        fname_woext = ".".join(fname.split(".")[:-1])
        img_path = os.path.join(img_folder_path, fname)
        json_label_path = os.path.join(json_folder_path, "%s.json" % fname_woext)
        file_name = img_path.split("/")[-1]
        file_size = os.path.getsize(img_path)
        width, height = get_img_shape(img_path)

        json_file = open(json_label_path, "w")
        label_list = []

        for obj in file_dict[fname]:
            bbox_dict = {}
            bbox_dict["class_name"] = obj[0]
            bbox_dict["conf"] = obj[1]
            bbox_dict["x1"] = obj[2]
            bbox_dict["y1"] = obj[3]
            bbox_dict["x2"] = obj[4]
            bbox_dict["y2"] = obj[5]
            label_list.append(bbox_dict)

            if obj[0] not in cls_list:
                cls_list.append(obj[0])

        label_dict = {"file_name": file_name}
        label_dict["image_width"] = width
        label_dict["image_height"] = height
        label_dict["file_size"] = file_size
        label_dict["bboxes"] = label_list
        label_dict["manual_label"] = 0
        label_dict["set_type"] = ""

        json.dump(label_dict, json_file)

        json_file.close()

    return cls_list


if __name__ == "__main__":
    img_folder_path = "image"
    csv_label_path = "2044_250822.csv"
    json_folder_path = "simplejson"
    csv2simplejson_db(img_folder_path, csv_label_path, json_folder_path, with_header=True)
