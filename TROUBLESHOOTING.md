# Troubleshooting & Diagnostic Guide

Common issues, failure modes, diagnostic steps, and resolutions for Blender AI Studio on Windows 11 with RTX 5060 8GB.

---

## 1. Blender Connection Issues

### Symptom: `blender-launcher.exe: The file cannot be accessed by the system`
- **Cause**: Windows Store AppExecutionAlias reparse point cannot be executed inside a low-integrity sandbox child process.
- **Resolution**: Use `blender-launcher.exe` in bypass sandbox mode or run the Blender Bridge daemon outside the sandbox. Alternatively, add the path to the user's execution environment.

### Symptom: Socket connection refused on `localhost:9855`
- **Cause**: Blender is not currently open, or the Blender AI Studio addon bridge server is disabled.
- **Resolution**:
  1. Open Blender.
  2. Verify in the sidebar (`N` panel) under **Blender AI Studio > Settings** that the **Bridge Server** is toggled **Active**.
  3. If running headless operations, the orchestrator automatically invokes `blender-launcher.exe -b` as fallback.

---

## 2. Memory & VRAM Management (8GB Constraints)

### Symptom: CUDA Out of Memory (OOM) error during generation or rendering
- **Cause**: Simultaneous execution of diffusion/3D generation models and Blender Cycles GPU rendering.
- **Resolution**:
  1. Check `vram_monitor.py` or run `nvidia-smi` to identify active memory allocations.
  2. Unload the local generation model before starting a Cycles render.
  3. Ensure Blender Cycles is configured with OptiX with tile size 256x256 or adaptive sampling to cap peak memory.

---

## 3. Local Model & LM Studio Issues

### Symptom: LM Studio API returns `Connection Refused` on `http://127.0.0.1:1234`
- **Cause**: LM Studio desktop app is closed or local server mode is stopped.
- **Resolution**:
  1. Launch LM Studio (`C:\Program Files\LM Studio\LM Studio.exe`).
  2. Navigate to the **Local Server** tab (double-arrow icon) and click **Start Server**.
  3. Load either `Qwen2.5-Coder-7B-Instruct-Q4_K_M` or `Qwen3.5-9B-Q4_K_M`.
  4. Alternatively, use the studio's standalone runner script `Core/bridge/local_runner.py` to run the model directly via the bundled CUDA `llama-server.exe`.

---

## 4. Geometry and Mesh Import Issues

### Symptom: Imported GLB has inverted normals or missing surfaces
- **Cause**: Direct raw marching cubes or neural mesh extraction can create non-manifold geometry.
- **Resolution**:
  1. Run the Studio QA cleanup pipeline: `blender_mesh_operations(action="recalculate_normals")` followed by `merge_by_distance(threshold=0.0001)`.
  2. Apply the Remesh modifier or automated Voxel Remesh via the Production tab.

