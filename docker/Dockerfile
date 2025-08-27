FROM pytorch/pytorch:2.7.1-cuda12.8-cudnn9-devel

RUN apt-get update && apt-get install -y wget

RUN mkdir -p ~/.cache/clip

RUN wget -O ~/.cache/clip/ViT-B-32.pt "https://huggingface.co/jinaai/clip-models/resolve/main/ViT-B-32.pt"

COPY dev_requirements.txt dev_requirements.txt

RUN pip install --no-cache-dir -r dev_requirements.txt

ENV JINA_HIDE_SURVEY=1
ENV NO_VERSION_CHECK=1
ENV JINA_OPTOUT_TELEMETRY=1