import os
import shutil
import xml.etree.ElementTree as ET

import cv2
import numpy as np


def parse_xml(img_path, classes, xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    size = root.find("size")
    w = int(size.find("width").text)
    h = int(size.find("height").text)
    bboxes = []
    labels = []
    bboxes_ignore = []
    labels_ignore = []
    for obj in root.findall("object"):
        name = obj.find("name").text
        label = classes.index(name)
        difficult = int(obj.find("difficult").text)
        bnd_box = obj.find("bndbox")
        bbox = [
            int(bnd_box.find("xmin").text),
            int(bnd_box.find("ymin").text),
            int(bnd_box.find("xmax").text),
            int(bnd_box.find("ymax").text),
        ]
        if difficult:
            bboxes_ignore.append(bbox)
            labels_ignore.append(label)
        else:
            bboxes.append(bbox)
            labels.append(label)

    annotation = {
        "filename": img_path,
        "width": w,
        "height": h,
        "ann": {
            "bboxes": bboxes,
            "labels": labels,
            "bboxes_ignore": bboxes_ignore,
            "labels_ignore": labels_ignore,
        },
    }
    return annotation


def voc2yolo(img_path, classes, voc_path, yolo_path):
    anno = parse_xml(img_path, classes, voc_path)
    img_h = anno["height"]
    img_w = anno["width"]

    with open(yolo_path, "w") as yolo_file:
        for bbox, label in zip(anno["ann"]["bboxes"], anno["ann"]["labels"]):
            class_id = label
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            center_x = bbox[0] + width / 2
            center_y = bbox[1] + height / 2
            scaled_center_x = center_x / img_w
            scaled_center_y = center_y / img_h
            scaled_width = width / img_w
            scaled_height = height / img_h
            line = "%d %f %f %f %f \n" % (
                class_id,
                scaled_center_x,
                scaled_center_y,
                scaled_width,
                scaled_height,
            )
            yolo_file.write(line)


def voc2yolo_db(img_folder, classes, voc_folder, yolo_folder):
    if not os.path.exists(yolo_folder):
        os.mkdir(yolo_folder)
    else:
        shutil.rmtree(yolo_folder)
        os.mkdir(yolo_folder)

    for img_fname in os.listdir(img_folder):
        img_fname_woext = img_fname.split(".")[0]
        img_path = os.path.join(img_folder, img_fname)

        voc_fname = "%s.xml" % img_fname_woext
        voc_fpath = os.path.join(voc_folder, voc_fname)

        yolo_fname = "%s.txt" % img_fname_woext
        yolo_fpath = os.path.join(yolo_folder, yolo_fname)

        voc2yolo(img_path, classes, voc_fpath, yolo_fpath)


def main():
    img_folder = "images"
    voc_folder = "annotations"
    yolo_folder = "yolo_anno"
    classes = ["tomato"]
    voc2yolo_db(img_folder, classes, voc_folder, yolo_folder)


if __name__ == "__main__":
    main()
