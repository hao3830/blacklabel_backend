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
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.encoders import jsonable_encoder

# code repository sub-package imports
from src.rcode import rcode
from src import rtracer
from src import general_tool

from src.mongodb import mongo_handler
import celery_worker

# init general envs

# load config
with open("config/api.json") as jfile:
    config = json.load(jfile)

RETURN_FORMAT = config["RETURN_FORMAT"]
# load more config here
UPLOAD_FOLDER = config["UPLOAD_FOLDER"]
TMP_FOLDER = config["TMP_FOLDER"]

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
@router.post("/label_tool/create_task")
async def label_tool_create_task(request: Request):
    return_result = rcode(1001)

    try:
        start_time = time.time()

        # Request tracing
        traceid = request.headers.get("rtraceid")
        if traceid is None or traceid == "":
            traceid = rtracer.get_traceid()
        logger.info("trace_id: %s", traceid)

        # TODO processing here
        task = celery_worker.background.delay(5)

        return_result = {**rcode(1000), **{"task_id": task.id}}
    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.get("/label_tool/get_task")
def label_tool_get_task(request: Request, task_id: str):
    return_result = rcode(1001)

    try:
        start_time = time.time()

        # Request tracing
        traceid = request.headers.get("rtraceid")
        if traceid is None or traceid == "":
            traceid = rtracer.get_traceid()
        # logger.info("trace_id: %s", traceid)

        # TODO processing here
        task = celery_worker.process_upload_ds_type1.AsyncResult(task_id)
        if task.state == "SUCCESS":
            return_result = {**rcode("Done"), **{"state": task.state, "result": task.get()}}
        else:
            return_result = {**rcode("Done"), **{"state": task.state}}
    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result
