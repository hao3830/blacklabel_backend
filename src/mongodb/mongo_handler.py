import json
import logging
import datetime

import pymongo

# load config
with open("config/api.json") as jfile:
    config = json.load(jfile)

# load logger
logger = logging.getLogger("blacklabel")


MONGO_USERNAME = config["MONGO_USERNAME"]
MONGO_PASSWORD = config["MONGO_PASSWORD"]


mongo_client = pymongo.MongoClient("mongodb://%s:%s@mongo:27017/" % (MONGO_USERNAME, MONGO_PASSWORD))


def create_dataset(ds_id, ds_name, ds_type, ds_path):
    mydb = mongo_client["blacklabel_database"]
    mycol = mydb["dataset"]

    now = datetime.datetime.now()
    create_time = now.strftime("%Y-%m-%d %H:%M:%S")

    mydict = {
        "ds_id": ds_id,
        "ds_name": ds_name,
        "ds_type": ds_type,
        "ds_path": ds_path,
        "class_list": [],
        "create_time": create_time,
        "update_time": create_time,
    }

    result = mycol.insert_one(mydict)
    return result


def list_dataset():
    mydb = mongo_client["blacklabel_database"]
    mycol = mydb["dataset"]
    result = list(mycol.find({}, {"_id": 0}))
    return result


def get_dataset_info(ds_id):
    mydb = mongo_client["blacklabel_database"]
    mycol = mydb["dataset"]
    result = mycol.find_one({"ds_id": ds_id}, {"_id": 0})
    return result


def update_dataset(ds_id, ds_name, ds_type, ds_path, class_list):
    now = datetime.datetime.now()
    update_time = now.strftime("%Y-%m-%d %H:%M:%S")

    mydb = mongo_client["blacklabel_database"]
    mycol = mydb["dataset"]

    if ds_name is not None:
        myquery = {"ds_id": ds_id}
        newvalues = {"$set": {"ds_name": ds_name}}
        result = mycol.update_one(myquery, newvalues)
    if class_list is not None:
        myquery = {"ds_id": ds_id}
        newvalues = {"$set": {"class_list": class_list}}
        result = mycol.update_one(myquery, newvalues)

    myquery = {"ds_id": ds_id}
    newvalues = {"$set": {"update_time": update_time}}
    result = mycol.update_one(myquery, newvalues)
    return result


def add_class_dataset(ds_id, class_name):
    mydb = mongo_client["blacklabel_database"]
    mycol = mydb["dataset"]

    find_result = mycol.find_one({"ds_id": ds_id}, {"_id": 0, "class_list": 1})
    if find_result is not None:
        class_list = list(find_result["class_list"])
        if class_name not in class_list:
            class_list.append(class_name)
        myquery = {"ds_id": ds_id}
        newvalues = {"$set": {"class_list": class_list}}
        result = mycol.update_one(myquery, newvalues)
    else:
        result = -1
    return result


def replace_class_dataset(ds_id, old_class_name, new_class_name):
    mydb = mongo_client["blacklabel_database"]
    mycol = mydb["dataset"]

    find_result = mycol.find_one({"ds_id": ds_id}, {"_id": 0, "class_list": 1})
    if find_result is not None:
        class_list = list(find_result["class_list"])
        if old_class_name in class_list:
            class_list[class_list.index(old_class_name)] = new_class_name
        myquery = {"ds_id": ds_id}
        newvalues = {"$set": {"class_list": class_list}}
        result = mycol.update_one(myquery, newvalues)
    else:
        result = -1
    return result


def is_dataset_exist(ds_name):
    mydb = mongo_client["blacklabel_database"]
    mycol = mydb["dataset"]
    result = mycol.find_one({"ds_name": ds_name})
    return result is not None


def update_dataset_analyse(ds_id, img_num, class_data, mean_imgsize, filesize):
    now = datetime.datetime.now()
    update_time = now.strftime("%Y-%m-%d %H:%M:%S")

    mydb = mongo_client["blacklabel_database"]
    mycol = mydb["dataset"]

    if img_num is not None:
        myquery = {"ds_id": ds_id}
        newvalues = {"$set": {"img_num": img_num}}
        result = mycol.update_one(myquery, newvalues)
    if class_data is not None:
        myquery = {"ds_id": ds_id}
        newvalues = {"$set": {"class_data": class_data}}
        result = mycol.update_one(myquery, newvalues)

    if mean_imgsize is not None:
        myquery = {"ds_id": ds_id}
        newvalues = {"$set": {"mean_imgsize": mean_imgsize}}
        result = mycol.update_one(myquery, newvalues)
    if filesize is not None:
        myquery = {"ds_id": ds_id}
        newvalues = {"$set": {"filesize": filesize}}
        result = mycol.update_one(myquery, newvalues)

    myquery = {"ds_id": ds_id}
    newvalues = {"$set": {"update_time": update_time}}
    result = mycol.update_one(myquery, newvalues)
    return result


def get_dataset_analyse(ds_id):
    mydb = mongo_client["blacklabel_database"]
    mycol = mydb["dataset"]
    result = mycol.find_one({"ds_id": ds_id}, {"_id": 0})
    return result
