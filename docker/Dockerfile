FROM nvidia/cuda:10.2-cudnn7-devel-centos8
MAINTAINER author "https://github.com/m986883511"

RUN yum install -y python36 libglvnd-glx
RUN python3 -m pip install --upgrade pip
ADD backend.tar /subtittle
ADD pretrained_models.tar /subtittle

COPY requirements.txt /subtittle
RUN pip3 install -r /subtittle/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
ADD flask /subtittle
ADD ffmpeg.tar /usr/bin
EXPOSE 6666

RUN pip3 install spleeter==2.2.2 -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip3 install librosa==0.6.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip3 install numba==0.48.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
WORKDIR /subtittle
CMD ["python3", "app.py"]
