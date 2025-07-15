#!/usr/bin/env python3
"""
Create a simple launcher icon for Z-Waifu Launcher
"""

import os
from PIL import Image, ImageDraw, ImageFont
import sys

def create_launcher_icon():
    """Create a simple launcher icon"""
    try:
        # Create a 64x64 image with a dark background
        img = Image.new('RGBA', (64, 64), (40, 44, 52, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple "Z" in white
        try:
            # Try to use a system font
            font = ImageFont.truetype("arial.ttf", 32)
        except:
            try:
                # Fallback to default font
                font = ImageFont.load_default()
            except:
                # Create a simple text without font
                font = None
        
        # Draw the "Z" text
        text = "Z"
        if font:
            # Calculate text position to center it
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (64 - text_width) // 2
            y = (64 - text_height) // 2
            draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        else:
            # Simple fallback - draw a white rectangle
            draw.rectangle([20, 20, 44, 44], fill=(255, 255, 255, 255))
        
        # Ensure the static/images directory exists
        icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "images")
        os.makedirs(icon_dir, exist_ok=True)
        
        # Save the icon
        icon_path = os.path.join(icon_dir, "launcher_icon.png")
        img.save(icon_path, "PNG")
        
        print(f"Launcher icon created successfully: {icon_path}")
        return True
        
    except Exception as e:
        print(f"Failed to create launcher icon: {e}")
        return False

if __name__ == "__main__":
    success = create_launcher_icon()
    sys.exit(0 if success else 1)