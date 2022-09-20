import os
import io
import json

import cv2
import zipfile

from src import general_tool
from src.converter import simplejson2yolo


def classification(label_file_path, txt_file):
    with open(label_file_path, "r") as json_file:
        json_content = json.load(json_file)
    for fname in json_content.keys():
        label = str(json_content[fname]["class_name"])
        txt_file.write(("%s, %s\n" % (fname, label)).encode())
    txt_file.seek(0)
    return txt_file


def obj_detection_yolo(label_folder_path, zip_buffer):
    zipf = zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED)
    cls_list, yolo_str_list = simplejson2yolo.simplejson2yolo_db_str(label_folder_path)

    # create classes.txt
    cls_str = ""
    for cls in cls_list:
        cls_str += "%s\n" % cls
    zipf.writestr("classes.txt", io.BytesIO(cls_str.encode()).getvalue())

    # create label for each file
    for (fname, obj) in yolo_str_list:
        data = io.BytesIO(obj.encode())
        zipf.writestr("labels/%s" % fname, data.getvalue())

    zipf.close()
    zip_buffer.seek(0)
    return zip_buffer


def obj_detection_simplejson(label_folder_path, zip_buffer):
    zip_buffer = general_tool.zipdir_bytes(label_folder_path, zip_buffer)
    return zip_buffer


def train_test_txt_file(ds_folder, zip_buffer):
    train_txt_path = os.path.join(ds_folder, "train.txt")
    test_txt_path = os.path.join(ds_folder, "test.txt")
    val_txt_path = os.path.join(ds_folder, "val.txt")

    zipf = zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED)
    zipf.write(train_txt_path, "train.txt")
    zipf.write(test_txt_path, "test.txt")
    zipf.write(val_txt_path, "val.txt")

    zipf.close()
    zip_buffer.seek(0)

    return zip_buffer


def download_ds(ds_path, image_folder_path, label_folder_path, zip_buffer):
    zipf = zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED)

    for fname in os.listdir(image_folder_path):
        fpath = os.path.join(image_folder_path, fname)
        zipf.write(fpath, "images/%s" % fname)

    for fname in os.listdir(label_folder_path):
        fpath = os.path.join(label_folder_path, fname)
        zipf.write(fpath, "labels/%s" % fname)

    zipf.close()
    zip_buffer.seek(0)

    return zip_buffer
