FROM ubuntu:20.04
WORKDIR /base

RUN ln -sf /usr/share/zoneinfo/Asia/Ho_Chi_Minh /etc/localtime

RUN apt-get update && apt-get install -y python3 python3-pip cmake wget llvm python3-tk
RUN apt-get install -y libglib2.0-0 libsm6 libxext6 libxrender-dev libgl1-mesa-glx 

RUN pip3 install uvicorn==0.13.3 fastapi==0.63.0 pymysql pandas scikit-learn
RUN pip3 install python-multipart multipledispatch
RUN pip3 install opencv-python==4.2.0.32
RUN pip3 install aiofiles
RUN pip3 install openpyxl xlsxwriter

RUN pip3 install gdown
RUN pip3 install tk
RUN pip3 install pymongo
RUN pip3 install celery==5.0.5 flower==1.0.0 redis==3.5.3
RUN pip3 install requests gdown
RUN pip3 install python-magic
RUN pip3 install hurry.filesize

CMD sh start_service.sh
