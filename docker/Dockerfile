# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# CLIP as Service
#
# ONE image that serves both devices. run.py picks the flow at startup from the
# "Compute device" modal switch:
#   * GPU -> clip.yml      (PyTorch, CUDA, fp32)
#   * CPU -> clip_cpu.yml  (PyTorch, CPU,  fp32)
# Same model, same weights, same preprocessing, same dtype on both sides - only
# the device differs, so the two modes produce interchangeable embeddings. The
# CUDA torch wheels installed here run perfectly well on a machine with no GPU
# at all (they just never load the CUDA libraries), which is why no separate
# CPU-only image is needed.
#
# Base is a plain slim Debian + CPython instead of pytorch/pytorch:*-cuda*.
# The CUDA runtime that torch needs is shipped inside the torch wheels
# themselves, so the ~8 GB vendor image only added attack surface, a conda
# distribution nobody uses and a long tail of unpatched packages.
#
# Python 3.11 is a hard ceiling, not a preference: clip-server 0.8.3 requires
# jina, which pins grpcio<=1.57.0, and grpcio 1.57.0 publishes wheels only up
# to cp311. Anything newer falls back to building grpcio from source and fails.
# ---------------------------------------------------------------------------

ARG PYTHON_BASE=python:3.11-slim-trixie

# Torch flavour. The default keeps GPU support (CUDA 12.8 wheels, driver
# >= 550.163.01) and is what the published image is built with. A CPU-only
# variant (~4 GB smaller, no NVIDIA binaries at all) can be built with
#   --build-arg TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu
# but it is not required for CPU mode - it is only a size optimisation, and the
# resulting image cannot serve GPU mode any more.
ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cu128


# --------------------------------- builder ---------------------------------
FROM ${PYTHON_BASE} AS builder

ARG TORCH_INDEX_URL

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# setuptools is bounded on both sides: >=78.1.1 clears CVE-2025-47273, and <81
# keeps pkg_resources, which setuptools 82+ dropped and jina-hubble-sdk still
# imports at module level (`from pkg_resources import Requirement`).
RUN pip install --upgrade pip wheel "setuptools>=78.1.1,<81"

# Torch first, from the flavour-specific index, so the transitive `torch`
# requirement of clip-server/open-clip is already satisfied and pip does not
# pull a second copy from PyPI.
RUN pip install torch==2.8.0 torchvision==0.23.0 --index-url ${TORCH_INDEX_URL}

COPY dev_requirements.txt /tmp/dev_requirements.txt

# All remaining runtime deps in a single resolve, so the pins below cannot be
# silently upgraded by a later install step:
#   pydantic<2   - jina 3.x is pydantic v1 only
#   protobuf<5   - jina reads FieldDescriptor.label, removed in protobuf 5. The
#                  bound is a guard against a transitive dependency pulling a
#                  newer protobuf: when that happened the jina gateway died with
#                  an AttributeError on every start, in GPU mode as well as CPU.
#                  open-clip-torch 2.8.x pins protobuf==3.20.*, which is what
#                  actually gets resolved here and is overridden below.
#   numpy<2      - docarray 0.21 predates the numpy 2 ABI
RUN pip install \
      -r /tmp/dev_requirements.txt \
      "pydantic<2" \
      "protobuf<5" \
      "numpy<2"

# Security bumps applied on top of the resolved set. Everything here is a
# straight upgrade of a package flagged by the image scanner; the two entries
# that override an upstream pin are called out individually.
#
#   protobuf 4.25.8 - overrides open-clip-torch's `protobuf==3.20.*`. Two
#     reasons: 3.20.3 has no cp311 binary wheel, so pip falls back to the
#     pure-Python implementation and every gRPC/DocumentArray serialisation
#     runs in interpreted code, and it carries two HIGH CVEs. 4.25.8 ships a
#     cp37-abi3 wheel, so Python 3.11 gets the C (upb) implementation.
#     open-clip needs protobuf only for its ONNX/training export paths, which
#     this service never touches, and jina requires just protobuf>=3.19.
#   urllib3 2.x - overrides jina's stale `urllib3<2.0.0`. Neither jina,
#     docarray, hubble nor clip-server imports urllib3 directly; the bound is
#     inherited from a 2023 requests pin.
#
# Three flagged packages are deliberately left alone, all for the same reason -
# the fix is only reachable by breaking a pin that jina 3.x actually needs:
#   starlette 0.50.0 (2 HIGH) - fixed in 1.x, but fastapi 0.125 pins
#     starlette<0.51.0 and a fastapi new enough to allow 1.x has dropped
#     pydantic v1, which jina requires.
#   protobuf 4.25.8 (1 HIGH) - fixed in 5.29.6, which jina itself tolerates,
#     but opentelemetry-proto pins protobuf<5 until otel 1.29, and that
#     upgrade drags jina's whole pinned opentelemetry-instrumentation-* set.
#   opentelemetry-instrumentation 0.40b0 (1 HIGH) - same knot: the -fastapi,
#     -asgi, -grpc and -aiohttp-client siblings all pin ==0.40b0.
# The telemetry stack is disabled in this image (JINA_OPTOUT_TELEMETRY=1), so
# the exposure is theoretical, whereas breaking jina's import graph is not.
RUN pip install \
      "pillow>=12.3.0" \
      "msgpack>=1.2.1" \
      "jaraco.context>=6.1.0" \
      "urllib3>=2.5.0" \
      "protobuf==4.25.8"

# A note for whoever opens this file wondering why the image is ~8 GB.
# site-packages/nvidia/ is ~4 GB and it is not build tooling - it IS the CUDA
# runtime. libtorch_cuda.so carries a hard DT_NEEDED on every one of cudnn,
# cublas, cusparseLt, nccl, cusolver, cusparse, cufft, curand, cufile, cupti
# and nvrtc, so removing any single one makes plain `import torch` fail, long
# before any GPU work happens. Verified one by one; do not try again.
# The remaining large items - triton (542 MB) and matplotlib+fonttools (64 MB) -
# are reachable but unused by this service. They are kept deliberately: nothing
# installs them on demand at runtime, so dropping them turns any code path that
# does reach them (torch.compile, docarray's plot/display helpers) from working
# into an ImportError.

# Bake the model weights into the image. clip-server verifies this file by md5
# and only downloads when the checksum is missing or wrong, so a correct cache
# means no network access on startup - important for air-gapped instances and it
# removes ~350 MB of traffic from every container start. One file covers both
# modes: GPU and CPU load the same torch checkpoint.
ARG CLIP_TORCH_URL=https://huggingface.co/jinaai/clip-models/resolve/main/ViT-B-32.pt

RUN set -eux; \
    mkdir -p /opt/clip-cache; \
    curl -fL --retry 5 --retry-all-errors -A 'Mozilla/5.0' \
        -o /opt/clip-cache/ViT-B-32.pt "${CLIP_TORCH_URL}"; \
    echo '3ba34e387b24dfe590eeb1ae6a8a122b  /opt/clip-cache/ViT-B-32.pt' | md5sum -c -


# --------------------------------- runtime ---------------------------------
FROM ${PYTHON_BASE} AS runtime

LABEL supervisely-sdk-version=6.74.22

# Pick up distro security fixes published after the base image was built, and
# add libgomp (the OpenMP runtime torch links against - needed for CPU mode in
# particular). No compilers, no curl, no apt lists are left behind.
RUN apt-get update \
 && apt-get upgrade -y \
 && apt-get install -y --no-install-recommends libgomp1 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# perl-base is the single largest source of unfixable CVEs in the base image
# (4 CRITICAL + 4 HIGH with no patched Debian version at build time). Nothing
# in this image links against it - no package depends on it and the service is
# pure Python - so it is dropped even though Debian marks it essential.
RUN apt-get remove -y --purge --allow-remove-essential perl-base \
 && rm -rf /var/lib/apt/lists/*

# The base image ships setuptools/wheel in the system site-packages. The
# application runs entirely out of /opt/venv, which carries its own patched
# copies, so the system ones are dead weight that only shows up in scan reports.
RUN /usr/local/bin/pip3 uninstall -y setuptools wheel

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/clip-cache /root/.cache/clip

# These two are what makes GPU mode work under the Supervisely agent, and they
# are easy to lose when moving off a CUDA base image - pytorch/pytorch:*-cuda*
# set them, python:*-slim does not.
#
# The agent starts task containers with `--runtime=nvidia` and no --gpus flag,
# so no DeviceRequests are set and the legacy nvidia-container-runtime hook
# decides what to inject purely from NVIDIA_VISIBLE_DEVICES in the container
# environment. Without it the hook injects nothing: no /dev/nvidia*, no driver
# libraries, torch.cuda.is_available() is False and Auto mode silently falls
# back to CPU on a machine that has a perfectly good GPU.
#
# Testing with `docker run --gpus all` does NOT catch this - that sets
# DeviceRequests explicitly and bypasses the variable. Verify GPU mode through
# an actual agent task, or with `--runtime=nvidia` and no --gpus.
ENV NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility

ENV PATH="/opt/venv/bin:${PATH}" \
    HOME=/root \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    JINA_HIDE_SURVEY=1 \
    NO_VERSION_CHECK=1 \
    JINA_OPTOUT_TELEMETRY=1

WORKDIR /app
