FROM pytorch/pytorch:2.8.0-cuda12.8-cudnn9-runtime

RUN apt-get update && apt-get install -y wget

RUN mkdir -p ~/.cache/clip

RUN wget -O ~/.cache/clip/ViT-B-32.pt "https://huggingface.co/jinaai/clip-models/resolve/main/ViT-B-32.pt"

RUN pip install --upgrade pip 

RUN pip install "pydantic<2.0"

COPY dev_requirements.txt dev_requirements.txt

RUN pip install --no-cache-dir -r dev_requirements.txt

# ONNX backend for CPU inference. We intentionally install the CPU build of
# onnxruntime (NOT onnxruntime-gpu) so it coexists with the CUDA PyTorch base
# image without CUDA-version conflicts: GPU runs via torch, CPU runs via ONNX.
# A modern onnxruntime is used because clip-server 0.8.3 pins onnxruntime<=1.13.1
# which has no wheels for the image's Python; clip-server only uses the stable
# InferenceSession/session.run API, so a newer runtime is compatible.
RUN pip install --no-cache-dir onnx "onnxruntime==1.18.1"

ENV JINA_HIDE_SURVEY=1
ENV NO_VERSION_CHECK=1
ENV JINA_OPTOUT_TELEMETRY=1