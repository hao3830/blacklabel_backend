"""This is routers

"""

# python standard library imports
from email.mime import image
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
from hurry.filesize import size


# code repository sub-package imports
from src.rcode import rcode
from src import rtracer
from src import general_tool

import celery_worker
from src.mongodb import mongo_handler

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
@router.post("/analyse_tool/dataset/analyse")
async def analyse_tool_post_dataset_analyse(
    request: Request,
    ds_id: str = Form(...),
):
    # init variables
    return_result = rcode(1001)

    try:
        start_time = time.time()
        try:
            logger.info("ds_id %s" % ds_id)
        except Exception as e:
            logger.error(e, exc_info=True)
            return_result = rcode(609)
            return
        # Request tracing
        traceid = request.headers.get("rtraceid")
        if traceid is None or traceid == "":
            traceid = rtracer.get_traceid()
        logger.info("trace_id: %s", traceid)

        # TODO processing here
        ds_path = os.path.join(DATASET_FOLDER, ds_id)

        task = celery_worker.process_dataset_analyse.delay(ds_id, ds_path)
        return_result = {**rcode(1000), **{"task_id": task.id}}

    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.get("/analyse_tool/dataset/analyse")
async def analyse_tool_get_dataset_analyse(
    request: Request,
    ds_id: str,
):
    # init variables
    return_result = rcode(1001)

    try:
        start_time = time.time()
        try:
            logger.info("ds_id %s" % ds_id)
        except Exception as e:
            logger.error(e, exc_info=True)
            return_result = rcode(609)
            return
        # Request tracing
        traceid = request.headers.get("rtraceid")
        if traceid is None or traceid == "":
            traceid = rtracer.get_traceid()
        logger.info("trace_id: %s", traceid)

        # TODO processing here
        analyse_result = mongo_handler.get_dataset_analyse(ds_id)
        if "filesize" in analyse_result:
            analyse_result["filesize"]["mean_filesize"] = size(analyse_result["filesize"]["mean_filesize"])
            analyse_result["filesize"]["min_filesize"] = size(analyse_result["filesize"]["min_filesize"])
            analyse_result["filesize"]["max_filesize"] = size(analyse_result["filesize"]["max_filesize"])
            return_result = {**rcode(1000), **{"analyse_result": analyse_result}}
        else:
            return_result = rcode(4001)

    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.get("/analyse_tool/bbox_heatmap")
async def get_bbox_heatmap(request: Request, ds_id: str, img_size: int = 640):
    try:
        # Request tracing
        traceid = request.headers.get("rtraceid")
        if traceid is None or traceid == "":
            traceid = rtracer.get_traceid()
        # logger.info("trace_id: %s", traceid)

        # TODO processing here

        bbox_heatmap_path = os.path.join(DATASET_FOLDER, ds_id, "bbox_heatmap.jpg")
        if not os.path.exists(bbox_heatmap_path):
            NOT_FOUND_PATH = os.path.join(STATIC_FOLDER, "404.jpg")
            return_result = FileResponse(NOT_FOUND_PATH)
            return

        img = cv2.imread(bbox_heatmap_path)

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
