import os
import cv2
import requests

classes = [
    "guava",
    "cantaloupe",
    "watermelon",
    "peache",
    "pomegranate",
    "tomato",
    "kiwifruit",
    "pineapple",
    "avocado",
    "orange",
    "apple",
    "banana",
    "passionfruit",
    "grape",
    "apricot",
    "fig",
    "blueberry",
    "lemon",
    "olive",
    "cherry",
    "lime",
    "mango",
    "blackberry",
    "raspberry",
    "pear",
    "acerola",
    "strawberry",
    "plum",
    "coconut",
    "grapefruit",
]


def getbbox(file_path):
    url = "https://aiclub.uit.edu.vn/gpu/service/u2net/predict_bbox_binary"

    f = {"binary_file": open(file_path, "rb")}

    response = requests.post(url, files=f)
    response = response.json()
    #    print(response)
    x1, y1, x2, y2 = response["predicts"][0]

    return x1, y1, x2, y2


if __name__ == "__main__":
    inpath = "fruitdet30"
    out_imgpath = "fruitdet30_img"
    out_labelpath = "fruitdet30_label"

    count = 0
    for dname in os.listdir(inpath):
        cls = dname
        dpath = os.path.join(inpath, dname)
        for fname in os.listdir(dpath):
            count += 1
            try:
                fpath = os.path.join(dpath, fname)
                print(count, fpath)

                fname_woext = ".".join(fname.split(".")[:-1])

                img = cv2.imread(fpath)
                img_height, img_width, _ = img.shape

                newfpath = os.path.join(out_imgpath, "%s.jpg" % fname_woext)
                cv2.imwrite(newfpath, img)

                x1, y1, x2, y2 = getbbox(fpath)
                print(x1, y1, x2, y2)

                width = x2 - x1
                height = y2 - y1

                center_x = x1 + (width / 2)
                center_y = y1 + (height / 2)

                scaled_width = width / img_width
                scaled_height = height / img_height
                scaled_center_x = center_x / img_width
                scaled_center_y = center_y / img_height

                label_path = os.path.join(out_labelpath, "%s.txt" % fname_woext)
                with open(label_path, "w") as f:
                    clsnum = classes.index(cls)
                    label_str = "%s %s %s %s %s" % (
                        clsnum,
                        scaled_center_x,
                        scaled_center_y,
                        scaled_width,
                        scaled_height,
                    )
                    f.write(label_str)

            except:
                True
