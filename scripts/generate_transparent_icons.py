import os
from pathlib import Path
from PIL import Image, ImageDraw

def create_transparent_logo(filename: str, draw_func):
    out_dir = Path(__file__).parent.parent / "assets" / "icons"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Create 100% transparent image
    img = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw_func(draw)

    path = out_dir / filename
    img.save(path, "PNG")
    print(f"Generated transparent icon: {filename}")

def draw_antigravity_ide(draw):
    # Deep purple rocket shape
    draw.polygon([(48, 8), (72, 64), (48, 52), (24, 64)], fill="#8E24AA")
    draw.polygon([(48, 30), (60, 64), (48, 52), (36, 64)], fill="#BA68C8")
    draw.rectangle([44, 64, 52, 88], fill="#FF7043") # Fire trail

def draw_antigravity_cli(draw):
    # Violet lightning / CLI chevron
    draw.polygon([(56, 12), (28, 52), (52, 52), (40, 84), (68, 44), (44, 44)], fill="#7C4DFF")

def draw_claude_code(draw):
    # Warm coral asterisk/spark
    draw.polygon([(48, 12), (56, 38), (82, 38), (62, 54), (72, 80), (48, 64), (24, 80), (34, 54), (14, 38), (40, 38)], fill="#D84315")

def draw_codex(draw):
    # OpenAI green spiral
    draw.ellipse([20, 20, 76, 76], outline="#009688", width=8)
    draw.ellipse([34, 34, 62, 62], fill="#004D40")

def draw_vscode(draw):
    # VS Code Blue Ribbon Fold
    draw.polygon([(30, 18), (66, 9), (84, 25), (84, 70), (66, 87), (30, 78)], fill="#007ACC")
    draw.polygon([(30, 18), (54, 48), (30, 78), (12, 66), (12, 30)], fill="#50B4FF")
    draw.polygon([(54, 48), (84, 25), (84, 70)], fill="#005FB8")

def draw_cursor(draw):
    # Cursor Blue Diamond
    draw.polygon([(48, 12), (80, 30), (80, 66), (48, 84), (16, 66), (16, 30)], fill="#0288D1")
    draw.polygon([(48, 12), (80, 30), (48, 48), (16, 30)], fill="#29B6F6")
    draw.polygon([(48, 48), (80, 30), (80, 66), (48, 84)], fill="#01579B")

def draw_windsurf(draw):
    # Windsurf Teal Sail
    draw.polygon([(24, 84), (72, 12), (72, 84)], fill="#00ACC1")
    draw.polygon([(36, 84), (72, 36), (72, 84)], fill="#80DEEA")

def draw_opencode(draw):
    # Green Globe / Globe Grid
    draw.ellipse([16, 16, 80, 80], outline="#43A047", width=6)
    draw.ellipse([32, 16, 64, 80], outline="#43A047", width=4)
    draw.line([(48, 16), (48, 80)], fill="#43A047", width=5)
    draw.line([(16, 48), (80, 48)], fill="#43A047", width=5)

def draw_qwen(draw):
    # Qwen Amber Diamond Star
    draw.polygon([(48, 12), (84, 48), (48, 84), (16, 48)], fill="#E65100")
    draw.polygon([(48, 28), (68, 48), (48, 68), (28, 48)], fill="#FFCC80")

def draw_continue(draw):
    # Continue Magenta Fast Forward
    draw.polygon([(16, 24), (48, 48), (16, 72)], fill="#E91E63")
    draw.polygon([(48, 24), (80, 48), (48, 72)], fill="#E91E63")

def draw_aider(draw):
    # Aider Red Python Prompt
    draw.line([(20, 24), (56, 48), (20, 72)], fill="#FF1744", width=10)
    draw.line([(50, 72), (76, 72)], fill="#FF1744", width=10)

def draw_supermaven(draw):
    # Gold Lightning Flash
    draw.polygon([(56, 12), (24, 52), (48, 52), (40, 84), (72, 44), (48, 44)], fill="#FFD600")

def draw_cline(draw):
    # Cline Purple Bot Face
    draw.rounded_rectangle([16, 24, 80, 72], radius=12, fill="#7B1FA2")
    draw.ellipse([28, 40, 40, 56], fill="#FFFFFF")
    draw.ellipse([56, 40, 68, 56], fill="#FFFFFF")

def draw_powershell(draw):
    # PowerShell Blue Chevron
    draw.polygon([(20, 20), (64, 48), (20, 76), (36, 76), (80, 48), (36, 20)], fill="#0091EA")
    draw.rectangle([50, 70, 80, 78], fill="#00B0FF")

def draw_gitbash(draw):
    # Git Orange Diamond Logo
    draw.polygon([(48, 12), (84, 48), (48, 84), (12, 48)], fill="#F4511E")
    draw.ellipse([40, 40, 56, 56], fill="#FFFFFF")
    draw.ellipse([64, 64, 80, 80], fill="#FFFFFF")
    draw.line([(48, 48), (72, 72)], fill="#FFFFFF", width=4)

if __name__ == "__main__":
    create_transparent_logo("antigravity_ide.png", draw_antigravity_ide)
    create_transparent_logo("antigravity_cli.png", draw_antigravity_cli)
    create_transparent_logo("claude_code.png", draw_claude_code)
    create_transparent_logo("codex.png", draw_codex)
    create_transparent_logo("vscode.png", draw_vscode)
    create_transparent_logo("cursor.png", draw_cursor)
    create_transparent_logo("windsurf.png", draw_windsurf)
    create_transparent_logo("opencode.png", draw_opencode)
    create_transparent_logo("qwen.png", draw_qwen)
    create_transparent_logo("continue.png", draw_continue)
    create_transparent_logo("aider.png", draw_aider)
    create_transparent_logo("supermaven.png", draw_supermaven)
    create_transparent_logo("cline.png", draw_cline)
    create_transparent_logo("powershell.png", draw_powershell)
    create_transparent_logo("gitbash.png", draw_gitbash)
