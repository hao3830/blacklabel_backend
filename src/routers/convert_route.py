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
@router.post("/convert/voc2yolo")
async def voc2yolo_route(
    image_zip_file: UploadFile = File(...),
    label_zip_file: UploadFile = File(...),
    class_txt_file: UploadFile = File(...),
):
    # init variables
    logger.info("convert/voc2yolo")
    return_result = rcode(1001)

    try:
        start_time = time.time()
        try:
            img_zip = await image_zip_file.read()
            label_zip = await label_zip_file.read()
            class_txt = await class_txt_file.read()
        except Exception as e:
            logger.error(e, exc_info=True)
            return_result = rcode(609)
            return

        # TODO processing here
        upload_id = str(general_tool.gen_id(32))
        img_upload_path = os.path.join(UPLOAD_FOLDER, "%s_img.zip" % upload_id)
        label_upload_path = os.path.join(UPLOAD_FOLDER, "%s_label.zip" % upload_id)
        class_upload_path = os.path.join(UPLOAD_FOLDER, "%s_class.txt" % upload_id)

        async with aiofiles.open(img_upload_path, "wb") as out_file:
            await out_file.write(img_zip)
        async with aiofiles.open(label_upload_path, "wb") as out_file:
            await out_file.write(label_zip)
        async with aiofiles.open(class_upload_path, "wb") as out_file:
            await out_file.write(class_txt)

        # create tmp folder for unzip
        unzipped_img_path = os.path.join(TMP_FOLDER, "%s_img" % upload_id)
        unzipped_label_path = os.path.join(TMP_FOLDER, "%s_label" % upload_id)
        yolo_path = os.path.join(TMP_FOLDER, "%s_yolo" % upload_id)
        general_tool.recreate_dir(unzipped_img_path)
        general_tool.recreate_dir(unzipped_label_path)
        general_tool.recreate_dir(yolo_path)

        # unzip uploaded file
        general_tool.unzip(img_upload_path, unzipped_img_path)
        general_tool.unzip(label_upload_path, unzipped_label_path)

        # load class list
        with open(class_upload_path, "r") as txt_file:
            classes = txt_file.readlines()
            classes = [line.rstrip() for line in classes]
            logger.info("classes: %s" % classes)

        voc2yolo.voc2yolo_db(unzipped_img_path, classes, unzipped_label_path, yolo_path)
        # create classes.txt
        class_fpath = os.path.join(yolo_path, "classes.txt")
        with open(class_fpath, "w") as class_file:
            for item in classes:
                class_file.write("%s\n" % item)

        # zip yolo annotation to file
        yolo_fname = "%s_yolo.zip" % upload_id
        yolo_fpath = os.path.join(TMP_FOLDER, yolo_fname)
        general_tool.zipdir(yolo_path, yolo_fpath)

        return_result = FileResponse(yolo_fpath, media_type="application/octet-stream", filename=yolo_fname)

    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.post("/convert/sheet2json")
async def sheet2json_route(
    sheet_zip_file: UploadFile = File(...),
):
    # init variables
    logger.info("convert/sheet2json")
    return_result = rcode(1001)

    try:
        start_time = time.time()
        try:
            sheet_zip = await sheet_zip_file.read()
        except Exception as e:
            logger.error(e, exc_info=True)
            return_result = rcode(609)
            return

        # TODO processing here
        upload_id = str(general_tool.gen_id(32))
        sheet_upload_path = os.path.join(UPLOAD_FOLDER, "%s.zip" % upload_id)

        async with aiofiles.open(sheet_upload_path, "wb") as out_file:
            await out_file.write(sheet_zip)

        # create tmp folder for unzip
        unzipped_sheet_path = os.path.join(TMP_FOLDER, "%s_sheet" % upload_id)
        json_path = os.path.join(TMP_FOLDER, "%s_json" % upload_id)
        general_tool.recreate_dir(unzipped_sheet_path)
        general_tool.recreate_dir(json_path)

        # unzip uploaded file
        general_tool.unzip(sheet_upload_path, unzipped_sheet_path)

        # convert
        sheet2json.sheet2json_db(unzipped_sheet_path, json_path)

        # zip yolo annotation to file
        json_fname = "%s_json.zip" % upload_id
        json_fpath = os.path.join(TMP_FOLDER, json_fname)
        general_tool.zipdir(json_path, json_fpath)

        return_result = FileResponse(json_fpath, media_type="application/octet-stream", filename=json_fname)

    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.post("/convert/json2sheet")
async def json2sheet_route(
    json_zip_file: UploadFile = File(...),
):
    # init variables
    logger.info("convert/json2sheet")
    return_result = rcode(1001)

    try:
        start_time = time.time()
        try:
            json_zip = await json_zip_file.read()
        except Exception as e:
            logger.error(e, exc_info=True)
            return_result = rcode(609)
            return

        # TODO processing here
        upload_id = str(general_tool.gen_id(32))
        json_upload_path = os.path.join(UPLOAD_FOLDER, "%s.zip" % upload_id)

        async with aiofiles.open(json_upload_path, "wb") as out_file:
            await out_file.write(json_zip)

        # create tmp folder for unzip
        unzipped_json_path = os.path.join(TMP_FOLDER, "%s_json" % upload_id)
        sheet_path = os.path.join(TMP_FOLDER, "%s_sheet" % upload_id)
        general_tool.recreate_dir(unzipped_json_path)
        general_tool.recreate_dir(sheet_path)

        # unzip uploaded file
        general_tool.unzip(json_upload_path, unzipped_json_path)

        # convert
        json2sheet.json2sheet_db(unzipped_json_path, sheet_path)

        # zip yolo annotation to file
        sheet_fname = "%s_sheet.zip" % upload_id
        sheet_fpath = os.path.join(TMP_FOLDER, sheet_fname)
        general_tool.zipdir(sheet_path, sheet_fpath)

        return_result = FileResponse(sheet_fpath, media_type="application/octet-stream", filename=sheet_fname)

    except Exception as e:
        logger.error(e, exc_info=True)
        return_result = rcode(1001)
    finally:
        return return_result


@router.post("/convert/voc2coco")
async def convert_coco_from_pascal(
    pascal_voc_zip_file: UploadFile = File(...), class_txt_file: UploadFile = File(...)
):

    logger.info("Converting from Pascal VOC XML to COCO JSON")

    try:
        label_list = class_txt_file.file.read().decode("utf-8").split("\n")
        pascal_voc_zip = await pascal_voc_zip_file.read()
    except Exception as e:
        logger.error(e)
        return rcode(609)

    label_list = [l.strip() for l in label_list]
    label2id = voc2coco.get_label2id(label_list)

    coco_format = {"images": [], "categories": [], "annotations": [], "info": {}, "licenses": {}}

    for label, label_id in label2id.items():
        category_info = {"supercategory": "none", "id": label_id, "name": label}
        coco_format["categories"].append(category_info)

    try:
        with ZipFile(BytesIO(pascal_voc_zip)) as zf:
            xml_files = zf.filelist

            for xml_file in xml_files:
                data = ZipFile.read(zf, xml_file)

                coco_json, err = voc2coco.convert_xmls_to_cocojson(BytesIO(data), label2id)

                if err:
                    return err

                coco_format["images"] += coco_json["images"]
                coco_format["annotations"] += coco_json["annotations"]

    except Exception as e:
        logger.error(e)
        return rcode(609)

    return StreamingResponse(
        BytesIO(json.dumps(coco_format, indent=4).encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment;filename=%s" % "result.json"},
    )


@router.post("/convert/coco2yolo")
async def convert_yolo_from_coco(coco_file: UploadFile = File(...)):

    try:
        coco_file = coco_file.file.read()
    except Exception as e:
        logger.error(e)
        return rcode(609)

    yolo_zip_file = BytesIO()

    dict_txt = coco2yolo.convert_coco_to_yolo(coco_file)
    with ZipFile(yolo_zip_file, "w") as zf:
        for img in dict_txt:
            img_ext = img.split(".")[-1]
            zf.writestr(img.replace(img_ext, "txt"), dict_txt[img])

    return StreamingResponse(
        iter([yolo_zip_file.getvalue()]),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment;filename=%s" % "result.zip"},
    )


@router.post("/convert/yolo2coco")
async def convert_coco_from_yolo(
    yolo_zip_file: UploadFile = File(...),
    image_zip_file: UploadFile = File(...),
    class_txt_file: UploadFile = File(...),
):

    logger.info("Converting from YOLO to COCO JSON")
    coco_format = {"images": [], "categories": [], "annotations": [], "info": {}, "licenses": {}}

    try:
        yolo_zip = await yolo_zip_file.read()
        image_zip = await image_zip_file.read()
        label_list = class_txt_file.file.read().decode("utf-8").split("\n")
    except Exception as e:
        logger.error(e)
        return rcode(609)

    label_list = [l.strip() for l in label_list]
    try:
        with ZipFile(BytesIO(image_zip)) as zf:
            image_files = zf.filelist
            image_info = []
            for image_file in image_files:
                info = {"file_name": image_file.filename, "width": 0, "height": 0}
                width, height = general_tool.read_img_size(ZipFile.read(zf, image_file))
                info["width"] = width
                info["height"] = height
                image_info.append(info)

        with ZipFile(BytesIO(yolo_zip)) as zf:
            yolo_files = zf.filelist
            image_id = 0
            for yolo_file in yolo_files:
                coco_format = yolo2coco.convert_yolo_to_coco(
                    ZipFile.read(zf, yolo_file), image_info, label_list, image_id, coco_format
                )
                image_id += 1
    except Exception as e:
        logger.error(e)
        return rcode(609)

    return StreamingResponse(
        BytesIO(json.dumps(coco_format, indent=4).encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment;filename=%s" % "result.json"},
    )
