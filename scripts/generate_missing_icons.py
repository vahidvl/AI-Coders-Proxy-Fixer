from pathlib import Path
from PIL import Image, ImageDraw

def create_crisp_icon(filename: str, bg_color: str, draw_func):
    out_dir = Path(__file__).parent.parent / "assets" / "icons"
    out_dir.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([4, 4, 124, 124], radius=28, fill=bg_color)
    draw_func(draw)
    path = out_dir / filename
    img.save(path, "PNG")
    print(f"Rendered missing icon: {filename}")

def draw_vscode(draw):
    draw.polygon([(40, 24), (88, 12), (112, 34), (112, 94), (88, 116), (40, 104)], fill="#FFFFFF")
    draw.polygon([(40, 24), (72, 64), (40, 104), (16, 88), (16, 40)], fill="#90CAF9")
    draw.polygon([(72, 64), (112, 34), (112, 94)], fill="#005FB8")

def draw_powershell(draw):
    draw.polygon([(28, 28), (80, 64), (28, 100), (48, 100), (96, 64), (48, 28)], fill="#FFFFFF")
    draw.rectangle([64, 90, 104, 100], fill="#81D4FA")

def draw_cursor(draw):
    draw.polygon([(64, 18), (108, 42), (108, 90), (64, 114), (20, 90), (20, 42)], fill="#1E88E5")
    draw.polygon([(64, 18), (108, 42), (64, 66), (20, 42)], fill="#90CAF9")
    draw.polygon([(64, 66), (108, 42), (108, 90), (64, 114)], fill="#1565C0")

def draw_continue(draw):
    draw.polygon([(24, 32), (64, 64), (24, 96)], fill="#FFFFFF")
    draw.polygon([(64, 32), (104, 64), (64, 96)], fill="#FFFFFF")

def draw_aider(draw):
    draw.line([(28, 36), (68, 64), (28, 92)], fill="#FFFFFF", width=12)
    draw.line([(68, 92), (100, 92)], fill="#FFFFFF", width=12)

if __name__ == "__main__":
    create_crisp_icon("vscode.png", "#007ACC", draw_vscode)
    create_crisp_icon("powershell.png", "#01579B", draw_powershell)
    create_crisp_icon("cursor.png", "#0B192C", draw_cursor)
    create_crisp_icon("continue.png", "#C62828", draw_continue)
    create_crisp_icon("aider.png", "#AD1457", draw_aider)
