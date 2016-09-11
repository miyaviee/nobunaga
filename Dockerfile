FROM ubuntu

RUN sed -i.bak -e "s%http://archive.ubuntu.com/ubuntu/%http://ftp.iij.ad.jp/pub/linux/ubuntu/archive/%g" /etc/apt/sources.list
RUN apt-get update \
&& apt-get -y upgrade \
&& apt-get clean

RUN apt-get -y install \
python3 \
python3-pip \
&& apt-get clean

RUN pip3 install --upgrade pip

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

CMD ["python3", "app.py"]
