import logging
import json
import time
import os
import re
import zipfile
import shutil
import random

from pathlib import Path

import cv2
import numpy as np
from celery import Celery
from celery.signals import after_setup_logger

import magic

from src import rlogger
from src import gdrive
from src.mongodb import mongo_handler
from src.converter import yolo2simplejson
from src.converter import csv2simplejson
from src.label_tool import create_empty_simplejson
from src.analyse_tool import heatmap
from src.autolabel import auto_yolov7
from src.spliter import detection_db_split

# load config
with open("config/api.json") as jfile:
    config = json.load(jfile)

LOG_PATH = config["LOG_PATH"]

# init celery
celery = Celery("celery_task", backend="redis://redis:6379/10", broker="redis://redis:6379/11")
# define celery logger
@after_setup_logger.connect()
def setup_loggers(logger, *args, **kwargs):

    log_formatter = logging.Formatter("%(asctime)s %(levelname)s" " %(filename)s %(funcName)s(%(lineno)d) %(message)s")
    log_handler = rlogger.BiggerRotatingFileHandler(
        "celery",
        LOG_PATH,
        mode="a",
        maxBytes=2 * 1024 * 1024,
        backupCount=200,
        encoding=None,
        delay=0,
    )
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)


@celery.task()
def background(n):
    delay = 5
    print("Task running")
    time.sleep(delay)
    print("Task complete")

    return 0


@celery.task()
def process_upload_ds_type1(ds_id, ds_folder, label_folder, upload_path, upload_folder):

    img_folder_path = os.path.join(ds_folder, "images")

    with zipfile.ZipFile(upload_path, "r") as zip_ref:
        zip_ref.extractall(upload_folder)

    class_list = os.listdir(upload_folder)
    class_num = len(class_list)

    record = {}

    for class_name in class_list:
        class_path = os.path.join(upload_folder, class_name)
        for img_name in os.listdir(class_path):

            # get image size
            img_path = os.path.join(class_path, img_name)
            file_size = os.path.getsize(img_path)
            file_magic = magic.from_file(img_path)
            width, height = re.findall("(\d+)x(\d+)", file_magic)[1]

            record[img_name] = {
                "class_name": class_name,
                "image_width": int(width),
                "image_height": int(height),
                "file_size": file_size,
            }
            image_path = os.path.join(class_path, img_name)
            save_image_path = os.path.join(upload_folder, img_name)
            shutil.move(image_path, save_image_path)
        # remove class folder
        shutil.rmtree(class_path)

    # update class_list to mongodb
    mongo_handler.update_dataset(ds_id=ds_id, ds_name=None, ds_type=None, ds_path=None, class_list=class_list)
    # create labels.json
    label_file_path = os.path.join(label_folder, "labels.json")
    if not os.path.exists(label_file_path):
        with open(label_file_path, "w") as f:
            f.write(json.dumps(record, indent=4))

    if os.path.exists(upload_path):
        os.remove(upload_path)
    return {"ds_id": ds_id, "class_num": class_num, "class_list": class_list}


@celery.task()
def process_upload_ds_type2(ds_id, ds_folder, label_folder, upload_path, upload_folder):
    img_folder_path = os.path.join(ds_folder, "images")

    with zipfile.ZipFile(upload_path, "r") as zip_ref:
        zip_ref.extractall(upload_folder)

    file_list = os.listdir(upload_folder)
    file_num = len(file_list)

    data_label = {}

    for img_name in file_list:
        # get image size
        img_path = os.path.join(img_folder_path, img_name)
        file_size = os.path.getsize(img_path)
        file_magic = magic.from_file(img_path)
        width, height = re.findall("(\d+)x(\d+)", file_magic)[1]

        data_label[img_name] = {
            "class_name": "None",
            "image_width": int(width),
            "image_height": int(height),
            "file_size": file_size,
        }
    # create labels.json
    label_file_path = os.path.join(label_folder, "labels.json")
    if not os.path.exists(label_file_path):
        with open(label_file_path, "w") as label_file:
            json.dump(data_label, label_file)

    if os.path.exists(upload_path):
        os.remove(upload_path)
    return {"ds_id": ds_id, "file_num": file_num}


@celery.task()
def process_upload_ds_type3(ds_id, ds_folder, label_folder, gdrive_link, upload_path, upload_folder):
    gdrive.download_gdrive_file(gdrive_link, upload_path)

    img_folder_path = os.path.join(ds_folder, "images")
    label_path = upload_folder.replace("images", "labels")

    with zipfile.ZipFile(upload_path, "r") as zip_ref:
        zip_ref.extractall(label_path)

    class_list = os.listdir(label_path)
    class_num = len(class_list)

    data_label = {}

    for img_name in class_list:
        # get image size
        img_path = os.path.join(img_folder_path, img_name)
        file_size = os.path.getsize(img_path)
        file_magic = magic.from_file(img_path)
        width, height = re.findall("(\d+)x(\d+)", file_magic)[1]

        data_label[img_name] = {
            "class_name": "None",
            "image_width": int(width),
            "image_height": int(height),
            "file_size": file_size,
        }

    # create labels.json
    label_file_path = os.path.join(label_folder, "labels.json")
    if not os.path.exists(label_file_path):
        with open(label_file_path, "w") as label_file:
            json.dump(data_label, label_file)

    if os.path.exists(upload_path):
        os.remove(upload_path)
    return {"ds_id": ds_id, "class_num": class_num, "class_list": class_list}


@celery.task()
def process_upload_ds_type4(ds_id, ds_folder, label_folder, gdrive_link, upload_path, upload_folder):
    img_folder_path = os.path.join(ds_folder, "images")

    gdrive.download_gdrive_file(gdrive_link, upload_path)

    with zipfile.ZipFile(upload_path, "r") as zip_ref:
        zip_ref.extractall(upload_folder)

    class_list = os.listdir(upload_folder)
    class_num = len(class_list)

    record = {}

    for class_name in class_list:
        class_path = os.path.join(upload_folder, class_name)

        for img_name in os.listdir(class_path):
            img_path = os.path.join(class_path, img_name)
            file_size = os.path.getsize(img_path)
            file_magic = magic.from_file(img_path)
            width, height = re.findall("(\d+)x(\d+)", file_magic)[1]

            record[img_name] = {
                "class_name": class_name,
                "image_width": int(width),
                "image_height": int(height),
                "file_size": file_size,
            }

            save_image_path = os.path.join(upload_folder, img_name)
            shutil.move(img_path, save_image_path)
        shutil.rmtree(class_path)

    # update class_list to mongodb
    mongo_handler.update_dataset(ds_id=ds_id, ds_name=None, ds_type=None, ds_path=None, class_list=class_list)
    # create labels.json
    label_file_path = os.path.join(label_folder, "labels.json")
    if not os.path.exists(label_file_path):
        with open(label_file_path, "w") as f:
            f.write(json.dumps(record, indent=4))

    if os.path.exists(upload_path):
        os.remove(upload_path)
    return {"ds_id": ds_id, "class_num": class_num, "class_list": class_list}


@celery.task()
def process_upload_subs_folder_label(ds_id, label_type, gdrive_link, upload_path, label_json_file):
    txt_path = upload_path + "label.txt"
    gdrive.download_gdrive_file(gdrive_link, txt_path)
    record = {}
    with open(txt_path) as f:
        lines = f.readlines()
        lines = [x.strip() for x in lines]
        lines = [x.split("\t") for x in lines]

    for line in lines:
        if len(line) != 2:
            assert 1
        class_name = line[0]
        image_name = line[1]
        record[image_name] = class_name

    with open(label_json_file, "w") as f:
        f.write(json.dumps(record, indent=4))

    return {"ds_id": ds_id, "class_num": len(record), "class_list": record.keys()}


@celery.task()
def process_upload_subs_folder_label_by_file(ds_id, ds_folder, label_type, label_string, label_json_file):

    img_folder_path = os.path.join(ds_folder, "images")

    if os.path.exists(label_json_file):
        labels_data = json.loads(open(label_json_file).read())
    else:
        labels_data = {}

    class_list = []

    label_list = label_string.split("\n")
    for line in label_list:
        if line == "":
            continue
        line = line.split(",")

        if len(line) != 2:
            print("error", line)
            continue

        img_name = line[0].strip()
        label = line[1].strip()

        # get image size
        img_path = os.path.join(img_folder_path, img_name)
        file_size = os.path.getsize(img_path)
        file_magic = magic.from_file(img_path)
        width, height = re.findall("(\d+)x(\d+)", file_magic)[1]

        labels_data[img_name] = {
            "class_name": label,
            "image_width": int(width),
            "image_height": int(height),
            "file_size": file_size,
        }

        if label not in class_list:
            class_list.append(label)

    mongo_handler.update_dataset(ds_id=ds_id, ds_name=None, ds_type=None, ds_path=None, class_list=class_list)

    with open(label_json_file, "w") as f:
        json.dump(labels_data, f)

    return {"ds_id": ds_id, "class_num": len(class_list), "class_list": class_list}


# object detection
@celery.task()
def process_upload_obj_detection(ds_id, ds_folder, label_folder, upload_path, upload_folder):
    with zipfile.ZipFile(upload_path, "r") as zip_ref:
        zip_ref.extractall(upload_folder)

    dir_nested = None
    for fname in os.listdir(upload_folder):
        if os.path.isdir(os.path.join(upload_folder, fname)):
            dir_nested = fname

    if dir_nested is not None:
        subdir_path = os.path.join(upload_folder, dir_nested)
        for image_name in os.listdir(subdir_path):
            img_path = os.path.join(subdir_path, image_name)
            shutil.move(img_path, upload_folder)
        # remove class folder
        shutil.rmtree(subdir_path)

    file_list = os.listdir(upload_folder)
    file_num = len(file_list)
    for fname in file_list:
        fpath = os.path.join(upload_folder, fname)
        fname_woext = ".".join(fname.split(".")[:-1])
        label_file_path = os.path.join(label_folder, "%s.json" % fname_woext)
        create_empty_simplejson.create_simplejson(fpath, label_file_path)

    if os.path.exists(upload_path):
        os.remove(upload_path)
    return {"ds_id": ds_id, "file_num": file_num, "class_num": 0, "class_list": []}


@celery.task()
def process_upload_label_obj_detection_yolo(ds_id, ds_folder, label_type, upload_path, upload_folder):
    with zipfile.ZipFile(upload_path, "r") as zip_ref:
        zip_ref.extractall(upload_folder)

    dir_nested = None
    for fname in os.listdir(upload_folder):
        if os.path.isdir(os.path.join(upload_folder, fname)):
            dir_nested = fname

    if dir_nested is not None:
        dir_nested_path = os.path.join(upload_folder, dir_nested)
        for fname in os.listdir(dir_nested_path):
            shutil.move(os.path.join(dir_nested_path, fname), upload_folder)
        os.rmdir(dir_nested_path)

    file_list = os.listdir(upload_folder)
    file_num = len(file_list)

    image_folder = Path(ds_folder, "images")
    label_folder = Path(ds_folder, "labels")

    if label_folder.exists():
        shutil.rmtree(label_folder)
        os.mkdir(label_folder)
    else:
        os.mkdir(label_folder)

    # create label json file
    cls_list = yolo2simplejson.yolo2simplejson_db(image_folder, upload_folder, label_folder)

    # update class_list to mongodb
    mongo_handler.update_dataset(ds_id=ds_id, ds_name=None, ds_type=None, ds_path=None, class_list=cls_list)

    if os.path.exists(upload_path):
        os.remove(upload_path)
    return {"ds_id": ds_id, "file_num": file_num}


@celery.task()
def process_upload_label_obj_detection_csv(ds_id, ds_folder, label_type, upload_path, upload_folder):
    image_folder = Path(ds_folder, "images")
    label_folder = Path(ds_folder, "labels")

    if label_folder.exists():
        shutil.rmtree(label_folder)
        os.mkdir(label_folder)
    else:
        os.mkdir(label_folder)

    # create label json file
    cls_list = csv2simplejson.csv2simplejson_db(image_folder, upload_path, label_folder)

    # update class_list to mongodb
    mongo_handler.update_dataset(ds_id=ds_id, ds_name=None, ds_type=None, ds_path=None, class_list=cls_list)

    if os.path.exists(upload_path):
        os.remove(upload_path)
    return {"ds_id": ds_id}


# analyser
@celery.task()
def process_dataset_analyse(ds_id, ds_path):
    img_folder_path = os.path.join(ds_path, "images")
    label_folder_path = os.path.join(ds_path, "labels")

    ds_info = mongo_handler.get_dataset_info(ds_id)
    ds_type = ds_info["ds_type"]

    img_num = len(os.listdir(img_folder_path))

    class_data = {}
    class_data["obj_in_class"] = {}
    width_list = []
    height_list = []
    area_list = []
    filesize_list = []

    if ds_type == "image_classification":
        label_file_path = os.path.join(label_folder_path, "labels.json")
        with open(label_file_path, "r") as label_file:
            label_json = json.load(label_file)

        for fname in label_json.keys():
            label = label_json[fname]["class_name"]
            img_width = int(label_json[fname]["image_width"])
            img_height = int(label_json[fname]["image_height"])
            width_list.append(img_width)
            height_list.append(img_height)
            area_list.append(img_width * img_height)
            filesize_list.append(int(label_json[fname]["file_size"]))
            if not label in class_data["obj_in_class"]:
                class_data["obj_in_class"][label] = 1
            else:
                class_data["obj_in_class"][label] += 1

        most_class = max(class_data["obj_in_class"], key=class_data["obj_in_class"].get)
        least_class = min(class_data["obj_in_class"], key=class_data["obj_in_class"].get)
        class_data["most_class"] = (most_class, class_data["obj_in_class"][most_class])
        class_data["least_class"] = (least_class, class_data["obj_in_class"][least_class])

    elif ds_type == "object_detection":
        for fname in os.listdir(label_folder_path):
            fpath = os.path.join(label_folder_path, fname)
            with open(fpath, "r") as label_file:
                label_json = json.load(label_file)

            img_width = int(label_json["image_width"])
            img_height = int(label_json["image_height"])
            width_list.append(img_width)
            height_list.append(img_height)
            area_list.append(img_width * img_height)
            filesize_list.append(int(label_json["file_size"]))
            for bbox in label_json["bboxes"]:
                label = bbox["class_name"]
                if not label in class_data["obj_in_class"]:
                    class_data["obj_in_class"][label] = 1
                else:
                    class_data["obj_in_class"][label] += 1

            if class_data["obj_in_class"] != {}:
                most_class = max(class_data["obj_in_class"], key=class_data["obj_in_class"].get)
                least_class = min(class_data["obj_in_class"], key=class_data["obj_in_class"].get)
                class_data["most_class"] = (most_class, class_data["obj_in_class"][most_class])
                class_data["least_class"] = (least_class, class_data["obj_in_class"][least_class])
            else:
                class_data["most_class"] = (-1, -1)
                class_data["least_class"] = (-1, -1)

    mean_width = float(np.mean(width_list))
    min_width = int(np.min(width_list))
    max_width = int(np.max(width_list))
    mean_height = float(np.mean(height_list))
    min_height = int(np.min(height_list))
    max_height = int(np.max(height_list))
    mean_area = float(np.mean(area_list))
    min_area = int(np.min(area_list))
    max_area = int(np.max(area_list))
    mean_imgsize = {
        "mean_width": mean_width,
        "min_width": min_width,
        "max_width": max_width,
        "mean_height": mean_height,
        "min_height": min_height,
        "max_height": max_height,
        "mean_area": mean_area,
        "min_area": min_area,
        "max_area": max_area,
    }
    mean_filesize = float(np.mean(filesize_list))
    min_filesize = float(np.min(filesize_list))
    max_filesize = float(np.max(filesize_list))
    filesize = {"mean_filesize": mean_filesize, "min_filesize": min_filesize, "max_filesize": max_filesize}
    mongo_handler.update_dataset_analyse(ds_id, img_num, class_data, mean_imgsize, filesize)

    if ds_type == "object_detection":
        # create bbox heatmap
        bbox_heatmap_path = os.path.join(ds_path, "bbox_heatmap.jpg")
        bbox_heatmap = heatmap.create_heatmap(img_folder_path, label_folder_path, max_width, max_height)
        cv2.imwrite(bbox_heatmap_path, bbox_heatmap)

    return {"ds_id": ds_id, "img_num": img_num, "ds_type": ds_type}


# auto labeling
@celery.task()
def process_auto_yolov7(ds_id, img_folder_path, label_folder_path, conf_thresh):
    cls_list = auto_yolov7.predict_db(img_folder_path, label_folder_path, conf_thresh)
    mongo_handler.update_dataset(ds_id=ds_id, ds_name=None, ds_type=None, ds_path=None, class_list=cls_list)
    return {"ds_id": ds_id}
