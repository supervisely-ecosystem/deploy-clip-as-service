<div align="center" markdown>

<img src="https://github.com/supervisely-ecosystem/embeddings-generator/releases/download/v0.1.0/clip_poster.jpg">

# CLIP as Service

**Deploy CLIP (Contrastive Language-Image Pre-Training) model as a microservice for generating high-quality image and text embeddings**

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervisely.com/apps/supervisely-ecosystem/deploy-clip-as-service)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervisely.com/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/deploy-clip-as-service)
[![views](https://app.supervisely.com/img/badges/views/supervisely-ecosystem/deploy-clip-as-service.png)](https://supervisely.com)
[![runs](https://app.supervisely.com/img/badges/runs/supervisely-ecosystem/deploy-clip-as-service.png)](https://supervisely.com)

</div>

## Overview

🧩 This application is a part of the **AI Search** feature in Supervisely and is designed to provide a robust backend service for generating embeddings from images and text using the CLIP model.

CLIP as Service is a headless Supervisely microservice that deploys the powerful CLIP (Contrastive Language-Image Pre-Training) model as a scalable HTTP service. This service provides high-performance multimodal embeddings generation for images and text, enabling advanced computer vision and natural language processing workflows.

The service operates as a background microservice and integrates seamlessly with the Supervisely ecosystem, providing RESTful API endpoints for generating embeddings that can be used for semantic search, similarity analysis, zero-shot classification, and other multimodal AI tasks.

### Key Highlights

- **Runs Anywhere**: One image serves both devices. The service detects available hardware — an NVIDIA GPU when present, CPU otherwise — and runs the same model either way. No configuration required.
- **CLIP Model**: Utilizes the state-of-the-art CLIP model for generating high-quality multimodal embeddings.

**Prerequisites:**

- Supervisely instance with admin access
- For **GPU** inference: an NVIDIA GPU with sufficient VRAM (recommended: 4GB+) and **NVIDIA driver ≥ 550.163.01** (required by the CUDA 12.8 runtime). A GPU is **optional** — the service runs on CPU just as well, with no driver requirement.

### Compute device modes

On launch a modal lets you choose the **Compute device**:

| Mode | Device | When to use | NVIDIA driver |
| --- | --- | --- | --- |
| **Auto** (default) | GPU if available, otherwise CPU | Just works on any machine | ≥ 550.163.01 to use the GPU; otherwise falls back to CPU |
| **GPU** | CUDA | Force GPU; fastest inference | ≥ 550.163.01 required (older/missing → runs on CPU) |
| **CPU** | CPU | Machines without a GPU | none |

Both modes run **PyTorch with the same weights, the same preprocessing and the same dtype (fp32)** — only the device differs. Measured on 200 images: the two devices agree to `1e-5` per vector and return an **identical top-10 for every query**, from either side of the query. So a project indexed by a GPU session can be extended by a CPU session and vice versa — **mixed collections are safe, no re-indexing required.**

Throughput, for planning (RTX 5090 / 32-core CPU, 200 documents, best of three):

| Device | Images | Texts | Single-image latency |
| --- | --- | --- | --- |
| GPU | 399 docs/s | 496 docs/s | 13 ms |
| CPU | 52 docs/s | 71 docs/s | 50 ms |

On this hardware that is ~7x on batch throughput but only ~4x on a single request — the GPU gap narrows when requests arrive one at a time, and widens on a weaker CPU. Measure on your own machine before sizing anything on these numbers.

> **Driver requirement.** GPU acceleration uses a CUDA 12.8 runtime, which needs **NVIDIA driver ≥ 550.163.01**. In **Auto** mode an older driver or missing GPU simply triggers a transparent fallback to the CPU. The modal shows this note for the **Auto** and **GPU** modes only.

> **Coming from version ≤ 0.1.3?** Those versions ran the GPU in fp16 (there was no CPU mode). Vectors from an fp16 session differ from fp32 ones by ~`1e-5` in cosine — enough to swap neighbours that were already tied, and nothing more: in a collection half fp16 and half fp32, the top-1 hit changed for 1–2 out of 200 queries, and the similarity given up in those cases was `0.0004`. Neither half is under-retrieved. **Existing collections need no re-indexing** — and note that `embeddings-generator` will not re-index them anyway, since it only encodes images whose `updated_at` changed. If you specifically need the old fp16 GPU behaviour, run app version **0.1.3**.

### Changing the CLIP model

The model is configurable, but it is **not exposed in the modal** — it is set in the Flow configs. To change it, edit the `name` field in **both** configs so GPU and CPU stay consistent:

- [`clip.yml`](clip.yml) — GPU flow
- [`clip_cpu.yml`](clip_cpu.yml) — CPU flow

```yaml
uses:
  jtype: CLIPEncoder
  with:
    name: ViT-B-32::openai   # <- change here (and in clip_cpu.yml)
    dtype: fp32
```

Pick a model supported by clip-server (e.g. `ViT-B-32::openai`, `ViT-B-16::openai`, `ViT-L-14::openai`, `RN50::openai`, …). Two important caveats:

1. **Keep the two configs in sync.** The whole point of the current setup is that GPU and CPU produce interchangeable vectors; that holds only while `name` and `dtype` match on both sides.
2. **Changing the model changes the embedding space and dimensionality** (e.g. ViT-B/32 → 512-D, ViT-L/14 → 768-D). New embeddings are **not compatible** with previously generated vectors, so you must **re-index** existing data, and the consumer's vector collection size (in `embeddings-generator`, default 512) must be updated to match.

> Keep `dtype: fp32` on both sides. fp16 on the GPU is ~10% slower here, not faster (the model is small enough that conversion overhead eats the gain), and fp16 on the CPU is **4x slower** — PyTorch has no native fp16 CPU kernels for most ops and emulates them. It would also reintroduce a GPU/CPU gap of `8.8e-3` instead of `1e-5`.

When launching the service, the application will automatically:

1. **Load CLIP Model**: The pre-trained ViT-B/32 weights are baked into the image, so no download happens at startup (which also means the service works on air-gapped instances).
2. **Select Device**: Picks the flow based on the selected mode — GPU or CPU — with Auto detecting a GPU and falling back to CPU when none is present. The chosen device is printed in the session log as `Selected CLIP backend: ...`.

> Note: To use the service, you must change the service's visibility to "Whole Instance" in the service settings. If you forget to do this, you can always change it later in the app session settings.

Сlick "Run" to deploy the service. The application will start in headless mode and will be available as a microservice for other applications in your Supervisely instance.

---

For technical support and questions, please join our [Supervisely Ecosystem Slack community](https://supervisely.com/slack).
