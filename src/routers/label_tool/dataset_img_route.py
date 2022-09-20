"""This is routers

"""

# python standard library imports
import os
import time
import base64
import logging
import traceback
import json

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
@router.get("/label_tool/dataset_img")
async def get_ds_image(
    request: Request,
    ds_id: str,
    img_id: str,
    img_size: int = 300,
):
    try:
        # Request tracing
        traceid = request.headers.get("rtraceid")
        if traceid is None or traceid == "":
            traceid = rtracer.get_traceid()
        # logger.info("trace_id: %s", traceid)

        # TODO processing here

        img_folder_path = os.path.join(DATASET_FOLDER, ds_id, "images")
        img_path = os.path.join(img_folder_path, img_id)

        if not os.path.exists(img_path):
            NOT_FOUND_PATH = os.path.join(STATIC_FOLDER, "404.jpg")
            return_result = FileResponse(NOT_FOUND_PATH)
            return

        img = cv2.imread(img_path)

        # height, width, _ = img.shape
        new_width = int(img_size)
        # new_height = int(new_width * height / width)

        img = cv2.resize(img, (int(new_width), int(new_width)))
        res, im_jpg = cv2.imencode(".jpg", img)

        return_result = Response(content=im_jpg.tobytes(), media_type="image/jpeg")

    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.get("/label_tool/dataset_img_list")
async def get_ds_image(
    request: Request,
    ds_id: str,
):
    try:
        # Request tracing
        traceid = request.headers.get("rtraceid")
        if traceid is None or traceid == "":
            traceid = rtracer.get_traceid()
        # logger.info("trace_id: %s", traceid)

        # TODO processing here

        img_folder_path = os.path.join(DATASET_FOLDER, ds_id, "images")

        img_list = []
        if os.path.exists(img_folder_path):
            img_list = os.listdir(img_folder_path)

        return_result = {**rcode(1000), **{"img_list": img_list}}

    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result
