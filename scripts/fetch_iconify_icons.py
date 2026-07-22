import urllib.request
from pathlib import Path
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

def fetch_and_convert_iconify():
    icons_dir = Path(__file__).parent.parent / "assets" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)

    # Iconify official API endpoints
    iconify_map = {
        "vscode.png": "https://api.iconify.design/logos:visual-studio-code.svg",
        "gitbash.png": "https://api.iconify.design/logos:git-icon.svg",
        "powershell.png": "https://api.iconify.design/logos:powershell.svg",
        "claude_code.png": "https://api.iconify.design/logos:claude-icon.svg",
        "codex.png": "https://api.iconify.design/logos:openai-icon.svg",
        "cursor.png": "https://api.iconify.design/logos:cursor-icon.svg",
        "windsurf.png": "https://api.iconify.design/logos:codeium.svg",
        "opencode.png": "https://api.iconify.design/logos:open-access.svg",
        "qwen.png": "https://api.iconify.design/logos:alibaba-cloud.svg",
        "continue.png": "https://api.iconify.design/logos:continue-icon.svg",
        "aider.png": "https://api.iconify.design/logos:python.svg",
        "supermaven.png": "https://api.iconify.design/logos:fastapi-icon.svg",
        "cline.png": "https://api.iconify.design/logos:claude-icon.svg",
        "antigravity_ide.png": "https://api.iconify.design/logos:google-icon.svg",
        "antigravity_cli.png": "https://api.iconify.design/logos:google-cloud.svg",
    }

    headers = {'User-Agent': 'Mozilla/5.0'}

    for png_name, url in iconify_map.items():
        svg_file = icons_dir / f"{png_name}.svg"
        png_file = icons_dir / png_name
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = resp.read()
                if b"<svg" in data:
                    with open(svg_file, "wb") as f:
                        f.write(data)

                    drawing = svg2rlg(str(svg_file))
                    if drawing:
                        scaling_factor = 48.0 / max(drawing.width, drawing.height)
                        drawing.width = drawing.width * scaling_factor
                        drawing.height = drawing.height * scaling_factor
                        drawing.scale(scaling_factor, scaling_factor)
                        renderPM.drawToFile(drawing, str(png_file), fmt="PNG")
                        print(f"Successfully converted Iconify logo for {png_name}")
        except Exception as e:
            print(f"Failed {png_name}: {e}")

if __name__ == "__main__":
    fetch_and_convert_iconify()
