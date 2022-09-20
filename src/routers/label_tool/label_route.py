"""This is routers

"""

# python standard library imports
import os
import io
from random import shuffle
import time
import base64
import logging
import traceback
import json
import shutil

# third-party module or package imports
import cv2
import pydantic
import numpy as np
import aiofiles

from io import BytesIO
from zipfile import ZipFile
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import StreamingResponse, FileResponse, Response
from fastapi.encoders import jsonable_encoder

# code repository sub-package imports
from src.rcode import rcode
from src import rtracer
from src import general_tool

import celery_worker
from src.mongodb import mongo_handler
from src.label_tool import uploader
from src.spliter import detection_db_split
from src.label_tool import downloader

# init general envs

# load config
with open("config/api.json") as jfile:
    config = json.load(jfile)

RETURN_FORMAT = config["RETURN_FORMAT"]
# load more config here
UPLOAD_FOLDER = config["UPLOAD_FOLDER"]
DATASET_FOLDER = config["DATASET_FOLDER"]
TMP_FOLDER = config["TMP_FOLDER"]
DS_TYPE = config["DS_TYPE"]
STATIC_FOLDER = config["STATIC_FOLDER"]


# init app
router = APIRouter()

# get logger
logger = logging.getLogger("blacklabel")

# define class
class Images(BaseModel):
    data: Optional[List[str]] = pydantic.Field(default=None, example=None, description="List of base64 encoded images")


class PredictData(BaseModel):
    #    images: Images
    images: Optional[List[str]] = pydantic.Field(
        default=None, example=None, description="List of base64 encoded images"
    )


# TODO load and warm-up model here


# define routes and functions
@router.post("/label_tool/upload_label")
async def label_tool_upload_label(
    request: Request,
    ds_id: str = Form(...),
    label_type: str = Form(...),
    label_file: UploadFile = File(None),
    gdrive_link: str = Form(None),
):
    # init variables
    try:

        if label_file is None and gdrive_link is None:
            assert 2

    except Exception as e:
        logger.error(e, exc_info=True)
        return rcode(609)

    # Request tracing
    traceid = request.headers.get("rtraceid")
    if traceid is None or traceid == "":
        traceid = rtracer.get_traceid()
    logger.info("trace_id: %s", traceid)

    # TODO processing here
    ds_folder = os.path.join(DATASET_FOLDER, ds_id)
    label_json_file = os.path.join(DATASET_FOLDER, ds_id, "labels", "labels.json")

    upload_path = os.path.join(
        TMP_FOLDER,
        ds_id,
    )
    upload_folder = os.path.join(TMP_FOLDER, "%s_folder" % ds_id)
    if not os.path.exists(upload_folder):
        os.mkdir(upload_folder)
    else:
        shutil.rmtree(upload_folder)
        os.mkdir(upload_folder)

    if "classification" in label_type:
        try:

            if gdrive_link is not None:
                task_id = uploader.upload_subs_folder_label(
                    ds_id, label_type, gdrive_link, upload_path, label_json_file
                )
            # read file txt
            else:
                label_file = await label_file.read()
                task_id = uploader.upload_subs_folder_label_by_file(
                    ds_id, ds_folder, label_type, label_file, label_json_file
                )

            return {**rcode(1000), **{"task_id": task_id, "ds_id": ds_id}}

        except Exception as e:
            logger.error(e, exc_info=True)
            return rcode(609)

    elif label_type == "yolo":
        labelzip_file = await label_file.read()
        async with aiofiles.open(upload_path, "wb") as out_file:
            await out_file.write(labelzip_file)

        task_id = uploader.upload_label_obj_detection_yolo(ds_id, ds_folder, label_type, upload_path, upload_folder)

        return {**rcode(1000), **{"task_id": task_id, "ds_id": ds_id}}
    elif label_type == "object_detection_csv":
        labelzip_file = await label_file.read()
        async with aiofiles.open(upload_path, "wb") as out_file:
            await out_file.write(labelzip_file)

        task_id = uploader.upload_label_obj_detection_csv(ds_id, ds_folder, label_type, upload_path, upload_folder)

        return {**rcode(1000), **{"task_id": task_id, "ds_id": ds_id}}


@router.post("/label_tool/split_train_test")
async def split_train_test(
    request: Request,
    response: Response,
    ds_id: str = Form(...),
    train_percent: int = Form(70),
    test_percent: int = Form(15),
    val_percent: int = Form(15),
):
    # init variables
    try:
        logger.info("ds_id %s" % ds_id)
    except Exception as e:
        logger.error(e, exc_info=True)
        return rcode(609)

    # Request tracing
    traceid = request.headers.get("rtraceid")
    if traceid is None or traceid == "":
        traceid = rtracer.get_traceid()
    logger.info("trace_id: %s", traceid)

    # TODO processing here
    ds_folder = os.path.join(DATASET_FOLDER, ds_id)
    image_folder = os.path.join(ds_folder, "images")
    label_folder = os.path.join(ds_folder, "labels")

    train_txt_path = os.path.join(ds_folder, "train.txt")
    test_txt_path = os.path.join(ds_folder, "test.txt")
    val_txt_path = os.path.join(ds_folder, "val.txt")

    train_imglist, val_imglist, test_imglist = detection_db_split.create_split_list(
        image_folder, train_percent, test_percent, val_percent
    )
    with open(train_txt_path, "w") as txt_file:
        for fname in train_imglist:
            fname_woext = ".".join(fname.split(".")[:-1])
            txt_file.write("%s\n" % fname)

            label_file_path = os.path.join(label_folder, "%s.json" % fname_woext)
            with open(label_file_path) as json_file:
                label_json = json.load(json_file)
            label_json["set_type"] = "train"
            with open(label_file_path, "w") as json_file:
                json.dump(label_json, json_file)
    with open(test_txt_path, "w") as txt_file:
        for fname in test_imglist:
            fname_woext = ".".join(fname.split(".")[:-1])
            txt_file.write("%s\n" % fname)

            label_file_path = os.path.join(label_folder, "%s.json" % fname_woext)
            with open(label_file_path) as json_file:
                label_json = json.load(json_file)
            label_json["set_type"] = "test"
            with open(label_file_path, "w") as json_file:
                json.dump(label_json, json_file)
    with open(val_txt_path, "w") as txt_file:
        for fname in val_imglist:
            fname_woext = ".".join(fname.split(".")[:-1])
            txt_file.write("%s\n" % fname)

            label_file_path = os.path.join(label_folder, "%s.json" % fname_woext)
            with open(label_file_path) as json_file:
                label_json = json.load(json_file)
            label_json["set_type"] = "val"
            with open(label_file_path, "w") as json_file:
                json.dump(label_json, json_file)

    return_file = io.BytesIO()
    zip_file = downloader.train_test_txt_file(ds_folder, return_file)
    response.headers["Content-Disposition"] = "attachment; filename=%s_spliter.zip" % ds_id
    return Response(
        content=zip_file.read(),
        media_type="application/x-zip-compressed",
    )
