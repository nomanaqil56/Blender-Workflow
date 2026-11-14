# Blender AI Studio: Autonomous 3D AI Agent

> **Complete Architecture Replacement**: An autonomous AI agent that interacts directly with the live desktop Blender GUI via persistent IPC, non-blocking main-thread task execution, structured tool calling, and computer-vision feedback.

---

## 1. What is Blender AI Studio?
Unlike traditional procedural generators or monolithic prompt-to-script wrappers, **Blender AI Studio** acts like a real 3D artist seated in front of Blender:
- **Operates on the Live Desktop GUI**: Commands execute directly inside your visible Blender window in real time.
- **Strict Main-Thread Safety**: Uses `bpy.app.timers` to safely dispatch Blender Python API (`bpy`) operations on Blender's main loop without crashing socket threads.
- **Multi-Step Tool Planning**: Decomposes natural language requests into structured, schema-validated tool calls.
- **Context & Object Memory**: Understands follow-up instructions (*"make the seams deeper and darken the leather"*) and modifies existing objects instead of creating duplicates.
- **Visual Intelligence Loop**: Captures viewport frames, computes luminance and contrast analytics, detects defects, and plans corrective actions.

---

## 2. Hardware & Software Requirements
- **Operating System**: Windows 11 (64-bit)
- **GPU**: NVIDIA RTX 5060 Laptop GPU (8GB VRAM) / Any modern CUDA GPU
- **CPU**: Intel Core i7-14650HX or equivalent
- **RAM**: 24GB DDR5
- **Software**:
  - Blender 5.3 (or 4.2+)
  - Python 3.11+
  - LM Studio / OpenAI-compatible endpoint (`http://127.0.0.1:1234/v1`) with local Qwen models

---

## 3. Quick Start

### Installation
```bash
git clone https://github.com/nomanaqil56/Blender-Workflow.git
cd "Blender AI Studio"
pip install -r requirements.txt
```

### Enable the Blender Addon
Copy or install `blender/addon` into Blender's addon directory:
```powershell
Copy-Item -Path "blender\addon\*" -Destination "$env:APPDATA\Blender Foundation\Blender\5.3\scripts\addons\blender_ai_studio" -Recurse -Force
```
In Blender:
1. Open **Edit > Preferences > Add-ons**.
2. Search for **Blender AI Studio** and enable it.
3. The addon will automatically start the background bridge on `127.0.0.1:9855`.
4. Open the 3D Viewport sidebar (`N`-panel) and click the **AI Studio** tab.

### Running Blender AI Studio

#### System Status Banner:
```bash
python -m app.main --status
```

#### Inspect Active Scene:
```bash
python -m app.main --inspect
```

#### Autonomous Instruction:
```bash
python -m app.main --prompt "Create a realistic professional football with accurate proportions, distinct pentagonal and hexagonal panels, realistic leather materials, visible seams, and studio lighting."
```

#### Interactive Console Loop:
```bash
python -m app.main
```

---

## 4. Supported Tool Categories
1. **Scene**: `inspect_scene`, `inspect_object`
2. **Object**: `create_object`, `delete_object` (with confirm guard), `select_object`, `transform_object`, `duplicate_object`
3. **Mesh Operations**: `create_mesh`, `create_truncated_icosahedron`, `edit_mesh`, `extrude`, `inset`, `bevel`, `subdivide`
4. **Modifiers**: `add_modifier`, `configure_modifier`, `apply_modifier`
5. **Materials**: `create_material` (PBR Principled BSDF), `assign_material`
6. **Cameras & Lighting**: `setup_camera`, `setup_light`
7. **Rendering & IO**: `render_preview`, `capture_viewport`, `save_project`, `export_asset` (GLB, OBJ, FBX)

---

## 5. Verification & Testing
Run the complete 27-test master test suite against the live Blender GUI session:
```bash
python tests/run_master_suite.py
```
Test results and empirical evidence:
- [TEST_REPORT.md](file:///d:/AI%20Local/Blender%20AI%20Studio/reports/TEST_REPORT.md)
- [DEVICE_TEST_REPORT.md](file:///d:/AI%20Local/Blender%20AI%20Studio/reports/DEVICE_TEST_REPORT.md)
- [ARCHITECTURE.md](file:///d:/AI%20Local/Blender%20AI%20Studio/reports/ARCHITECTURE.md)
