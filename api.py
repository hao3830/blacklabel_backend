"""This is template for making a api

"""

# python standard library imports
import os
import logging
import time
import datetime
import json

# third-party module or package imports
import uvicorn
import asyncio

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware

# code repository sub-package imports
from src import rlogger
from src import rcode

from src.routers import routers
from src.routers import info_route
from src.routers import convert_route
from src.routers import convert_img_route

from src.routers import stringconvert_route
from src.routers import split_route
from src.routers import autolabel_route
from src.routers import crop_route
from src.routers import map_route
from src.routers import analyze_route
from src.routers import labeling_route

from src.routers.label_tool import dataset_route
from src.routers.label_tool import dataset_img_route
from src.routers.label_tool import label_route


from src.routers.label_tool import task_route
from src.routers.label_tool import annotate_route
from src.routers.analyse_tool import dataset_route as al_dataset_route


# init general envs
now = datetime.datetime.now()

# load config
with open("config/api.json") as jfile:
    config = json.load(jfile)

SERVICE_IP = config["SERVICE_IP"]
SERVICE_PORT = config["SERVICE_PORT"]
LOG_PATH = config["LOG_PATH"]
RETURN_FORMAT = config["RETURN_FORMAT"]
UPLOAD_FOLDER = config["UPLOAD_FOLDER"]
TMP_FOLDER = config["TMP_FOLDER"]
DATASET = config["DATASET"]
DATASET_FOLDER = config["DATASET_FOLDER"]

# init app
app = FastAPI()

origins = [
    "https://aiclub.uit.edu.vn",
    "http://aiclub.uit.edu.vn",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://192.168.28.77:3000",
    "*",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(routers.router)
app.include_router(info_route.router)
app.include_router(convert_route.router)
app.include_router(convert_img_route.router)

app.include_router(stringconvert_route.router)
app.include_router(split_route.router)
app.include_router(autolabel_route.router)
app.include_router(crop_route.router)
app.include_router(map_route.router)
app.include_router(analyze_route.router)
app.include_router(labeling_route.router)

app.include_router(dataset_route.router)
app.include_router(dataset_img_route.router)
app.include_router(label_route.router)


app.include_router(task_route.router)
app.include_router(annotate_route.router)

app.include_router(al_dataset_route.router)


# create folder structure
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(TMP_FOLDER):
    os.makedirs(TMP_FOLDER)
if not os.path.exists(DATASET_FOLDER):
    os.makedirs(DATASET_FOLDER)
# if not os.path.exists(DATASET):
#     os.mkdir(DATASET)

# create logger
log_formatter = logging.Formatter("%(asctime)s %(levelname)s" " %(funcName)s(%(lineno)d) %(message)s")
log_handler = rlogger.BiggerRotatingFileHandler(
    "ali",
    LOG_PATH,
    mode="a",
    maxBytes=2 * 1024 * 1024,
    backupCount=200,
    encoding=None,
    delay=0,
)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)

logger = logging.getLogger("blacklabel")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

logger.info("INIT LOGGER SUCCESSED")


# print app info
print("SERVICE_IP", SERVICE_IP)
print("SERVICE_PORT", SERVICE_PORT)
print("LOG_PATH", LOG_PATH)
print("API READY")


# run app
if __name__ == "__main__":
    uvicorn.run(app, port=SERVICE_PORT, host=SERVICE_IP)
