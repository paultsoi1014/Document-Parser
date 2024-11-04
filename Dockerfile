FROM nvidia/cuda:12.2.0-devel-ubuntu22.04
RUN apt update -y && apt upgrade -y
RUN apt-get install -y software-properties-common
RUN apt update -y
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN apt update -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt update -y
RUN apt-get install python3.10 python3.10-venv python3.10-dev -y
RUN apt update -y
RUN apt install python3-pip -y
RUN python3 -m pip install --upgrade pip 
RUN apt-get update && apt-get install wget git -y

WORKDIR /app
COPY . . 

ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

RUN /root/.cargo/bin/uv pip install --system -r requirements.txt

CMD ["python3.10", "api_server.py"]