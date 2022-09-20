
from turtle import width


def yolo2xywh(xc, yc, w, h, imgw, imgh):
    xc = xc * imgw
    yc = yc * imgh
    w = w * imgw
    h = h * imgh
    x = xc  - w / 2
    y = yc  - h / 2
    return int(x), int(y), int(w), int(h)

def create_image_annotation(img_name: str, width: int, height: int, image_id: int):
    image_annotation = {
        "file_name": img_name,
        "height": height,
        "width": width,
        "id": image_id,
    }
    return image_annotation

def create_annotation_from_yolo_format(
    xc, yc, w, h,img_size, image_id, category_id, annotation_id, segmentation=False
):
    min_x, min_y, width, height = yolo2xywh(xc, yc, w, h, img_size[1], img_size[0])
    area = width * height
    max_x = min_x + width
    max_y = min_y + height

    bbox = [min_x, min_y, width, height]

    if segmentation:
        seg = [[min_x, min_y, max_x, min_y, max_x, max_y, min_x, max_y]]
    else:
        seg = []
    annotation = {
        "id": annotation_id,
        "image_id": image_id,
        "bbox": bbox,
        "area": area,
        "iscrowd": 0,
        "category_id": category_id,
        "segmentation": seg,
    }

    return annotation

def create_categories(categories):
    categories_list = []
    index = 0
    for category in categories:
        category_dict = {
            "supercategory": "none",
            "id": index,
            "name": category,
        }
        categories_list.append(category_dict)
        index += 1
    return categories_list

def convert_yolo_to_coco(
    b_string,
    img_info,
    labels,
    image_id,
    coco_format
):
    annotation_id = 0
    categories = create_categories(labels)
    coco_format["categories"] = categories
    lines = b_string.splitlines()
    
    images = create_image_annotation(img_info[image_id]["file_name"], img_info[image_id]["width"], img_info[image_id]["height"], image_id)
    coco_format["images"].append(images)

    for line in lines:
        line = line.strip()
        if line == "":
            continue
        line = line.split()
        category_id = int(line[0])
        xc, yc, w, h = float(line[1]), float(line[2]), float(line[3]), float(line[4])

        

        annotation = create_annotation_from_yolo_format(
            xc, yc, w, h,(img_info[image_id]["width"], img_info[image_id]["height"]), image_id, category_id, annotation_id
        )
        coco_format["annotations"].append(annotation)
        
        annotation_id += 1
    return coco_format
