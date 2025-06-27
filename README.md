<div align="center" markdown>

<img src="https://github.com/supervisely-ecosystem/embeddings-generator/releases/download/v0.1.0/clip_poster.jpg">

# CLIP as Service

**Deploy CLIP (Contrastive Language-Image Pre-Training) model as a microservice for generating high-quality image and text embeddings**

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervisely.com/apps/supervisely-ecosystem/deploy-clip-as-service)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervisely.com/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/deploy-clip-as-service)
[![views](https://app.supervisely.com/img/badges/views/supervisely-ecosystem/deploy-clip-as-service.png)](https://supervisely.com)
[![runs](https://app.supervisely.com/img/badges/runs/supervisely-ecosystem/deploy-clip-as-service.png)](https://supervisely.com)

</div>

## Overview

🧩 This application is a part of the **AI Search** feature in Supervisely and is designed to enhance the capabilities of the **Embeddings Generator** app.

CLIP as Service is a headless Supervisely microservice that deploys the powerful CLIP (Contrastive Language-Image Pre-Training) model as a scalable HTTP service. This service provides high-performance multimodal embeddings generation for images and text, enabling advanced computer vision and natural language processing workflows.

The service operates as a background microservice and integrates seamlessly with the Supervisely ecosystem, providing RESTful API endpoints for generating embeddings that can be used for semantic search, similarity analysis, zero-shot classification, and other multimodal AI tasks.

**Important**: This service is designed to run in a Supervisely instance with admin access for internal use. It is not intended for public access via API, but rather as a backend component for the **Embeddings Generator** app.

### Key Highlights

- **High Performance**: Leverages NVIDIA GPUs for fast inference and embedding generation.
- **CLIP Model**: Utilizes the state-of-the-art CLIP model for generating high-quality multimodal embeddings.

## How To Run

**Prerequisites:**

- Supervisely instance with admin access
- Docker support enabled
- NVIDIA GPU with sufficient VRAM (recommended: 8GB+)

When launching the service, the application will automatically:

1. **Download CLIP Model**: Pre-trained ViT-B/32 model weights are automatically downloaded during container initialization.
2. **Initialize GPU**: Automatically detects and utilizes available GPU resources for optimal performance.

> Note: To use the service, you must change the service's visibility to "Whole Instance" in the service settings. If you forget to do this, you can always change it later in the app session settings.

After configuration, click "Run" to deploy the service. The application will start in headless mode and will be available as a microservice for other applications in your Supervisely instance.

---

For technical support and questions, please join our [Supervisely Ecosystem Slack community](https://supervisely.com/slack).
