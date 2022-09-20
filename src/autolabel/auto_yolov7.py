import os
import json
import logging

import cv2
import requests

from src import general_tool

# get logger
logger = logging.getLogger("blacklabel")

# get config
with open("config/api.json") as jfile:
    config = json.load(jfile)

YOLO_SERVICE_URL = config["YOLO_SERVICE_URL"]
AUTOLABEL_IOU_THRESHOLD = config["AUTOLABEL_IOU_THRESHOLD"]

# define function


def predict_yolo(img, conf_thresh):
    file_bytes = cv2.imencode(".jpg", img)[1].tobytes()
    f = {"binary_file": file_bytes}
    data = {"conf_thresh": conf_thresh, "iou_thresh": AUTOLABEL_IOU_THRESHOLD}
    response = requests.post(YOLO_SERVICE_URL, data=data, files=f)
    response = response.json()
    return response


def predict_db(img_folder_path, label_folder_path, conf_thresh):
    cls_list = []
    for fname in os.listdir(img_folder_path):
        fname_woext = ".".join(fname.split(".")[:-1])
        fpath = os.path.join(img_folder_path, fname)
        json_path = os.path.join(label_folder_path, "%s.json" % fname_woext)

        img = cv2.imread(fpath)

        label_list = []
        predict_result = predict_yolo(img, conf_thresh)["predicts"][0]
        for obj in predict_result:
            x1, y1, x2, y2 = [int(i) for i in obj["bbox"]]
            bbox_dict = {}
            bbox_dict["class_name"] = obj["cls"]

            if obj["cls"] not in cls_list:
                cls_list.append(obj["cls"])

            bbox_dict["conf"] = float(obj["conf"])
            bbox_dict["x1"] = x1
            bbox_dict["y1"] = y1
            bbox_dict["x2"] = x2
            bbox_dict["y2"] = y2
            label_list.append(bbox_dict)

        file_size = os.path.getsize(fpath)
        img_width, img_height = general_tool.get_img_shape(fpath)
        label_dict = {"file_name": fname}
        label_dict["image_width"] = img_width
        label_dict["image_height"] = img_height
        label_dict["bboxes"] = label_list
        label_dict["file_size"] = file_size
        label_dict["manual_label"] = 0
        label_dict["set_type"] = ""

        with open(json_path, "w") as json_file:
            json.dump(label_dict, json_file)

    return cls_list


if __name__ == "__main__":
    #    img = cv2.imread("../../test/test.jpg")
    #    result = predict_yolo(img)["predicts"][0]
    #    print(result)
    img_folder_path = "test_frames/6804079649329532161.mp4"
    label_folder_path = "yolo_test"
    predict_db(img_folder_path, label_folder_path)
