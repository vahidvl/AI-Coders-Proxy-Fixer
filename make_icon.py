from PIL import Image, ImageDraw

def create_icon(filename, color):
    img = Image.new('RGBA', (256, 256), color=(0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    # Draw a rounded rectangle for the background
    d.rounded_rectangle([16, 16, 240, 240], radius=40, fill="#1e1e1e", outline=color, width=8)
    
    # Draw a network/proxy symbol (simple nodes)
    d.ellipse([100, 60, 156, 116], fill=color) # Top node
    d.ellipse([60, 140, 116, 196], fill=color) # Bottom left
    d.ellipse([140, 140, 196, 196], fill=color) # Bottom right
    
    # Lines
    d.line([128, 116, 88, 140], fill=color, width=12)
    d.line([128, 116, 168, 140], fill=color, width=12)
    
    img.save(filename, format='ICO', sizes=[(256, 256)])

if __name__ == "__main__":
    import os
    os.makedirs('assets', exist_ok=True)
    create_icon('assets/app_icon.ico', '#00ffcc') # Cyan aesthetic
    print("Icon generated successfully.")
