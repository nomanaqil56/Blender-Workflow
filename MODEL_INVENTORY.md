# Model Inventory

This document catalogs all pre-existing and active AI models discovered on the local system. In accordance with Directive Working Rule 6 ("Reuse existing installations; do not download redundant models"), existing assets are integrated directly into Blender AI Studio.

---

## 1. Discovered Local Models (`D:\AI Local\`)

| Model Name | Physical Path | Format | Size | Purpose in Blender AI Studio | VRAM Footprint |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Qwen2.5-Coder-7B-Instruct** | `D:\AI Local\lmstudio-community\Qwen2.5-Coder-7B-Instruct-GGUF\Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf` | GGUF (Q4_K_M) | 4.68 GB (4,683,074,048 B) | **Primary Local Blender Python & Shader Code Generator**: Synthesizes bpy scripts, procedural modifiers, Geometry Node graphs, and debugging routines. | ~5.1 GB (GPU Offloaded) |
| **Qwen3.5-9B** | `D:\AI Local\lmstudio-community\Qwen3.5-9B-GGUF\Qwen3.5-9B-Q4_K_M.gguf` | GGUF (Q4_K_M) | 5.63 GB (5,627,044,256 B) | **Multimodal Reference Image Analyzer & Reasoner**: Evaluates reference images, checks camera perspective, inspects render quality, and plans modeling strategy. | ~6.2 GB (GPU Offloaded) |
| **Qwen3.5-9B Vision Projector** | `D:\AI Local\lmstudio-community\Qwen3.5-9B-GGUF\mmproj-Qwen3.5-9B-BF16.gguf` | GGUF (BF16) | 921 MB (921,704,480 B) | Vision adapter enabling image input processing for Qwen3.5-9B. | ~1.0 GB |
| **DeepSeek-R1-0528-Qwen3-8B** | `D:\AI Local\lmstudio-community\DeepSeek-R1-0528-Qwen3-8B-GGUF\DeepSeek-R1-0528-Qwen3-8B-Q4_K_M.gguf` | GGUF (Q4_K_M) | 5.03 GB (5,027,782,720 B) | **Complex Scene Planner & Algorithmic Problem Solver**: Used for intricate procedural generation logic and multi-step pipeline planning. | ~5.5 GB (GPU Offloaded) |
| **Z-Image-Turbo** | `D:\AI Local\unsloth\Z-Image-Turbo-GGUF\z-image-turbo-Q4_K_M.gguf` | GGUF (Q4_K_M) | 3.85 GB (3,850,130,496 B) | **Fast Local Concept / Texture Image Synthesizer**: Generates concept views and texture references. | ~4.2 GB (GPU Offloaded) |

---

## 2. Model Routing & Execution Matrix

```mermaid
flowchart TD
    UserReq["User Prompt / Reference Images"] --> Router["Core Router & Decision Engine"]
    
    Router -->|Coding / bpy Script| M1["Qwen2.5-Coder-7B-Instruct (Local GGUF)"]
    Router -->|Visual Inspection / Multi-View| M2["Qwen3.5-9B + mmproj (Local Vision)"]
    Router -->|Complex Logic & Planning| M3["DeepSeek-R1-Qwen3-8B (Local Reasoning)"]
    Router -->|Concept Art / Texture Maps| M4["Z-Image-Turbo / SD Pipeline"]
    Router -->|3D Mesh Generation| M5["TripoSR / SF3D / Procedural BPY"]
    Router -->|Cloud Fallback (Optional)| M6["Gemini / ChatGPT Supported APIs"]
```

---

## 3. License & Attribution Registry

- **Qwen2.5-Coder-7B-Instruct**: Apache 2.0 (Commercial & personal use permitted).
- **Qwen3.5-9B**: Qwen Research / Open Source License.
- **DeepSeek-R1-Distill-Qwen-8B**: MIT License.
- **Z-Image-Turbo**: Open Source Community Weights.
- **TripoSR**: MIT License (VAST AI Research / Stability AI).
- **Stable Fast 3D**: Stability AI Community License.

