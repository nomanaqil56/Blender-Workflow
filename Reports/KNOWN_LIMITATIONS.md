# Known Limitations & Technical Constraints

## 1. Local AI & LM Studio Connectivity
- **Offline / Local Fallback**: When LM Studio is not active on `127.0.0.1:1234`, the agent automatically shifts to its deterministic semantic planner. Full natural-language open-domain LLM function calling requires LM Studio or `llama-server.exe` running.
- **Multimodal Vision Model VRAM Requirements**: The multimodal vision model (`Qwen3.5-9B` + `mmproj-BF16`) requires approximately 6.5 GB VRAM. When running Cycles GPU rendering with high sample counts concurrently on the 8GB RTX 5060, memory must be monitored to stay within the 6.8 GB safe operating margin.

## 2. Windows Desktop Automation & UAC
- **Windows Session Stations**: When running automation commands in secondary window stations or non-interactive service tokens, Windows `EnumWindows` and `SetForegroundWindow` calls may not enumerate windows belonging to interactive desktop session 2. In such cases, the primary persistent socket IPC bridge (`127.0.0.1:9855`) handles all communication directly, which is 100% immune to window station isolation.

## 3. Blender Store AppX Permissions
- **Executable Invocation**: Blender 5.3 installed via the Microsoft Store cannot be launched by directly invoking `C:\Program Files\WindowsApps\...\blender.exe` due to Windows AppContainer ACLs (`WinError 5 Access Denied`). Execution must always route through the Windows AppExecutionAlias `blender-launcher.exe`.

## 4. Multi-Material glTF Submesh Boundaries
- **glTF Boundary Vertices**: Exporting meshes with multiple materials to standard glTF/GLB splits vertices along material boundaries. Re-importing into Blender may report open edges unless `bmesh.ops.remove_doubles(dist=0.001)` is applied across shared boundaries.

## 5. Vision Inference Latency & Context Sizing
- **Multimodal Token Latency**: Performing multimodal base64 image projection on `Qwen3.5-9B` via LM Studio requires 30-50 seconds per frame on an 8GB laptop GPU. Client socket timeouts for vision inference should be configured to at least 90 seconds to prevent premature HTTP read timeouts.
- **Model Specialization**: `Qwen2.5-Coder-7B` is optimized for rapid tool planning, code execution, and parameter formatting (2-3 seconds per plan), whereas `Qwen3.5-9B` is utilized for visual evaluation and inspection.

## 6. Destructive Modeling vs. Modifier Stack
- **Mesh Topology Preservation**: Applying permanent in-place polygon subdivision destroys the original polygon degree (converting pentagons and hexagons into quads). For production assets requiring semantic topology audits, procedural modifier stacks (`SUBSURF`, `BEVEL`, `CAST`) and object-level metadata should be favored over permanent destructive mesh subdivision.
