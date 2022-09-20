import json


def xywh2yolo(x, y, w, h, imgw, imgh):
    xc = x + w / 2
    yc = y + h / 2
    xc = xc / imgw
    yc = yc / imgh
    w = w / imgw
    h = h / imgh

    xc = min(max(xc, 0), 1)
    yc = min(max(yc, 0), 1)
    w = min(max(w, 0), 1)
    h = min(max(h, 0), 1)

    return (xc, yc, w, h)


def convert_coco_to_yolo(coco_file):
    data = json.loads(coco_file)
    images = data["images"]
    annotations = data["annotations"]

    dict_txt = {}

    for image in images:
        img_id = image["id"]
        img_width = image["width"]
        img_height = image["height"]
        img_name = image["file_name"]
        txt_content = ""

        for annotation in annotations:
            if annotation["image_id"] == img_id:
                bbox = annotation["bbox"]
                xc, yc, w, h = xywh2yolo(
                    x=bbox[0], y=bbox[1], w=bbox[2], h=bbox[3], imgw=img_width, imgh=img_height
                )
                category_id = annotation["category_id"]
                txt_content += f"{category_id} {xc} {yc} {w} {h}\n"

        dict_txt[img_name] = txt_content

    return dict_txt
