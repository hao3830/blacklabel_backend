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


# third-party module or package imports
import cv2
import pydantic
import numpy as np
import aiofiles

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.encoders import jsonable_encoder
from starlette.responses import FileResponse
from zipfile import ZipFile
from io import BytesIO

# code repository sub-package imports
from src.rcode import rcode
from src import rtracer
from src import general_tool
from src.autolabel import auto_yolov7
import celery_worker

# init general envs

# load config
with open("config/api.json") as jfile:
    config = json.load(jfile)

RETURN_FORMAT = config["RETURN_FORMAT"]
# load more config here
UPLOAD_FOLDER = config["UPLOAD_FOLDER"]
TMP_FOLDER = config["TMP_FOLDER"]
DATASET_FOLDER = config["DATASET_FOLDER"]
AUTOLABEL_CONF_THRESHOLD = config["AUTOLABEL_CONF_THRESHOLD"]


# init app
router = APIRouter()

# get logger
logger = logging.getLogger("blacklabel")

# define class
class Images(BaseModel):
    data: Optional[List[str]] = pydantic.Field(default=None, example=None, description="")


class PredictData(BaseModel):
    #    images: Images
    images: Optional[List[str]] = pydantic.Field(default=None, example=None, description="")


# TODO load and warm-up model here


# define routes and functions
@router.post("/autolabel/salient")
async def autolabel_salient(zip_file: UploadFile = File(...)):
    # init variables
    logger.info("autolabel_salient")
    return_result = rcode(1001)

    try:
        start_time = time.time()
        predicts = []
        try:
            True
        except Exception as e:
            logger.error(e, exc_info=True)
            return_result = rcode(609)
            return
        # TODO processing here
        fpath = "src/autolabel/auto_salient.py"
        fname = "auto_salient.py"

        return_result = FileResponse(fpath, media_type="application/octet-stream", filename=fname)

    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.post("/autolabel_tool/object_detection")
async def autolabel_tool_object_detection(
    ds_id: str = Form(...), method: str = Form("yolov7"), conf_thresh: float = Form(None)
):
    # init variables
    return_result = rcode(1001)

    try:
        start_time = time.time()
        predicts = []
        try:
            if conf_thresh is None or conf_thresh == -1:
                conf_thresh = AUTOLABEL_CONF_THRESHOLD
            logger.info("ds_id %s, conf_thresh %s" % (ds_id, conf_thresh))
        except Exception as e:
            logger.error(e, exc_info=True)
            return_result = rcode(609)
            return
        # TODO processing here
        ds_path = os.path.join(DATASET_FOLDER, ds_id)
        img_folder_path = os.path.join(ds_path, "images")
        label_folder_path = os.path.join(ds_path, "labels")

        if method == "yolov7":
            task = celery_worker.process_auto_yolov7.delay(ds_id, img_folder_path, label_folder_path, conf_thresh)
            return_result = {**rcode(1000), **{"task_id": task.id, "ds_id": ds_id}}
        else:
            return rcode(609)
    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.get("/autolabel_tool/method_list")
def autolabel_tool_method_list(request: Request, ds_type: str = Form("object_detection")):
    return_result = rcode(1001)

    try:
        # Request tracing
        traceid = request.headers.get("rtraceid")
        if traceid is None or traceid == "":
            traceid = rtracer.get_traceid()
        # logger.info("trace_id: %s", traceid)

        # TODO processing here
        if ds_type == "object_detection":
            method_list = ["yolov7"]
            return_result = {**rcode(1000), **{"method_list": method_list}}
        else:
            return_result = rcode(609)
    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result
