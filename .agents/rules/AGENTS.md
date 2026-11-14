# Blender AI Studio Guidelines

You are operating within the **Blender AI Studio** environment.

## 1. Principles
- For hard-surface, mechanical, and architectural models, prioritize procedural modeling, precise modifier stacks, and Geometry Nodes over noisy neural meshes.
- For organic creatures, characters, and concept sculptures, combine generative base meshes with automated remeshing, normal smoothing, and UV unwrap.
- Always verify manifold geometry before final export.

## 2. Active Integrations
- Blender 5.3 is accessible via `blender_*` MCP tools and the `BlenderBridge`.
- Live socket communicates over `localhost:9855`. Headless execution fallback operates via `blender-launcher.exe -b`.
- Local AI models: `Qwen2.5-Coder-7B` (Blender scripts), `Qwen3.5-9B` (Visual inspection), `DeepSeek-R1-Qwen3-8B` (Complex planning).
- Always ensure VRAM safety margins (under 8GB) before launching heavy render passes.

