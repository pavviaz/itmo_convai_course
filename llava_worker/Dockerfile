FROM nvidia/cuda:11.7.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=on

RUN apt update && \
    apt -y upgrade && \
    apt install -y --no-install-recommends \
        software-properties-common \
        build-essential \
        python3-pip \
        python3-tk \
        python3-dev \
        git \
        bash \
        libsm6 \
        libgl1 \
        libxrender1 \
        libxext6 \
        wget \
        curl \
        zip \
        unzip \
        libtcmalloc-minimal4 \
        ca-certificates && \
    update-ca-certificates && \
    apt clean && \
    rm -rf /var/lib/apt/lists/* && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen

ARG LLAVA_URL
RUN wget ${LLAVA_URL} && unzip "main.zip" && rm "main.zip"
WORKDIR /LLaVA-main

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -e .
RUN python3 -m pip install gdown protobuf

# ARG MODEL_NAME
# RUN python3 -c 'from transformers import AutoTokenizer; \
#                 from llava.model import *; \
#                 import os; \
#                 AutoTokenizer.from_pretrained(os.environ["MODEL_NAME"]); \
#                 LlavaLlamaForCausalLM.from_pretrained(os.environ["MODEL_NAME"])'

COPY launcher.py .
