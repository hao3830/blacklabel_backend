import os
import random
import shutil
import glob
import time
import cv2

# label format: filename, class_name, x1, y1, x2, y2


def main():
    IMAGE_FOLDER = "input"
    LABEL_FILE_PATH = "labels.txt"
    ROI_PATH = "output"
    if not os.path.exists(ROI_PATH):
        os.mkdir(ROI_PATH)

    with open(LABEL_FILE_PATH, "r") as label_file:
        objs = label_file.readlines()

    for obj in objs:
        obj = obj.strip()

        filename, class_name, x1, y1, x2, y2 = obj.split(",")
        filename_woext = ".".join(filename.split(".")[:-1])
        x1, y1, x2, y2 = [int(i) for i in [x1, y1, x2, y2]]
        fpath = os.path.join(IMAGE_FOLDER, filename)
        class_folder = os.path.join(ROI_PATH, str(class_name))

        img = cv2.imread(fpath)
        roi = img[y1:y2, x1:x2]
        roi_name = "%s_%s.jpg" % (filename_woext, str(time.time))
        roipath = os.path.join(class_folder, roi_name)

        if not os.path.exists(class_folder):
            os.mkdir(class_folder)
        cv2.imwrite(roipath, roi)


if __name__ == "__main__":
    main()
