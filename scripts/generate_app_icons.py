import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def draw_app_icon(name: str, bg_color: str, text_symbol: str, accent_color: str = "#FFFFFF") -> Image.Image:
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw rounded rectangle background card
    draw.rounded_rectangle([4, 4, 124, 124], radius=28, fill=bg_color, outline="#2A2A3C", width=3)

    # Inner subtle glow ring
    draw.rounded_rectangle([12, 12, 116, 116], radius=20, fill=None, outline=accent_color, width=2)

    # Draw letter/symbol in center
    try:
        # Use default font
        draw.text((64, 64), text_symbol, fill="#FFFFFF", anchor="mm")
    except Exception:
        pass

    return img

def generate_all_icons(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    icons_data = {
        "antigravity_ide": ("#6200EA", "AG", "#B388FF"),
        "antigravity_cli": ("#7C4DFF", "AG", "#D1C4E9"),
        "claude_code": ("#D84315", "CC", "#FFAB91"),
        "codex": ("#00897B", "CX", "#80CBC4"),
        "vscode": ("#007ACC", "VS", "#90CAF9"),
        "cursor": ("#1A237E", "CU", "#8C9EFF"),
        "windsurf": ("#00ACC1", "WS", "#80DEEA"),
        "opencode": ("#2E7D32", "OC", "#A5D6A7"),
        "qwen": ("#E65100", "QW", "#FFCC80"),
        "continue": ("#C62828", "CN", "#EF9A9A"),
        "aider": ("#AD1457", "AD", "#F48FB1"),
        "supermaven": ("#F57F17", "SM", "#FFF59D"),
        "cline": ("#6A1B9A", "CL", "#E1BEE7"),
        "powershell": ("#01579B", "PS", "#81D4FA"),
        "gitbash": ("#F4511E", "GB", "#FFAB91"),
    }

    for filename, (bg, text, accent) in icons_data.items():
        icon_img = draw_app_icon(filename, bg, text, accent)
        icon_path = output_dir / f"{filename}.png"
        icon_img.save(icon_path, "PNG")
        print(f"Generated: {icon_path}")

if __name__ == "__main__":
    out = Path(__file__).parent.parent / "assets" / "icons"
    generate_all_icons(out)
