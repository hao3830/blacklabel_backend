import os
import re
import xml.etree.ElementTree as ET
from typing import Dict, List
from src.rcode import rcode


def get_label2id(labels_str: str) -> Dict[str, int]:
    """id is 1 start"""
    labels_ids = list(range(1, len(labels_str) + 1))
    return dict(zip(labels_str, labels_ids))


def get_annpaths(
    ann_dir_path: str = None,
    ann_ids_path: str = None,
    ext: str = "",
    annpaths_list_path: str = None,
) -> List[str]:
    # If use annotation paths list
    if annpaths_list_path is not None:
        with open(annpaths_list_path, "r") as f:
            ann_paths = f.read().split()
        return ann_paths

    # If use annotaion ids list
    ext_with_dot = "." + ext if ext != "" else ""
    with open(ann_ids_path, "r") as f:
        ann_ids = f.read().split()
    ann_paths = [os.path.join(ann_dir_path, aid + ext_with_dot) for aid in ann_ids]
    return ann_paths


def get_image_info(annotation_root, extract_num_from_imgid=True):
    path = annotation_root.findtext("path")
    if path is None:
        filename = annotation_root.findtext("filename")
    else:
        filename = os.path.basename(path)
    img_name = os.path.basename(filename)
    img_id = os.path.splitext(img_name)[0]
    if extract_num_from_imgid and isinstance(img_id, str):
        img_id = int(re.findall(r"\d+", img_id)[0])

    size = annotation_root.find("size")
    width = int(size.findtext("width"))
    height = int(size.findtext("height"))

    image_info = {"file_name": filename, "height": height, "width": width, "id": img_id}
    return image_info


def get_coco_annotation_from_obj(obj, label2id):
    label = obj.findtext("name")

    if label not in label2id:
        raise Exception(f"Error: {label} is not in label2id !")

    category_id = label2id[label]
    bndbox = obj.find("bndbox")
    xmin = int(bndbox.findtext("xmin")) - 1
    ymin = int(bndbox.findtext("ymin")) - 1
    xmax = int(bndbox.findtext("xmax"))
    ymax = int(bndbox.findtext("ymax"))

    if xmax <= xmin or ymax <= ymin:
        raise Exception(
            f"Error: Box size error !: (xmin, ymin, xmax, ymax): {xmin, ymin, xmax, ymax}"
        )

    o_width = xmax - xmin
    o_height = ymax - ymin
    ann = {
        "area": o_width * o_height,
        "iscrowd": 0,
        "bbox": [xmin, ymin, o_width, o_height],
        "category_id": category_id,
        "ignore": 0,
        "segmentation": [],  # This script is not for segmentation
    }
    return ann


def convert_xmls_to_cocojson(
    file_pascal_voc, label2id: Dict[str, int], extract_num_from_imgid: bool = True
):
    try:
        output_json_dict = {"images": [], "type": "instances", "annotations": [], "categories": []}
        bnd_id = 1

        ann_tree = ET.parse(file_pascal_voc)
        ann_root = ann_tree.getroot()

        img_info = get_image_info(
            annotation_root=ann_root, extract_num_from_imgid=extract_num_from_imgid
        )
        img_id = img_info["id"]
        output_json_dict["images"].append(img_info)

        for obj in ann_root.findall("object"):
            ann = get_coco_annotation_from_obj(obj=obj, label2id=label2id)
            ann.update({"image_id": img_id, "id": bnd_id})
            output_json_dict["annotations"].append(ann)
            bnd_id = bnd_id + 1

        return output_json_dict, None
    except Exception as e:
        print(f"Error: {e}")
        return None, rcode("ReadFileError")
