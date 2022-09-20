import os
import random
import glob
import shutil


def process(imglist, in_imgpath, in_labelpath, out_imgpath, out_labelpath):
    for fname in imglist:
        fname_woext = ".".join(fname.split(".")[:-1])
        print(fname_woext)

        img_pattern = "%s/%s.*" % (in_imgpath, fname_woext)
        fimgpath = glob.glob(img_pattern)[0]

        label_pattern = "%s/%s.*" % (in_labelpath, fname_woext)
        flabelpath = glob.glob(label_pattern)[0]
        flabelname = flabelpath.split("/")[-1]

        print(fimgpath, flabelpath)

        new_fimgpath = os.path.join(out_imgpath, fname)
        new_flabelpath = os.path.join(out_labelpath, flabelname)
        shutil.copy(fimgpath, new_fimgpath)
        shutil.copy(flabelpath, new_flabelpath)


def create_split_list(imgpath, train_percent, test_percent, val_percent):
    imglist = os.listdir(imgpath)
    imgnum = len(imglist)

    train_imgnum = int(imgnum * train_percent / 100)
    test_imgnum = int(imgnum * test_percent / 100)
    val_imgnum = int(imgnum * val_percent / 100)

    test_imglist = random.sample(imglist, test_imgnum)
    val_imglist = random.sample(imglist, val_imgnum)
    train_imglist = []
    for imgname in imglist:
        if imgname not in test_imglist:
            train_imglist.append(imgname)

    return train_imglist, val_imglist, test_imglist


def split(imgpath, labelpath, train_percent, test_percent, val_percent):
    if train_percent + test_percent + val_percent != 100:
        assert "percent sum not == 100"

    train_imgpath = "train_img"
    train_labelpath = "train_label"
    if not os.path.exists(train_imgpath):
        os.mkdir(train_imgpath)
    if not os.path.exists(train_labelpath):
        os.mkdir(train_labelpath)

    test_imgpath = "test_img"
    test_labelpath = "test_label"
    if not os.path.exists(test_imgpath):
        os.mkdir(test_imgpath)
    if not os.path.exists(test_labelpath):
        os.mkdir(test_labelpath)

    val_imgpath = "val_img"
    val_labelpath = "val_label"
    if not os.path.exists(val_imgpath):
        os.mkdir(val_imgpath)
    if not os.path.exists(val_labelpath):
        os.mkdir(val_labelpath)

    train_imglist, val_imglist, test_imglist = create_split_list(imgpath, train_percent, test_percent, val_percent)

    print("train_imglist num: ", len(train_imglist))
    print("test_imglist num: ", len(test_imglist))
    print("val_imglist num: ", len(val_imglist))

    process(train_imglist, imgpath, labelpath, train_imgpath, train_labelpath)
    process(test_imglist, imgpath, labelpath, test_imgpath, test_labelpath)
    process(val_imglist, imgpath, labelpath, val_imgpath, val_labelpath)


if __name__ == "__main__":
    imgpath = "images"
    labelpath = "labels"
    train_percent = 60
    test_percent = 20
    val_percent = 20
    split(imgpath, labelpath, train_percent, test_percent, val_percent)
