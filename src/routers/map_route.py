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
from src.converter import voc2yolo
from src.converter import sheet2json, json2sheet, voc2coco, coco2yolo, yolo2coco

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
@router.post("/mapper/yolo/class_mapper")
async def mapper_yolo_class_mapper():
    # init variables
    logger.info("mapper_yolo_class_mapper")
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
        fpath = "src/mapper/mapping_yolo_class.py"
        fname = "mapping_yolo_class.py"

        return_result = FileResponse(fpath, media_type="application/octet-stream", filename=fname)

    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result
