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
import io

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

from src.mongodb import mongo_handler
from src.label_tool import uploader
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
@router.get("/label_tool/list_dataset")
async def label_tool_list_dataset(request: Request):
    # logger.info("label_tool_list_dataset")
    return_result = rcode(1001)

    try:
        start_time = time.time()

        # Request tracing
        traceid = request.headers.get("rtraceid")
        if traceid is None or traceid == "":
            traceid = rtracer.get_traceid()
        logger.info("trace_id: %s", traceid)

        # TODO processing here
        ds_list = mongo_handler.list_dataset()

        return_result = {**rcode(1000), **{"ds_list": ds_list}}
    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.get("/label_tool/dataset_detail")
def get_dataset_detail(
    request: Request,
    ds_id: str,
):
    logger.info("label_tool_dataset_detail")
    return_result = rcode(1001)

    try:
        # Request tracing
        traceid = request.headers.get("rtraceid")
        if traceid is None or traceid == "":
            traceid = rtracer.get_traceid()
        logger.info("trace_id: %s", traceid)

        # TODO processing here
        list_labels = []
        list_images = []
        dataset_type = ""

        row = mongo_handler.get_dataset_info(ds_id)
        ds_type = row["ds_type"]

        images_path = os.path.join(DATASET_FOLDER, "%s" % (ds_id), "images")

        # edit type dataset
        if "classification" in ds_type:
            dataset_type = "image classification"

            list_images = os.listdir(images_path)

            list_labels = row["class_list"]

        elif ds_type == "object_detection":
            dataset_type = "object detection"
            list_images = os.listdir(images_path)
            list_labels = row["class_list"]

        return_result = {
            **rcode(1000),
            "data_detail": {"list_labels": list_labels, "list_images": list_images, "dataset_type": dataset_type},
        }

    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.post("/label_tool/create_dataset")
async def label_tool_create_dataset(request: Request, ds_name: str = Form(...), ds_type: str = Form(...)):
    # init variables
    # logger.info("label_tool_create_dataset")
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
        # Request tracing
        traceid = request.headers.get("rtraceid")
        if traceid is None or traceid == "":
            traceid = rtracer.get_traceid()
        logger.info("trace_id: %s", traceid)

        # TODO processing here
        ds_id = general_tool.gen_uuid()

        ds_folder = os.path.join(DATASET_FOLDER, "%s" % (ds_id))
        os.mkdir(ds_folder)

        upload_folder = os.path.join(DATASET_FOLDER, "%s" % (ds_id), "images")
        os.mkdir(upload_folder)

        mongo_handler.create_dataset(ds_id, ds_name, ds_type, "/")

        return_result = rcode(1000)

    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.post("/label_tool/upload_dataset")
async def label_tool_upload_dataset(
    request: Request,
    ds_name: str = Form(...),
    ds_type: str = Form(...),
    dataset_zip_file: UploadFile = File(None),
    gdrive_link: str = Form(None),
):
    # init variables
    return_result = rcode(1001)
    upload_path = ""

    try:
        start_time = time.time()
        predicts = []
        try:
            if ds_type not in DS_TYPE:
                assert 1
            if dataset_zip_file is None and gdrive_link is None:
                assert 2
            if dataset_zip_file is not None:
                dataset_zip = await dataset_zip_file.read()
            logger.info("ds_name: %s ,ds_type: %s" % (ds_name, ds_type))
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
        ds_id = general_tool.gen_uuid()

        upload_path = os.path.join(
            TMP_FOLDER,
            ds_id,
        )

        ds_folder = os.path.join(DATASET_FOLDER, ds_id)
        os.mkdir(ds_folder)

        upload_folder = os.path.join(DATASET_FOLDER, ds_id, "images")
        os.mkdir(upload_folder)

        label_folder = os.path.join(DATASET_FOLDER, ds_id, "labels")
        os.mkdir(label_folder)

        if ds_type == "classification_type1":  # upload direct zipfile, subfolder
            ds_type = "image_classification"
            async with aiofiles.open(upload_path, "wb") as out_file:
                await out_file.write(dataset_zip)
            task_id = uploader.upload_classification_type1(ds_id, ds_folder, label_folder, upload_path, upload_folder)
        elif ds_type == "classification_type2":  # upload direct zipfile, all image in one folder
            ds_type = "image_classification"
            async with aiofiles.open(upload_path, "wb") as out_file:
                await out_file.write(dataset_zip)
            task_id = uploader.upload_classification_type2(ds_id, ds_folder, label_folder, upload_path, upload_folder)
        elif ds_type == "classification_type3":  # upload zipfile using google drive, subfolder
            ds_type = "image_classification"
            task_id = uploader.upload_classification_type3(
                ds_id, ds_folder, label_folder, gdrive_link, upload_path, upload_folder
            )
        elif ds_type == "classification_type4":  # upload zipfile using google drive, all image in one folder
            ds_type = "image_classification"
            task_id = uploader.upload_classification_type4(
                ds_id, ds_folder, label_folder, gdrive_link, upload_path, upload_folder
            )
        elif ds_type == "object_detection":
            ds_type = "object_detection"
            async with aiofiles.open(upload_path, "wb") as out_file:
                await out_file.write(dataset_zip)
            task_id = uploader.upload_object_detection(ds_id, ds_folder, label_folder, upload_path, upload_folder)
        else:
            return_result = rcode(609)
            return

        # add dataset to mongodb
        mongo_handler.create_dataset(ds_id, ds_name, ds_type, ds_folder)

        return_result = {**rcode(1000), **{"task_id": task_id, "ds_id": ds_id}}

    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.put("/label_tool/update_dataset")
async def label_tool_update_dataset(
    request: Request,
    ds_id: str = Form(...),
    ds_name: str = Form(None),
    ds_type: str = Form(None),
    class_list: List[str] = Form(None),
):
    # init variables
    return_result = rcode(1001)

    try:
        start_time = time.time()
        try:
            1
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

        mongo_handler.update_dataset(ds_id, ds_name, ds_type, "", class_list)

        return_result = rcode(1000)

    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.post("/label_tool/add_class_dataset")
async def label_tool_add_class_dataset(
    request: Request,
    ds_id: str = Form(...),
    class_name: str = Form(...),
):
    # init variables
    return_result = rcode(1001)

    try:
        start_time = time.time()
        try:
            logger.info("ds_id %s" % ds_id)
            logger.info("class_name %s" % class_name)
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

        result = mongo_handler.add_class_dataset(ds_id, class_name)
        if result == -1:
            return_result = rcode("NotFound")
        else:
            return_result = rcode(1000)

    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.post("/label_tool/replace_class_dataset")
async def label_tool_replace_class_dataset(
    request: Request,
    ds_id: str = Form(...),
    old_class_name: str = Form(...),
    new_class_name: str = Form(...),
):
    # init variables
    return_result = rcode(1001)

    try:
        start_time = time.time()
        try:
            logger.info("ds_id %s" % ds_id)
            logger.info("old_class_name %s" % old_class_name)
            logger.info("new_class_name %s" % new_class_name)
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

        result = mongo_handler.replace_class_dataset(ds_id, old_class_name, new_class_name)

        label_file_path = os.path.join(DATASET_FOLDER, ds_id, "labels", "labels.json")
        with open(label_file_path, "r") as json_file:
            label_content = json.load(json_file)
        for fname in label_content.keys():
            if label_content[fname] == old_class_name:
                label_content[fname] = new_class_name
        with open(label_file_path, "w") as json_file:
            json.dump(label_content, json_file)

        if result == -1:
            return_result = rcode("NotFound")
        else:
            return_result = rcode(1000)

    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.get("/label_tool/dataset/download")
def download_ds(
    ds_id: str,
    response: Response,
    annotation_type: str = None,
):
    try:
        return_file = io.BytesIO()

        ds_info = mongo_handler.get_dataset_info(ds_id)
        if ds_info is None:
            return rcode(614)

        ds_type = ds_info["ds_type"]
        ds_path = os.path.join(DATASET_FOLDER, ds_id)
        image_folder_path = os.path.join(DATASET_FOLDER, ds_id, "images")
        label_folder_path = os.path.join(DATASET_FOLDER, ds_id, "labels")

        zip_file = downloader.download_ds(ds_path, image_folder_path, label_folder_path, return_file)
        response.headers["Content-Disposition"] = "attachment; filename=%s_dataset.zip" % ds_id
        return Response(content=zip_file.read(), media_type="application/x-zip-compressed", headers=response.headers)
    except Exception as e:
        logger.error(e, exc_info=True)
        return rcode(1001)
    finally:
        return_file.close()
