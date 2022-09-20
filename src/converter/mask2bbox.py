import os
import requests

import cv2
import numpy as np


def get_mask(img_path):
    url = "https://aiclub.uit.edu.vn/gpu/service/u2net/predict_stream_multipart"
    f = {"binary_file": open(img_path, "rb")}
    data = {"get_mask_th": 1}

    response = requests.post(url, data=data, files=f)
    with open("mask.png", "wb") as f:
        f.write(response.content)


def mask2bbox(img_mask):

    img_mask1 = cv2.rotate(img_mask, cv2.ROTATE_90_CLOCKWISE)

    min_y, _, _ = np.argwhere(img_mask > 128)[0]
    max_y, _, _ = np.argwhere(img_mask > 128)[-1]
    min_x, _, _ = np.argwhere(img_mask1 > 128)[0]
    max_x, _, _ = np.argwhere(img_mask1 > 128)[-1]

    return min_x, min_y, max_x, max_y


def main():
    img_path = "qua-vai-1560152977-5727-156015-9492-9212-1561699481.png"

    get_mask(img_path)
    img_mask = cv2.imread("mask.png")

    img = cv2.imread(img_path)

    min_x, min_y, max_x, max_y = mask2bbox(img_mask)
    print(min_x, min_y, max_x, max_y)

    new_img = cv2.rectangle(img, (min_x, min_y), (max_x, max_y), (255, 0, 0), 2)

    cv2.imwrite("new_img.jpg", new_img)


if __name__ == "__main__":
    main()
