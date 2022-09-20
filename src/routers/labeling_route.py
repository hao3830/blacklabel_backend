"""This is routers

"""

# python standard library imports
import os
import time
import base64
import logging
import traceback
import json
import re
import shutil
import cv2
import gdown

# third-party module or package imports

from typing import Optional, List
from fastapi import File, UploadFile, Form, APIRouter
from fastapi.responses import StreamingResponse
from zipfile import ZipFile
from io import BytesIO

# code repository sub-package imports
from src.rcode import rcode

# load config
with open("config/api.json") as jfile:
    config = json.load(jfile)

DATASET = config["DATASET"]
ANNOTATION_FOLDER = config["ANNOTATION_FOLDER"]
STATIC_FOLDER = config["STATIC_FOLDER"]
# init app
router = APIRouter()

# get logger
logger = logging.getLogger("blacklabel")

@router.post("/labeling/classification")
async def upload_classification(
    data_name: str = Form(...),
    image_zip_file: Optional[UploadFile] = Form(None),
    label_txt_file: Optional[UploadFile] = Form(None),
    image_link_drive: Optional[str] = Form(None),
    label_link_drive: Optional[str] = Form(None),
):

    if image_zip_file is None and image_link_drive is None:
        return rcode(609)

    # create dataset folder
    save_path = os.path.join(DATASET, "classification", data_name)
    annotate_path = os.path.join(ANNOTATION_FOLDER, data_name)

    if os.path.exists(save_path) or os.path.exists(annotate_path):
        return rcode(908)

    os.makedirs(save_path)
    os.makedirs(annotate_path)

    image_preview = {}

    try:
        if image_zip_file is not None:
            # unzip image file
            image_zip = await image_zip_file.read()

            with ZipFile(BytesIO(image_zip)) as zip_file:
                zip_file.extractall(save_path)
        else:
            # download image file
            output = os.path.join(save_path, "images.zip")
            gdown.download_folder(image_link_drive, output)
            while not ".zip" in [os.path.splitext(file)[1] for file in os.listdir(save_path)]:
                time.sleep(2)

            with ZipFile(output) as zip_file:
                zip_file.extractall(save_path)
            os.remove(output)

        if label_txt_file:
            # create classs folder
            with open(label_txt_file) as f:
                label_image_class = f.readlines()
            label_image_class = [l.strip() for l in label_image_class]
        elif label_link_drive:

            # download label file
            output = os.path.join(annotate_path, "label.txt")
            gdown.download(label_link_drive, output)
            while not ".txt" in [os.path.splitext(file)[1] for file in os.listdir(save_path)]:
                time.sleep(2)

            with open(output) as f:
                label_image_class = f.readlines()
            label_image_class = [l.strip() for l in label_image_class]
            os.remove(output)

        if label_image_class:
            for line in label_image_class:
                if len(line) != 2:
                    raise Exception("label file format error")

                os.makedirs(os.path.join(annotate_path, line[1]), exist_ok=True)

                image_path = os.path.join(save_path, line[0])
                label_path = os.path.join(annotate_path, line[1], line[0])

                if line[1] not in image_preview:
                    image_preview[line[1]] = line[0]

                shutil.copy(image_path, label_path)

    except Exception as e:
        logger.error(e, exc_info=True)
        return rcode(609)

    return {
        **rcode(1000),
        "image_preview": image_preview,
    }


@router.put("/labeling/classification")
async def update_classification_label(
    data_name: str = Form(...),
    image_name: str = Form(...),
    new_label: str = Form(...),
    old_label: Optional[str] = Form(None),
):

    image_path = os.path.join(DATASET, "classification", data_name)
    annotate_path = os.path.join(ANNOTATION_FOLDER, data_name)

    save_label_path = os.path.join(annotate_path, data_name)
    label_path = os.path.join(save_label_path, new_label)

    if old_label is not None:
        old_label_path = os.path.join(save_label_path, old_label)

    if not os.path.exists(image_path):
        return rcode(609)

    if not os.path.exists(label_path):
        os.makedirs(label_path)

    # copy image to label folder

    image_path = os.path.join(image_path, image_name)
    if not os.path.exists(image_path):
        return rcode(609)

    label_image_path = os.path.join(label_path, image_name)
    shutil.copyfile(image_path, label_image_path)

    # remove old img in label folder if exist
    if old_label is not None:
        old_label_image_path = os.path.join(old_label_path, image_name)
        if os.path.exists(old_label_image_path):
            os.remove(old_label_image_path)
        if not os.listdir(old_label_path):
            os.rmdir(old_label_path)

    return rcode(1000)
