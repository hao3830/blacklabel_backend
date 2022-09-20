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

# code repository sub-package imports
from src.rcode import rcode
from src import rtracer
from src import general_tool

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
    data: Optional[List[str]] = pydantic.Field(default=None, example=None, description="")


class PredictData(BaseModel):
    #    images: Images
    images: Optional[List[str]] = pydantic.Field(default=None, example=None, description="")


# TODO load and warm-up model here


# define routes and functions
@router.post("/crop/roi")
async def crop_roi():
    # init variables
    logger.info("crop/roi")
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
        fpath = "src/cropper/roi_cropper.py"
        fname = "roi_cropper.py"

        return_result = FileResponse(fpath, media_type="application/octet-stream", filename=fname)

    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result
