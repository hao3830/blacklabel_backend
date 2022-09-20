import os
import random
import glob
import shutil


imgpath = "img"
labelpath = "label"

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

train_percent = 70
imglist = os.listdir(imgpath)
imgnum = len(imglist)

train_imgnum = int(imgnum * train_percent / 100)
test_imgnum = imgnum - train_imgnum

test_imglist = random.sample(imglist, test_imgnum)
train_imglist = []
for imgname in imglist:
    if imgname not in test_imglist:
        train_imglist.append(imgname)

print(len(test_imglist))
print(len(train_imglist))


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


if __name__ == "__main__":
    process(train_imglist, imgpath, labelpath, train_imgpath, train_labelpath)
    process(test_imglist, imgpath, labelpath, test_imgpath, test_labelpath)
