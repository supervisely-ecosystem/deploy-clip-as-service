FROM supervisely/base-py-sdk:6.73.350

RUN apt-get update && apt-get install -y wget

RUN mkdir -p ~/.cache/clip

RUN wget -O ~/.cache/clip/ViT-B-32.pt "https://huggingface.co/jinaai/clip-models/resolve/main/ViT-B-32.pt"

COPY dev_requirements.txt dev_requirements.txt

RUN pip install --no-cache-dir -r dev_requirements.txt

ENV JINA_HIDE_SURVEY=1
ENV NO_VERSION_CHECK=1
ENV JINA_OPTOUT_TELEMETRY=1