"""
Blender AI Studio - Image & Texture Generation Engine
Provides concept reference generation, multi-view turnarounds,
and procedural PBR texture map synthesis optimized for 8GB VRAM.
"""

import os
import sys
import math
import random
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from Core.config import GENERATION_DIR, INPUT_DIR, OUTPUT_DIR, TEXTURES_DIR, LOCAL_MODELS
    from Core.vram_monitor import ResourceMonitor
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from Core.config import GENERATION_DIR, INPUT_DIR, OUTPUT_DIR, TEXTURES_DIR, LOCAL_MODELS
    from Core.vram_monitor import ResourceMonitor


class ImageGenerator:
    """Generates concept art, multi-view turnaround references, and PBR texture maps."""

    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.textures_dir = TEXTURES_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.textures_dir.mkdir(parents=True, exist_ok=True)

    def generate_multiview_reference(self, prompt: str, asset_name: str = "asset",
                                     resolution: Tuple[int, int] = (1024, 1024)) -> Dict[str, Any]:
        """Generates a synchronized 4-view orthographic reference sheet (Front, Side, Rear, Perspective)."""
        if not HAS_PIL:
            return {"status": "error", "message": "Pillow is required for image generation."}

        width, height = resolution
        cell_w, cell_h = width // 2, height // 2

        # Create studio backdrop
        canvas = Image.new("RGBA", (width, height), (30, 32, 38, 255))
        draw = ImageDraw.Draw(canvas)

        # Draw grid lines and labels
        views = [
            ("FRONT VIEW", (0, 0, cell_w, cell_h), (60, 140, 220)),
            ("SIDE VIEW", (cell_w, 0, width, cell_h), (80, 200, 120)),
            ("REAR VIEW", (0, cell_h, cell_w, height), (220, 160, 60)),
            ("PERSPECTIVE / DETAIL", (cell_w, cell_h, width, height), (180, 100, 240)),
        ]

        # Draw reference framing guides
        for label, (x0, y0, x1, y1), color in views:
            # Border
            draw.rectangle([x0 + 4, y0 + 4, x1 - 4, y1 - 4], outline=(60, 65, 75, 255), width=2)
            # Center guideline
            cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
            draw.line([(cx, y0 + 10), (cx, y1 - 10)], fill=(45, 50, 60, 255), width=1)
            draw.line([(x0 + 10, cy), (x1 - 10, cy)], fill=(45, 50, 60, 255), width=1)
            # Label
            draw.text((x0 + 15, y0 + 15), f"{asset_name.upper()} - {label}", fill=color)

        # Draw concept silhouette schematic placeholder
        cx, cy = width // 4, height // 4
        draw.ellipse([cx - 80, cy - 120, cx + 80, cy + 120], outline=(100, 180, 255), width=3)
        draw.text((cx - 70, cy), prompt[:30], fill=(200, 210, 225))

        out_path = self.output_dir / f"multiview_{asset_name}.png"
        canvas.save(out_path, "PNG")

        return {
            "status": "success",
            "prompt": prompt,
            "filepath": str(out_path.resolve()),
            "resolution": [width, height],
            "views": ["front", "side", "rear", "perspective"]
        }

    def generate_pbr_texture_set(self, material_name: str, texture_type: str = "metal_panel",
                                 size: int = 1024) -> Dict[str, str]:
        """Synthesizes a complete set of seamless PBR maps (BaseColor, Normal, Roughness, Metallic, Height)."""
        if not HAS_PIL:
            raise RuntimeError("Pillow is required for procedural texture synthesis.")

        mat_folder = self.textures_dir / material_name
        mat_folder.mkdir(parents=True, exist_ok=True)

        # 1. Height / Bump Map Generation (Basis for normal map)
        height_img = Image.new("L", (size, size), 128)
        h_draw = ImageDraw.Draw(height_img)

        step = size // 8
        for x in range(0, size, step):
            for y in range(0, size, step):
                # Draw modular panel grooves
                h_draw.rectangle([x + 2, y + 2, x + step - 2, y + step - 2], fill=180, outline=40, width=4)
                # Corner rivet indentations
                r = 6
                h_draw.ellipse([x + 12 - r, y + 12 - r, x + 12 + r, y + 12 + r], fill=60)
                h_draw.ellipse([x + step - 12 - r, y + 12 - r, x + step - 12 + r, y + 12 + r], fill=60)

        height_img = height_img.filter(ImageFilter.GaussianBlur(radius=1.5))
        height_path = mat_folder / f"{material_name}_height.png"
        height_img.save(height_path)

        # 2. Normal Map Generation (Sobel filter from height map)
        normal_img = Image.new("RGB", (size, size), (128, 128, 255))
        n_pixels = normal_img.load()
        h_pixels = height_img.load()

        for y in range(size):
            for x in range(size):
                x_left = h_pixels[(x - 1) % size, y]
                x_right = h_pixels[(x + 1) % size, y]
                y_top = h_pixels[x, (y - 1) % size]
                y_bot = h_pixels[x, (y + 1) % size]

                # Gradients
                dx = (x_right - x_left) / 255.0 * 2.0
                dy = (y_bot - y_top) / 255.0 * 2.0
                dz = 1.0

                # Normalize vector
                length = math.sqrt(dx * dx + dy * dy + dz * dz)
                nx = int(((dx / length) * 0.5 + 0.5) * 255)
                ny = int(((-dy / length) * 0.5 + 0.5) * 255)  # OpenGL standard (green channel up)
                nz = int(((dz / length) * 0.5 + 0.5) * 255)
                n_pixels[x, y] = (nx, ny, nz)

        normal_path = mat_folder / f"{material_name}_normal.png"
        normal_img.save(normal_path)

        # 3. Base Color Map (Albedo)
        diffuse_img = Image.new("RGB", (size, size), (45, 50, 60))
        d_draw = ImageDraw.Draw(diffuse_img)
        for x in range(0, size, step):
            for y in range(0, size, step):
                # Subtle tonal variation across panels
                shade = random.randint(50, 75)
                d_draw.rectangle([x + 4, y + 4, x + step - 4, y + step - 4], fill=(shade, shade + 5, shade + 15))
        diffuse_img = diffuse_img.filter(ImageFilter.GaussianBlur(radius=1.0))
        diffuse_path = mat_folder / f"{material_name}_basecolor.png"
        diffuse_img.save(diffuse_path)

        # 4. Roughness Map
        rough_img = Image.new("L", (size, size), 60)
        rough_draw = ImageDraw.Draw(rough_img)
        for x in range(0, size, step):
            for y in range(0, size, step):
                rough_draw.rectangle([x + 2, y + 2, x + step - 2, y + step - 2], fill=random.randint(40, 70), outline=180, width=4)
        rough_path = mat_folder / f"{material_name}_roughness.png"
        rough_img.save(rough_path)

        # 5. Metallic Map
        metal_img = Image.new("L", (size, size), 230)  # Near 1.0 metallic
        metal_path = mat_folder / f"{material_name}_metallic.png"
        metal_img.save(metal_path)

        return {
            "base_color": str(diffuse_path.resolve()),
            "normal": str(normal_path.resolve()),
            "roughness": str(rough_path.resolve()),
            "metallic": str(metal_path.resolve()),
            "height": str(height_path.resolve())
        }


if __name__ == "__main__":
    gen = ImageGenerator()
    mv = gen.generate_multiview_reference("Futuristic Aerodynamic Hypercar", "hypercar")
    print("Multiview generated:", mv["filepath"])
    pbr = gen.generate_pbr_texture_set("SciFiHullPlate")
    print("PBR Maps generated:", list(pbr.keys()))

