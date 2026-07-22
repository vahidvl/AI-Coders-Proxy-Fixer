from pathlib import Path
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

def convert_all_svgs():
    icons_dir = Path(__file__).parent.parent / "assets" / "icons"
    svg_files = list(icons_dir.glob("*.svg"))

    for svg_file in svg_files:
        try:
            png_filename = svg_file.stem # e.g. vscode.png
            png_path = icons_dir / png_filename
            drawing = svg2rlg(str(svg_file))
            if drawing:
                # Scale drawing to 48x48
                scaling_factor = 48.0 / max(drawing.width, drawing.height)
                drawing.width = drawing.width * scaling_factor
                drawing.height = drawing.height * scaling_factor
                drawing.scale(scaling_factor, scaling_factor)
                renderPM.drawToFile(drawing, str(png_path), fmt="PNG")
                print(f"Converted {svg_file.name} -> {png_filename}")
        except Exception as e:
            print(f"Failed converting {svg_file.name}: {e}")

if __name__ == "__main__":
    convert_all_svgs()
