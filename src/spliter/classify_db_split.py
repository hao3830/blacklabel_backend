import os
import random
import shutil
import glob


def process(imglist, in_imgpath, out_imgpath):
    if not os.path.exists(out_imgpath):
        os.mkdir(out_imgpath)

    for fname in imglist:
        fname_woext = ".".join(fname.split(".")[:-1])
        # print(fname_woext)

        img_pattern = "%s/%s.*" % (in_imgpath, fname_woext)
        fimgpath = glob.glob(img_pattern)[0]

        #        print(fimgpath)

        new_fimgpath = os.path.join(out_imgpath, fname)
        shutil.copy(fimgpath, new_fimgpath)


def main():
    inpath = "/MLCV/thuann/lab/lab_aic2022/pill_cls/"
    outpath = "datasets"
    train_percent = 60
    val_percent = 0
    test_percent = 100 - train_percent - val_percent

    trainpath = os.path.join(outpath, "train")
    testpath = os.path.join(outpath, "test")
    valpath = os.path.join(outpath, "val")

    if not os.path.exists(outpath):
        os.mkdir(outpath)
    if not os.path.exists(trainpath):
        os.mkdir(trainpath)
    if not os.path.exists(testpath):
        os.mkdir(testpath)
    if not os.path.exists(valpath):
        os.mkdir(valpath)

    cls_list = os.listdir(inpath)
    cls_num = len(cls_list)

    cls_info = {}

    print("cls_index, cls_num, imgperclsnum, clsname, clspath")
    for cls_index, clsname in enumerate(sorted(cls_list)):
        cls_info[clsname] = {"cls_num": 0}
        clspath = os.path.join(inpath, clsname)
        imglist = os.listdir(clspath)
        imgnum = len(imglist)
        cls_info[clsname]["cls_num"] = imgnum

        print("%i/%i/%i" % (cls_index, cls_num, imgnum), clsname, clspath)

        if imgnum >= 3:
            train_imgnum = int(imgnum * train_percent / 100)
            test_imgnum = int(imgnum * test_percent / 100)
            val_imgnum = int(imgnum * val_percent / 100)

            train_imglist = imglist
            test_imglist = random.sample(train_imglist, test_imgnum)
            train_imglist = [i for i in train_imglist if i not in test_imglist]
            val_imglist = random.sample(train_imglist, val_imgnum)
            train_imglist = [i for i in train_imglist if i not in val_imglist]

            process(test_imglist, clspath, os.path.join(outpath, "test", clsname))
            process(val_imglist, clspath, os.path.join(outpath, "val", clsname))
            process(train_imglist, clspath, os.path.join(outpath, "train", clsname))
        else:
            process(imglist, clspath, os.path.join(outpath, "test", clsname))
            process(imglist, clspath, os.path.join(outpath, "val", clsname))
            process(imglist, clspath, os.path.join(outpath, "train", clsname))

    print(cls_info)


if __name__ == "__main__":
    main()
