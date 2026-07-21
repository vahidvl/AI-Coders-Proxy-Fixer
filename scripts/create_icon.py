from PIL import Image, ImageDraw

def create_ico():
    size = 256
    image = Image.new('RGBA', (size, size), (18, 18, 26, 255))
    dc = ImageDraw.Draw(image)
    
    # Outer glowing border
    dc.rounded_rectangle((10, 10, size - 10, size - 10), radius=30, outline=(0, 230, 118, 255), width=6)
    
    # Shield / Lightning Icon in center
    # Lightning bolt polygon points
    points = [
        (140, 30),
        (80, 140),
        (130, 140),
        (110, 226),
        (180, 116),
        (130, 116)
    ]
    dc.polygon(points, fill=(0, 229, 255, 255))
    
    ico_path = "assets/app_icon.ico"
    image.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Saved {ico_path}")

if __name__ == "__main__":
    create_ico()
