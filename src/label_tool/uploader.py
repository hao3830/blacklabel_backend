import os
import json

import requests
import celery_worker

# image classification
def upload_classification_type1(ds_id, ds_folder, label_folder, upload_path, upload_folder):
    task = celery_worker.process_upload_ds_type1.delay(ds_id, ds_folder, label_folder, upload_path, upload_folder)
    return task.id


def upload_classification_type2(ds_id, ds_folder, label_folder, upload_path, upload_folder):
    task = celery_worker.process_upload_ds_type2.delay(ds_id, ds_folder, label_folder, upload_path, upload_folder)
    return task.id


def upload_classification_type3(ds_id, ds_folder, label_folder, gdrive_link, upload_path, upload_folder):
    task = celery_worker.process_upload_ds_type3.delay(
        ds_id, ds_folder, label_folder, gdrive_link, upload_path, upload_folder
    )
    return task.id


def upload_classification_type4(ds_id, ds_folder, label_folder, gdrive_link, upload_path, upload_folder):
    task = celery_worker.process_upload_ds_type4.delay(
        ds_id, ds_folder, label_folder, gdrive_link, upload_path, upload_folder
    )
    return task.id


def upload_label(ds_id, ds_path, label_type, label_file_path):
    return 1


def upload_subs_folder_label(ds_id, label_type, gdrive_link, upload_path, label_json_file):
    task = celery_worker.process_upload_subs_folder_label.delay(
        ds_id, label_type, gdrive_link, upload_path, label_json_file
    )
    return task.id


def upload_subs_folder_label_by_file(ds_id, ds_folder, label_type, label_file, label_json_file):
    label_string = label_file.decode("utf-8")
    task = celery_worker.process_upload_subs_folder_label_by_file.delay(
        ds_id, ds_folder, label_type, label_string, label_json_file
    )
    return task.id


# object detection
def upload_object_detection(ds_id, ds_folder, label_folder, upload_path, upload_folder):
    task = celery_worker.process_upload_obj_detection.delay(ds_id, ds_folder, label_folder, upload_path, upload_folder)
    return task.id


def upload_label_obj_detection_yolo(ds_id, ds_folder, label_type, upload_path, upload_folder):
    task = celery_worker.process_upload_label_obj_detection_yolo.delay(
        ds_id, ds_folder, label_type, upload_path, upload_folder
    )
    return task.id


def upload_label_obj_detection_csv(ds_id, ds_folder, label_type, upload_path, upload_folder):
    task = celery_worker.process_upload_label_obj_detection_csv.delay(
        ds_id, ds_folder, label_type, upload_path, upload_folder
    )
    return task.id
