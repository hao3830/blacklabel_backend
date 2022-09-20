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

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.encoders import jsonable_encoder
from configparser import ConfigParser

# code repository sub-package imports
from src.rcode import rcode
from src import rtracer

# init general envs

# load config
with open("config/api.json") as jfile:
    config = json.load(jfile)

RETURN_FORMAT = config["RETURN_FORMAT"]
# load more config here

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
@router.post("/predict")
async def predict(data: PredictData):
    # init variables
    logger.info("predict")
    return_result = rcode(1001)

    try:
        start_time = time.time()
        predicts = []
        try:
            images = jsonable_encoder(data.images)
        except Exception as e:
            logger.error(e, exc_info=True)
            return_result = rcode(609)
            return

        for image in images:
            image_decoded = base64.b64decode(image)
            jpg_as_np = np.frombuffer(image_decoded, dtype=np.uint8)
            process_image = cv2.imdecode(jpg_as_np, flags=1)
            # uncomment for convert opencv img to pillow img
        #            process_image = cv2.cvtColor(process_image, cv2.COLOR_BGR2RGB)
        #            process_image = Image.fromarray(process_image)

        # TODO processing here

        return_result = {
            **rcode(1000),
            "predicts": predicts,
            "process_time": time.time() - start_time,
            "return": RETURN_FORMAT,
        }
    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.post("/predict_binary")
async def predict_binary(binary_file: UploadFile = File(...)):
    # init variables
    logger.info("predict_binary")
    return_result = rcode(1001)

    try:
        start_time = time.time()
        predicts = []
        try:
            bytes_file = await binary_file.read()
        except Exception as e:
            logger.error(e, exc_info=True)
            return_result = rcode(609)
            return

        nparr = np.fromstring(bytes_file, np.uint8)
        process_image = cv2.imdecode(nparr, flags=1)
        # uncomment for convert opencv img to pillow img
        #        process_image = cv2.cvtColor(process_image, cv2.COLOR_BGR2RGB)
        #        process_image = Image.fromarray(process_image)

        # TODO processing here

        return_result = {
            **rcode(1000),
            "predicts": predicts,
            "process_time": time.time() - start_time,
            "return": RETURN_FORMAT,
        }
    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.post("/predict_multipart")
async def predict_multipart(argument: Optional[float] = Form(...), binary_file: UploadFile = File(...)):
    # init variables
    logger.info("predict_multipart")
    return_result = rcode(1001)

    try:
        start_time = time.time()
        predicts = []
        try:
            bytes_file = await binary_file.read()
        except Exception as e:
            logger.error(e, exc_info=True)
            return_result = rcode(609)
            return

        nparr = np.fromstring(bytes_file, np.uint8)
        process_image = cv2.imdecode(nparr, flags=1)
        # uncomment for convert opencv img to pillow img
        #        process_image = cv2.cvtColor(process_image, cv2.COLOR_BGR2RGB)
        #        process_image = Image.fromarray(process_image)

        # TODO processing here

        return_result = {
            **rcode(1000),
            "predicts": predicts,
            "process_time": time.time() - start_time,
            "return": RETURN_FORMAT,
        }
    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result
