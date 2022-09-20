import os

INPATH_IMG = "image_jpg"
INPATH_LABEL = "labels_new"

_, _, files = next(os.walk(INPATH_IMG))
img_count = len(files)
_, _, files = next(os.walk(INPATH_LABEL))
label_count = len(files)

print("img_count", img_count)
print("label_count", label_count)

if img_count > label_count:
    for fname in os.listdir(INPATH_IMG):
        fname_woext = fname.split(".jpg")[0]
        lname = "%s.txt" % fname_woext
        lpath = os.path.join(INPATH_LABEL, lname)
        if not os.path.exists(lpath):
            print(fname)
else:
    for fname in os.listdir(INPATH_LABEL):
        fname_woext = fname.split(".txt")[0]
        iname = "%s.jpg" % fname_woext
        ipath = os.path.join(INPATH_IMG, iname)
        if not os.path.exists(ipath):
            print(fname, iname)
