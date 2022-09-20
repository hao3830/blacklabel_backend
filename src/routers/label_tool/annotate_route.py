# python standard library imports
import os
import time
import io
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
from src.mongodb import mongo_handler
from src.label_tool import downloader
from src.label_tool import label_handler

router = APIRouter()

# get logger
logger = logging.getLogger("blacklabel")

# get config
with open("config/api.json") as jfile:
    config = json.load(jfile)

DATASET_FOLDER = config["DATASET_FOLDER"]

# define model
class Annotation(BaseModel):
    ds_id: str
    image_name: str
    class_name: str = ""
    bbox_list: List[List] = []


@router.get("/label_tool/annotate")
def get_annotate(
    ds_id: str,
):
    labels = []
    images = []
    image_size = []
    list_labels = []
    try:

        row = mongo_handler.get_dataset_info(ds_id)
        ds_type = row["ds_type"]
        image_folder_path = os.path.join(DATASET_FOLDER, ds_id, "images")
        label_folder_path = os.path.join(DATASET_FOLDER, ds_id, "labels")
        if "classification" in ds_type:
            label_file_path = os.path.join(label_folder_path, "labels.json")
            labels_data = json.loads(open(label_file_path).read())

            for image in labels_data:
                labels.append(labels_data[image]["class_name"])
                image_size.append([labels_data[image]["image_width"], labels_data[image]["image_height"]])
                images.append(image)

            list_labels = row["class_list"]
        elif ds_type == "object_detection":
            for label_fname in os.listdir(label_folder_path):
                label_file_path = os.path.join(label_folder_path, label_fname)
                with open(label_file_path) as label_file:
                    label_json = json.load(label_file)

                label_list = label_json["bboxes"]
                image_size.append([label_json["image_width"], label_json["image_height"]])
                image_fname = label_json["file_name"]
                labels.append(label_list)
                images.append(image_fname)

                for box in label_list:
                    if box["class_name"] not in list_labels:
                        list_labels.append(box["class_name"])
        else:
            labels = []
            images = os.listdir(image_folder_path)

        return {
            **rcode(1000),
            "results": {
                "labels": labels,
                "images": images,
                "list_labels": list_labels,
                "ds_type": ds_type,
                "image_size": image_size,
            },
        }
    except Exception as e:
        logger.error(e, exc_info=True)
        return rcode(1001)


@router.put("/label_tool/annotate")
def annotate(data: Annotation):
    try:
        row = mongo_handler.get_dataset_info(data.ds_id)
        ds_type = row["ds_type"]
        class_list = row["class_list"]

        if "classification" in ds_type:
            label_json_path = os.path.join(DATASET_FOLDER, data.ds_id, "labels", "labels.json")
            labels_data = json.loads(open(label_json_path).read())

            if data.class_name not in class_list:
                return rcode(609)

            labels_data[data.image_name]["class_name"] = data.class_name

            with open(label_json_path, "w") as f:
                f.write(json.dumps(labels_data))
            return rcode(1000)
        elif ds_type == "object_detection":
            label_handler.update_label_obj_detection(data.ds_id, class_list, data.image_name, data.bbox_list)

        return rcode(1000)
    except Exception as e:
        logger.error(e, exc_info=True)
        return rcode(1001)


@router.get("/label_tool/annotation/download")
def download_annotate(
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

        image_folder_path = os.path.join(DATASET_FOLDER, ds_id, "images")
        label_folder_path = os.path.join(DATASET_FOLDER, ds_id, "labels")
        if "classification" in ds_type:
            label_file_path = os.path.join(DATASET_FOLDER, ds_id, "labels", "labels.json")
            return_file = downloader.classification(label_file_path, return_file)
            response.headers["Content-Disposition"] = "attachment; filename=labels.txt"

            return Response(
                content=return_file.read(),
                media_type="text/plain",
                headers=response.headers,
            )
        elif ds_type == "object_detection":
            if annotation_type == "yolo":
                zip_file = downloader.obj_detection_yolo(label_folder_path, return_file)
                response.headers["Content-Disposition"] = "attachment; filename=%s_yolo_labels.zip" % ds_id
                return Response(
                    content=zip_file.read(),
                    media_type="application/x-zip-compressed",
                    headers=response.headers,
                )
            elif annotation_type == "simplejson":
                zip_file = downloader.obj_detection_simplejson(label_folder_path, return_file)
                response.headers["Content-Disposition"] = "attachment; filename=%s_simplejson_labels.zip" % ds_id
                return Response(
                    content=zip_file.read(),
                    media_type="application/x-zip-compressed",
                    headers=response.headers,
                )
            else:
                return rcode(1000)
        else:
            return rcode(1201)
    except Exception as e:
        logger.error(e, exc_info=True)
        return rcode(1001)
    finally:
        return_file.close()
