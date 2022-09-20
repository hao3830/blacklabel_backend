import os

import cv2


def yolo2txt(img_path, yolo_label_path, txt_label_path):
    img = cv2.imread(img_path)
    height, width, _ = img.shape
    with open(yolo_label_path, "r") as yolo_file:
        yolo_label = yolo_file.readlines()

    txt_file = open(txt_label_path, "w")

    for line in yolo_label:
        line = line.strip()
        cls_id, scale_cx, scale_cy, scale_w, scale_h = [float(i) for i in line.split(" ")]
        bbox_cx = scale_cx * width
        bbox_cy = scale_cy * height
        bbox_width = scale_w * width
        bbox_height = scale_h * height

        x1 = int(bbox_cx - (bbox_width / 2))
        y1 = int(bbox_cy - (bbox_height / 2))
        x2 = int(bbox_cx + (bbox_width / 2))
        y2 = int(bbox_cy + (bbox_height / 2))
        print(x1, y1, x2, y2)
        txt_file.write("%s, %d, %d, %d, %d" % (cls_id, x1, y1, x2, y2))
    txt_file.close()


if __name__ == "__main__":
    img_path = "000002_fake_B_png.rf.73c0fff550877063cedcc73d1971467b.jpg"
    yolo_label_path = "000002_fake_B_png.rf.73c0fff550877063cedcc73d1971467b.txt"
    txt_label_path = "000002_fake_B_png.rf.73c0fff550877063cedcc73d1971467b.txt.txt"
    yolo2txt(img_path, yolo_label_path, txt_label_path)
