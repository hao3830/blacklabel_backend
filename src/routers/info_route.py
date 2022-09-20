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

SERVICE_IP = config["SERVICE_IP"]
SERVICE_PORT = config["SERVICE_PORT"]
LOG_PATH = config["LOG_PATH"]
RETURN_FORMAT = config["RETURN_FORMAT"]
SERVICE_INFO = config["SERVICE_INFO"]
VERSION = config["VERSION"]

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


@router.get("/info")
async def info(request: Request):
    logger.info("info")
    return_result = rcode(1001)

    try:
        start_time = time.time()

        # Request tracing
        traceid = request.headers.get("rtraceid")
        if traceid is None or traceid == "":
            traceid = rtracer.get_traceid()
        logger.info("trace_id: %s", traceid)

        return_result = {
            **rcode(1000),
            **{
                "traceid": traceid,
                "info": SERVICE_INFO,
                "version": VERSION,
                "process_time": time.time() - start_time,
                "return": RETURN_FORMAT,
            },
        }
    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result
