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

- **Runs Anywhere**: Automatically detects available hardware — uses an NVIDIA GPU (PyTorch backend) for fast inference when present, and transparently falls back to a CPU-optimized ONNX backend otherwise. No configuration required.
- **CLIP Model**: Utilizes the state-of-the-art CLIP model for generating high-quality multimodal embeddings.

**Prerequisites:**

- Supervisely instance with admin access
- For **GPU** inference: an NVIDIA GPU with sufficient VRAM (recommended: 4GB+) and **NVIDIA driver ≥ 550.163.01** (required by the CUDA 12.8 runtime). A GPU is **optional** — the service also runs on CPU via the ONNX backend, which has no driver requirement.

### Compute device modes

On launch a modal lets you choose the **Compute device**:

| Mode | Backend | When to use | NVIDIA driver |
| --- | --- | --- | --- |
| **Auto** (default) | PyTorch on GPU if available, otherwise ONNX on CPU | Just works on any machine | ≥ 550.163.01 to use the GPU; otherwise falls back to CPU |
| **GPU** | PyTorch (CUDA) | Force GPU; fastest inference | ≥ 550.163.01 required (older/missing → runs on CPU) |
| **CPU** | ONNX Runtime | Machines without a GPU; fast on CPU | none |

> **Driver requirement.** GPU acceleration uses a CUDA 12.8 runtime, which needs **NVIDIA driver ≥ 550.163.01**. In **Auto** mode an older driver or missing GPU simply triggers a transparent fallback to the CPU (ONNX) backend. The modal shows this note for the **Auto** and **GPU** modes only.

> **Embeddings are interchangeable across all modes.** Every mode runs the exact same model (ViT-B/32, fp32, 512-D) with identical preprocessing — only the inference engine (PyTorch vs ONNX Runtime) differs, which changes the output only at the level of floating-point noise. Because search uses cosine similarity, this has no practical effect on results. You can therefore run different sessions in different modes and **mix their embeddings in the same index/collection — no re-indexing required.**

### Changing the CLIP model

The model is configurable, but it is **not exposed in the modal** — it is set in the Flow configs. To change it, edit the `name` field in **both** backend configs so GPU and CPU stay consistent:

- [`clip.yml`](clip.yml) — PyTorch (GPU) backend
- [`clip_onnx.yml`](clip_onnx.yml) — ONNX (CPU) backend

```yaml
uses:
  jtype: CLIPEncoder
  with:
    name: ViT-B-32::openai   # <- change here (and in clip_onnx.yml)
```

Pick a model supported by clip-server (e.g. `ViT-B-32::openai`, `ViT-B-16::openai`, `ViT-L-14::openai`, `RN50::openai`, …). Two important caveats:

1. **The model must exist for both backends.** The ONNX backend supports a subset of models — choose one available in both PyTorch and ONNX, otherwise CPU/GPU sessions will not match.
2. **Changing the model changes the embedding space and dimensionality** (e.g. ViT-B/32 → 512-D, ViT-L/14 → 768-D). New embeddings are **not compatible** with previously generated vectors, so you must **re-index** existing data, and the consumer's vector collection size (in `embeddings-generator`, default 512) must be updated to match.

> Keep `dtype` at the default (**fp32**) on both backends. Switching to fp16/int8 would break cross-backend embedding compatibility.

When launching the service, the application will automatically:

1. **Download CLIP Model**: Pre-trained ViT-B/32 model weights are automatically downloaded during container initialization.
2. **Select Device**: Picks the backend based on the selected mode — GPU (PyTorch) or CPU (ONNX) — with Auto detecting a GPU and falling back to CPU when none is present.

> Note: To use the service, you must change the service's visibility to "Whole Instance" in the service settings. If you forget to do this, you can always change it later in the app session settings.

Сlick "Run" to deploy the service. The application will start in headless mode and will be available as a microservice for other applications in your Supervisely instance.

---

For technical support and questions, please join our [Supervisely Ecosystem Slack community](https://supervisely.com/slack).
