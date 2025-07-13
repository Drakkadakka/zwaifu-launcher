from PIL import Image, ImageDraw, ImageFont
import os

def create_launcher_icon():
    # Create a 256x256 image with a transparent background
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Main purple circular background
    circle_color = (120, 70, 200, 255)  # Nice purple
    draw.ellipse([0, 0, size, size], fill=circle_color)

    # Add a lighter purple border
    border_color = (180, 140, 255, 255)
    draw.ellipse([8, 8, size-8, size-8], outline=border_color, width=6)

    # Draw a big bold 'Z' in the center
    z_text = "Z"
    try:
        font_z = ImageFont.truetype("arialbd.ttf", 120)
    except:
        font_z = ImageFont.truetype("DejaVuSans-Bold.ttf", 120) if os.name != 'nt' else ImageFont.load_default()
    bbox_z = font_z.getbbox(z_text)
    w, h = bbox_z[2] - bbox_z[0], bbox_z[3] - bbox_z[1]
    z_x = (size - w) // 2
    z_y = 40
    draw.text((z_x, z_y), z_text, font=font_z, fill=(255,255,255,255))

    # Draw 'Launcher' below the Z
    launcher_text = "Launcher"
    try:
        font_launcher = ImageFont.truetype("arial.ttf", 38)
    except:
        font_launcher = ImageFont.truetype("DejaVuSans.ttf", 38) if os.name != 'nt' else ImageFont.load_default()
    bbox_launcher = font_launcher.getbbox(launcher_text)
    lw, lh = bbox_launcher[2] - bbox_launcher[0], bbox_launcher[3] - bbox_launcher[1]
    launcher_x = (size - lw) // 2
    launcher_y = z_y + h + 10
    draw.text((launcher_x, launcher_y), launcher_text, font=font_launcher, fill=(255,255,255,255))

    # Save the icon
    img.save('launcher_icon.png', 'PNG')
    print("Simple, bold Z Launcher icon created: launcher_icon.png")

if __name__ == "__main__":
    create_launcher_icon() 