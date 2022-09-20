import os
import json

import numpy as np
import cv2


def create_heatmap(img_folder, label_folder, width, height):
    heatmap = np.zeros((height, width))

    for fname in os.listdir(img_folder):
        # print(fname)
        fname_woext = ".".join(fname.split(".")[:-1])
        label_path = os.path.join(label_folder, "%s.json" % fname_woext)
        with open(label_path, "r") as label_file:
            label_json = json.load(label_file)
        img_width = label_json["image_width"]
        img_height = label_json["image_height"]
        for bbox in label_json["bboxes"]:
            #            print(bbox)
            class_name = bbox["class_name"]
            x1 = int(bbox["x1"] * width / img_width)
            y1 = int(bbox["y1"] * height / img_height)
            x2 = int(bbox["x2"] * width / img_width)
            y2 = int(bbox["y2"] * height / img_height)
            heatmap[y1:y2, x1:x2] = heatmap[y1:y2, x1:x2] + 1

    # cv2.imwrite("heatmap1.jpg", heatmap)
    heatmapshow = None
    heatmap = cv2.normalize(heatmap, heatmapshow, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    heatmapshow = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

    # cv2.imwrite("heatmap.jpg", heatmapshow)
    return heatmapshow


if __name__ == "__main__":
    img_folder = "image"
    label_folder = "labels"
    create_heatmap(img_folder, label_folder)
