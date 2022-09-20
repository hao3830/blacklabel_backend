import os
import json


def simplejson2yolo_str(cls_list, simplejson):
    yolostr = ""
    img_width = simplejson["image_width"]
    img_height = simplejson["image_height"]

    for obj in simplejson["bboxes"]:
        cls_name = obj["class_name"]
        if cls_name not in cls_list:
            cls_list.append(cls_name)

        x1 = obj["x1"]
        y1 = obj["y1"]
        x2 = obj["x2"]
        y2 = obj["y2"]
        width = x2 - x1
        height = y2 - y1
        cs_x = float(x1 + (width / 2)) / img_width
        cs_y = float(y1 + (height / 2)) / img_height
        s_width = float(width / img_width)
        s_height = float(height / img_height)

        yolostr += "%s %f %f %f %f\n" % (cls_list.index(cls_name), cs_x, cs_y, s_width, s_height)
    return yolostr.strip()


def simplejson2yolo_db_str(simplejson_folder):
    db_yolo_list = []
    cls_list = []
    for fname in os.listdir(simplejson_folder):
        fname_woext = ".".join(fname.split(".")[:-1])
        fpath = os.path.join(simplejson_folder, fname)
        with open(fpath, "r") as simple_file:
            simplejson = json.load(simple_file)
        yolostr = simplejson2yolo_str(cls_list, simplejson)

        db_yolo_list.append(("%s.txt" % fname_woext, yolostr))
    return cls_list, db_yolo_list


if __name__ == "__main__":
    #    cls_list = []
    #    fpath = "1-500x500_jpg.rf.3ad4b0d86a75b6d60207fd510cc06c81.json"
    #    with open(fpath, "r") as simple_file:
    #        simplejson = json.load(simple_file)
    #    yolostr = simplejson2yolo_str(cls_list, simplejson)
    #    print(yolostr)

    cls_list, db_yolo_list = simplejson2yolo_db_str("simplejson")
    for f in db_yolo_list:
        print(f[0])
        print(f[1])
