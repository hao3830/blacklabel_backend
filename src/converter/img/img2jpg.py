import os
from multiprocessing import Process, Pool

import cv2
from tqdm import tqdm


def convert(fname_list):
    for fname in fname_list:
        fpath = os.path.join(INPATH, fname)
        fname_woext = ".".join(fname.split(".")[:-1])
        nfpath = os.path.join(OUTPATH, "%s%s" % (fname_woext, EXT))
        img = cv2.imread(fpath)
        cv2.imwrite(nfpath, img)


if __name__ == "__main__":
    INPATH = "images"
    OUTPATH = "image_jpg"
    EXT = ".jpg"

    if not os.path.exists(OUTPATH):
        os.mkdir(OUTPATH)

    _, _, files = next(os.walk(INPATH))
    img_count = len(files)
    print("img_count", img_count)

    fname_list = os.listdir(INPATH)

    th_num = 100
    fnum = int(img_count / th_num)
    fname_list_split_list = []
    for i in range(th_num):
        fname_list_split_list.append(fname_list[i * fnum : (i + 1) * fnum])

    if img_count % th_num > 0:
        fname_list_split_list.append(fname_list[th_num * fnum :])

    with Pool(processes=th_num) as p:
        with tqdm(total=th_num) as pbar:
            for _ in p.imap_unordered(convert, fname_list_split_list):
                pbar.update()
