import os
from pathlib import Path
from PIL import Image, ImageDraw

def draw_official_brand_icon(filename: str, bg_color: str, shape_type: str, fg_color: str = "#FFFFFF") -> Image.Image:
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background squircle
    draw.rounded_rectangle([4, 4, 124, 124], radius=28, fill=bg_color)

    # Vector Shapes matching authentic brand identities
    if shape_type == "vscode":
        # VS Code Blue Ribbon Fold
        draw.polygon([(40, 24), (88, 12), (112, 34), (112, 94), (88, 116), (40, 104)], fill="#FFFFFF")
        draw.polygon([(40, 24), (72, 64), (40, 104), (16, 88), (16, 40)], fill="#90CAF9")
        draw.polygon([(72, 64), (112, 34), (112, 94)], fill="#005FB8")
    elif shape_type == "antigravity":
        # Quantum Portal / Rocket
        draw.ellipse([28, 28, 100, 100], outline="#E040FB", width=8)
        draw.polygon([(64, 24), (88, 88), (64, 76), (40, 88)], fill="#FFFFFF")
    elif shape_type == "claude":
        # Anthropic Asterisk / Spark
        draw.polygon([(64, 20), (74, 54), (108, 64), (74, 74), (64, 108), (54, 74), (20, 64), (54, 54)], fill="#FFFFFF")
    elif shape_type == "codex":
        # OpenAI Spiral Ring
        draw.ellipse([24, 24, 104, 104], outline="#FFFFFF", width=12)
        draw.ellipse([44, 44, 84, 84], fill="#004D40", outline="#80CBC4", width=6)
    elif shape_type == "cursor":
        # Cursor Cube / Diamond
        draw.polygon([(64, 18), (108, 42), (108, 90), (64, 114), (20, 90), (20, 42)], fill="#1E88E5")
        draw.polygon([(64, 18), (108, 42), (64, 66), (20, 42)], fill="#90CAF9")
        draw.polygon([(64, 66), (108, 42), (108, 90), (64, 114)], fill="#1565C0")
    elif shape_type == "windsurf":
        # Windsurf Waves
        draw.arc([24, 24, 104, 104], start=180, end=360, fill="#FFFFFF", width=10)
        draw.arc([36, 48, 92, 96], start=0, end=180, fill="#80DEEA", width=10)
    elif shape_type == "opencode":
        # Globe/Code Bracket
        draw.ellipse([24, 24, 104, 104], outline="#FFFFFF", width=8)
        draw.line([(64, 24), (64, 104)], fill="#FFFFFF", width=6)
        draw.line([(24, 64), (104, 64)], fill="#FFFFFF", width=6)
    elif shape_type == "qwen":
        # Qwen Diamond Star
        draw.polygon([(64, 16), (112, 64), (64, 112), (16, 64)], fill="#FFFFFF")
        draw.polygon([(64, 36), (92, 64), (64, 92), (36, 64)], fill="#E65100")
    elif shape_type == "continue":
        # Double Arrow Fast Forward
        draw.polygon([(24, 32), (64, 64), (24, 96)], fill="#FFFFFF")
        draw.polygon([(64, 32), (104, 64), (64, 96)], fill="#FFFFFF")
    elif shape_type == "aider":
        # Shell Prompt >_
        draw.line([(28, 36), (68, 64), (28, 92)], fill="#FFFFFF", width=12)
        draw.line([(68, 92), (100, 92)], fill="#FFFFFF", width=12)
    elif shape_type == "supermaven":
        # Flash Lightning
        draw.polygon([(72, 16), (28, 68), (64, 68), (56, 112), (100, 60), (64, 60)], fill="#FFFFFF")
    elif shape_type == "cline":
        # Cline Purple Bot Eyes
        draw.rounded_rectangle([24, 32, 104, 96], radius=16, fill="#FFFFFF")
        draw.ellipse([40, 52, 56, 76], fill="#4A148C")
        draw.ellipse([72, 52, 88, 76], fill="#4A148C")
    elif shape_type == "powershell":
        # PowerShell Chevron >_
        draw.polygon([(28, 28), (80, 64), (28, 100), (48, 100), (96, 64), (48, 28)], fill="#FFFFFF")
        draw.rectangle([64, 90, 104, 100], fill="#81D4FA")
    elif shape_type == "gitbash":
        # Git Diamond Branch
        draw.polygon([(64, 16), (112, 64), (64, 112), (16, 64)], fill="#FFFFFF")
        draw.ellipse([40, 40, 56, 56], fill="#F4511E")
        draw.ellipse([72, 72, 88, 88], fill="#F4511E")
        draw.ellipse([40, 72, 56, 88], fill="#F4511E")
        draw.line([(48, 48), (48, 80), (80, 80)], fill="#F4511E", width=6)
    else:
        draw.ellipse([32, 32, 96, 96], fill="#FFFFFF")

    return img

def generate_all_official_icons():
    out_dir = Path(__file__).parent.parent / "assets" / "icons"
    out_dir.mkdir(parents=True, exist_ok=True)

    icon_specs = {
        "antigravity_ide.png": ("#6200EA", "antigravity"),
        "antigravity_cli.png": ("#7C4DFF", "antigravity"),
        "claude_code.png": ("#D84315", "claude"),
        "codex.png": ("#00897B", "codex"),
        "vscode.png": ("#007ACC", "vscode"),
        "cursor.png": ("#0B192C", "cursor"),
        "windsurf.png": ("#00ACC1", "windsurf"),
        "opencode.png": ("#2E7D32", "opencode"),
        "qwen.png": ("#E65100", "qwen"),
        "continue.png": ("#C62828", "continue"),
        "aider.png": ("#AD1457", "aider"),
        "supermaven.png": ("#F57F17", "supermaven"),
        "cline.png": ("#6A1B9A", "cline"),
        "powershell.png": ("#01579B", "powershell"),
        "gitbash.png": ("#F4511E", "gitbash"),
    }

    for filename, (bg, shape) in icon_specs.items():
        img = draw_official_brand_icon(filename, bg, shape)
        path = out_dir / filename
        img.save(path, "PNG")
        print(f"Created official brand icon: {path}")

if __name__ == "__main__":
    generate_all_official_icons()
