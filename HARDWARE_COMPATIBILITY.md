# Hardware Compatibility & Resource Optimization Report

**Target Platform**: Windows 11 Home / Pro (Build 10.0.26300)  
**Host Architecture**: x86_64 AMD64  
**Date of Assessment**: November 14, 2026  

---

## 1. Physical Hardware Specifications

| Component | Specification | Studio Assessment |
| :--- | :--- | :--- |
| **GPU** | NVIDIA GeForce RTX 5060 Laptop GPU | Active (Device 0). 8,151 MiB GDDR7/VRAM. Compute Capability 10.0 / Blackwell architecture. |
| **Driver & CUDA** | Driver Version: 621.01<br>CUDA UMD: 13.5<br>CUDA Compiler (nvcc): 13.5.37 | Fully supported. OptiX & CUDA acceleration available in Blender Cycles. |
| **CPU** | Intel Core i7-14650HX | 16 Physical Cores (8 P-Cores, 8 E-Cores), 24 Logical Processors. High single-core and multi-core throughput for CPU offloading and geometry compilation. |
| **System RAM** | 24 GB DDR5 | Ample memory for CPU offload buffers, PyTorch CPU offloading, Blender mesh operations, and concurrent OS tasks. |
| **Storage Volumes** | `C:\` Fixed: 217.26 GB total, **68.02 GB free**<br>`D:\` Fixed: 268.44 GB total, **242.74 GB free**<br>`G:\` Fixed: 536.87 GB total, **124.61 GB free** | Project workspace resides entirely on `D:\` (`D:\AI Local\Blender AI Studio`). Preserves >25 GB safety threshold easily (>240 GB available). |

---

## 2. 8GB VRAM Budget & Concurrency Strategy

With 8,151 MiB of VRAM on the RTX 5060 Laptop GPU, memory isolation and sequential task execution are critical to avoid Out-Of-Memory (OOM) crashes:

```
Total VRAM: 8,151 MiB
├── OS & Display Reserved: ~600 - 800 MiB (when no external display is on dGPU)
└── Available AI / 3D Workload Budget: ~7,200 - 7,400 MiB
```

### Concurrency Rules
1. **Never run local diffusion generation and Blender Cycles GPU rendering simultaneously.**
   - While texturing or generating meshes, Blender should operate in EEVEE or solid viewport mode.
   - When launching Cycles renders with OptiX/CUDA, generation models must either be unloaded or offloaded to CPU RAM.
2. **Quantization Baseline**:
   - Local LLMs must use 4-bit quantization (`Q4_K_M` or `Q4_0`). A 7B-9B Q4 model requires **4.5 GB - 5.8 GB VRAM**, leaving ~1.5 GB headroom.
3. **Sequential Model Swapping**:
   - The studio orchestrator features automatic model lifecycle management: loading 3D generation engines on-demand and unloading them immediately after mesh export to restore VRAM for Blender.

---

## 3. Evaluation of 3D Generation Engines (Directive Section 3.E)

| Engine | VRAM Req. | RAM Req. | Windows 11 Support | Texture Output | Quality / Speed | Studio Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TripoSR** | 4 - 6 GB | 12 GB | Excellent (PyTorch + torchmcubes) | Baked vertex colors / textured mesh | Ultra-fast (~1.5s), reliable watertight meshes for props and concept base meshes. | **A - Suitable for local RTX 5060 8GB** (Primary fast generative engine) |
| **Stable Fast 3D (SF3D)** | 6 - 7 GB | 16 GB | Good (PyTorch, trimesh, torch-sparse) | Full UV unwrap + Diffuse, Normal, Roughness maps | High-quality PBR asset in ~2 seconds. | **A / B - Suitable for local RTX 5060 8GB** (Primary high-detail textured engine) |
| **Modly** | 2 - 4 GB | 8 GB | Excellent | Procedural / Mesh | Lightweight, mechanical & structural procedural generation. | **A - Suitable for local RTX 5060 8GB** |
| **Hunyuan3D-2** | 16 - 24 GB | 32 GB | Moderate (Linux-first, heavy dependencies) | High-res textured mesh | State-of-the-art detail, but requires heavy multi-GPU or cloud instances. | **C - Requires cloud or stronger hardware** (Assigned to Cloud Adapter) |
| **TRELLIS** | 12 - 16 GB | 24 GB | Complex (requires spconv / custom CUDA kernels often failing on Windows CUDA 13.5) | Latent Radiance Field / Textured mesh | Exceptional geometry, but too heavy for local 8GB laptop without severe memory degradation. | **B / C - High overhead; assign to Cloud Adapter or optional secondary** |

---

## 4. Local Image Generation Feasibility

- **Z-Image-Turbo GGUF**: Already downloaded at `D:\AI Local\unsloth\Z-Image-Turbo-GGUF\z-image-turbo-Q4_K_M.gguf` (3.85 GB).
- **SDXL-Lightning / SD 1.5**: 4-step / 8-step checkpoints run comfortably within 4.5 GB VRAM with `xformers` or `sdpa` (scaled dot-product attention).
- **Multi-view concept generation**: Supported via optimized multi-prompt or ControlNet in ~4.8 GB VRAM.

